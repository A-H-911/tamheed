/* Run tests/standup_browser_check.js against one standup page (plan 251 v2, U4).

     node tests/run_standup_browser_check.mjs <path to the page.html> [path to chrome] [shots dir]

   It starts a headless Chrome with a fresh, temporary profile, opens the page from its file,
   evaluates the check file through the DevTools protocol, then checks two things the page
   cannot check on itself: no sideways scroll at a 375 px phone width, and print hides the
   controls. With a shots dir it saves screenshots (light and dark, 1280 and 375 px). It exits 1
   when a check fails, and 2 when it cannot run (no Chrome is a failure, never a skip). It needs
   Node 22 or later and a Chrome or Chromium. CI runs it in the job `standup-browser`. */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const page = process.argv[2];
if (!page || !existsSync(page)) {
  console.error('usage: node tests/run_standup_browser_check.mjs <page.html> [chrome] [shots dir]');
  process.exit(2);
}
const candidates = [process.argv[3], process.env.CHROME,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
const chrome = candidates.find((path) => path && existsSync(path));
if (!chrome) { console.error('no Chrome found. Pass its path as the second argument.'); process.exit(2); }
const shots = process.argv[4];

const source = readFileSync(join(here, 'standup_browser_check.js'), 'utf8');
const check = source.slice(source.indexOf('async () =>'));
const profile = mkdtempSync(join(tmpdir(), 'standup-check-'));
const port = 9300 + Math.floor(Math.random() * 600);
const browser = spawn(chrome, ['--headless=new', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--window-size=1280,900',
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
async function shot(name) {
  if (!shots) return;
  mkdirSync(shots, { recursive: true });
  const image = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  writeFileSync(join(shots, name + '.png'), Buffer.from(image.data, 'base64'));
}

let code = 1;
try {
  socket = new WebSocket(await target());
  await new Promise((done, fail) => { socket.onopen = done; socket.onerror = fail; });
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (waiting.has(message.id)) { waiting.get(message.id)(message.result || {}); waiting.delete(message.id); }
  };
  // Wait until the page is whole and its own script has run: a fixed pause was too short on
  // CI for a page of 100 KB (the phase list was still empty).
  let ready = false;
  for (let n = 0; n < 150 && !ready; n += 1) {
    ready = await evaluate("document.readyState === 'complete' && document.documentElement.dataset.js === 'on'");
    if (!ready) await sleep(200);
  }
  if (!ready) throw new Error('the page did not finish loading, or its script did not run');
  const value = await evaluate(`(${check})()`);
  const lines = value.lines;

  for (const theme of ['light', 'dark']) {
    await evaluate(`document.getElementById('theme-${theme}').click()`);
    await shot(`standup-${theme}-1280`);
  }
  await send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 1, mobile: true });
  await sleep(200);
  const wide = await evaluate('document.documentElement.scrollWidth - window.innerWidth');
  lines.push((wide <= 0 ? 'pass ' : 'FAIL ') + 'no sideways scroll at 375 px' + (wide > 0 ? ` (${wide} px too wide)` : ''));
  for (const theme of ['light', 'dark']) {
    await evaluate(`document.getElementById('theme-${theme}').click()`);
    await shot(`standup-${theme}-375`);
  }
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  const hidden = await evaluate("['#tree-controls', '.theme'].every((s) => getComputedStyle(document.querySelector(s)).display === 'none')");
  lines.push((hidden ? 'pass ' : 'FAIL ') + 'print hides the controls and the colour switch');
  await evaluate("document.getElementById('theme-auto').click()");

  lines.forEach((line) => console.log(line));
  const failed = lines.filter((line) => line.startsWith('FAIL')).length;
  console.log(`${lines.length - failed} passed, ${failed} failed`);
  code = failed === 0 ? 0 : 1;
  socket.close();
} catch (error) {
  console.error('the check did not run: ' + error.message);
  code = 2;
} finally {
  browser.kill();
  await sleep(300);
  try { rmSync(profile, { recursive: true, force: true }); } catch (error) { /* temporary */ }
}
process.exit(code);
