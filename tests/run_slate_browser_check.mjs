/* Run tests/slate_browser_check.js against one exported interview page (plan 227c, R114;
   plan 257, R154).

     node tests/run_slate_browser_check.mjs <path to the page.html> [path to chrome]

   It starts a headless Chrome with a fresh, temporary profile, opens the page from its file,
   and waits until the page is whole and its own script has run. It then evaluates the check
   file as it stands through the DevTools protocol at 1440 x 900, and prints each line. A check
   that a part of the page gates prints SKIP and fails nothing (plan 244). The page needs at
   least one ready round with a question of the room: a page without one is refused, untouched.
   Then, at 390 x 844 (plan 257, Jisr's FB-034), it shows every question and checks that no
   element of the reading column passes the edge of its card, and that the page has no
   sideways scroll. It exits 1 when a check fails. It needs Node 22 or later (for the built-in
   WebSocket) and a Chrome or Chromium. It loads no package. CI runs it in the job
   `slate-browser`, on the pages that tests/slate_browser_page.py builds. */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const page = process.argv[2];
if (!page || !existsSync(page)) {
  console.error('usage: node tests/run_slate_browser_check.mjs <page.html> [chrome]');
  process.exit(2);
}
const candidates = [process.argv[3], process.env.CHROME,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
const chrome = candidates.find((path) => path && existsSync(path));
if (!chrome) { console.error('no Chrome found. Pass its path as the second argument.'); process.exit(2); }

const source = readFileSync(join(here, 'slate_browser_check.js'), 'utf8');
const check = source.slice(source.indexOf('async () =>'));
const profile = mkdtempSync(join(tmpdir(), 'slate-check-'));
const port = 9300 + Math.floor(Math.random() * 600);
const browser = spawn(chrome, ['--headless=new', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--window-size=1440,900',
  pathToFileURL(resolve(page)).href], { stdio: 'ignore' });

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
async function target() {
  for (let n = 0; n < 150; n += 1) {      // up to 30 s: a CI machine starts Chrome slowly
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const found = list.find((item) => item.type === 'page' && item.url.startsWith('file:'));
      if (found) { return found.webSocketDebuggerUrl; }
    } catch (error) { /* the browser is still starting */ }
    await sleep(200);
  }
  throw new Error('the browser did not open the page');
}

let socket;
let next = 0;
const waiting = new Map();
function send(method, params = {}) {
  next += 1;
  const id = next;
  socket.send(JSON.stringify({ id, method, params }));
  return new Promise((done) => waiting.set(id, done));
}
async function evaluate(expression) {
  const answer = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (answer.exceptionDetails) { throw new Error(JSON.stringify(answer.exceptionDetails).slice(0, 400)); }
  return answer.result.value;
}

/* No card of the reading column may hold content wider than itself, and no card may reach past
   the column. A card's scrollWidth counts text that runs past the box of its element, which
   the boxes alone do not show: an unwrapped word overflows its paragraph while the paragraph's
   box stays inside the card. A card that grows to fit its content instead (a fieldset sizes to
   its content) is caught by its edge against the column's. The presenter view and the
   recommendations are switched on first, so the operator's questions and every reason are laid
   out: a hidden card has no box and is passed over. */
const OVERFLOW = `(() => {
  ['presenter', 'recs'].forEach((id) => {
    const button = document.getElementById(id);
    if (button.getAttribute('aria-pressed') !== 'true') { button.click(); }
  });
  document.getElementById('view-all').click();
  const column = document.querySelector('.column').getBoundingClientRect();
  const bad = [];
  let cards = 0;
  document.querySelectorAll('.column .step, .column .pagehead').forEach((card) => {
    if (!card.clientWidth) { return; }
    cards += 1;
    const box = card.getBoundingClientRect();
    const past = Math.max(card.scrollWidth - card.clientWidth,
                          Math.round(box.right - column.right), Math.round(column.left - box.left));
    if (past > 1) { bad.push((card.getAttribute('data-q') || card.className) + ' +' + past + ' px'); }
  });
  return { bad: bad.slice(0, 5), count: bad.length, cards, width: window.innerWidth,
           wide: document.documentElement.scrollWidth - window.innerWidth };
})()`;

let code = 1;
try {
  socket = new WebSocket(await target());
  await new Promise((done, fail) => { socket.onopen = done; socket.onerror = fail; });
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (waiting.has(message.id)) { waiting.get(message.id)(message.result || {}); waiting.delete(message.id); }
  };
  // Wait until the page is whole and its own script has run (the standup runner's lesson: a
  // fixed pause was too short on CI)
  let ready = false;
  for (let n = 0; n < 150 && !ready; n += 1) {
    ready = await evaluate("document.readyState === 'complete' && document.documentElement.classList.contains('ready')");
    if (!ready) await sleep(200);
  }
  if (!ready) throw new Error('the page did not finish loading, or its script did not run');
  const value = await evaluate(`(${check})()`);
  const lines = value.lines;

  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await sleep(200);
  const phone = await evaluate(OVERFLOW);
  // a check that measured nothing proves nothing: the width and the count are part of it
  const measured = phone.width === 390 && phone.cards > 0;
  lines.push((measured && phone.count === 0 ? 'pass ' : 'FAIL ')
    + `no card holds content wider than itself at 390 px (${phone.cards} cards at ${phone.width} px)`
    + (phone.count ? ` (${phone.count}: ${phone.bad.join(', ')})` : ''));
  lines.push((phone.wide <= 0 ? 'pass ' : 'FAIL ') + 'no sideways scroll at 390 px'
    + (phone.wide > 0 ? ` (${phone.wide} px too wide)` : ''));
  await send('Emulation.clearDeviceMetricsOverride');

  lines.forEach((line) => console.log(line));
  const failed = lines.filter((line) => line.startsWith('FAIL')).length;
  const skipped = lines.filter((line) => line.startsWith('SKIP')).length;
  console.log(`${lines.length - failed - skipped} passed, ${skipped} skipped, ${failed} failed`);
  code = failed === 0 ? 0 : 1;
  socket.close();
} catch (error) {
  console.error('the check did not run: ' + error.message);
} finally {
  browser.kill();
  await sleep(300);
  try { rmSync(profile, { recursive: true, force: true }); } catch (error) { /* the profile is temporary */ }
}
process.exit(code);
