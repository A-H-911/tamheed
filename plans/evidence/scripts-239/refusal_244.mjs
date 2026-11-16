/* Plan 244 (FB-018, R126): proof that the browser check leaves a page it refuses untouched.
   The runner starts with an empty profile, so its storage proves nothing. This script answers
   a question IN the page first, reads the page's storage, runs the check as it stands, and
   reads the storage again, all in one page session.

     node plans/evidence/scripts-239/refusal_244.mjs <page.html> [chrome] [check file]

   It prints the check's lines, the number of stored keys, and whether the storage is the same.
   It exits 0 only when the check refused the page AND the storage did not change. */
import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const repo = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const page = process.argv[2];
const chrome = [process.argv[3], process.env.CHROME,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium'].find((path) => path && existsSync(path));
// an optional third argument names another check file: the control run reads HEAD's copy
const source = readFileSync(process.argv[4] || join(repo, 'tests', 'slate_browser_check.js'), 'utf8');
const check = source.slice(source.indexOf('async () =>'));
const profile = mkdtempSync(join(tmpdir(), 'slate-refusal-'));
const port = 9300 + Math.floor(Math.random() * 600);
const browser = spawn(chrome, ['--headless=new', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--no-first-run', pathToFileURL(resolve(page)).href],
  { stdio: 'ignore' });
const sleep = (ms) => new Promise((done) => setTimeout(done, ms));

async function target() {
  for (let n = 0; n < 50; n += 1) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const found = list.find((item) => item.type === 'page' && item.url.startsWith('file:'));
      if (found) { return found.webSocketDebuggerUrl; }
    } catch (error) { /* the browser is still starting */ }
    await sleep(200);
  }
  throw new Error('the browser did not open the page');
}

let code = 1;
try {
  const socket = new WebSocket(await target());
  await new Promise((done, fail) => { socket.onopen = done; socket.onerror = fail; });
  const waiting = new Map();
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (waiting.has(message.id)) { waiting.get(message.id)(message.result); }
  };
  let next = 0;
  const run = (expression) => new Promise((done) => {
    next += 1;
    waiting.set(next, done);
    socket.send(JSON.stringify({ id: next, method: 'Runtime.evaluate',
      params: { expression, awaitPromise: true, returnByValue: true } }));
  });
  const storage = 'JSON.stringify(Object.keys(localStorage).sort().map((k) => [k, localStorage.getItem(k)]))';
  await sleep(500);                                   // the page's own script has run
  await run("document.querySelector('fieldset.question input[type=\"radio\"]').click()");
  await sleep(200);
  const before = (await run(storage)).result.value;
  const value = (await run(`(${check})()`)).result.value;
  const after = (await run(storage)).result.value;
  value.lines.forEach((line) => console.log(line));
  const keys = JSON.parse(before).length;
  console.log(`stored keys before: ${keys}; storage unchanged: ${before === after}`);
  code = value.failed === 1 && value.passed === 0 && keys > 0 && before === after ? 0 : 1;
  socket.close();
} catch (error) {
  console.error('the proof did not run: ' + error.message);
} finally {
  browser.kill();
  await sleep(300);
  try { rmSync(profile, { recursive: true, force: true }); } catch (error) { /* temporary */ }
}
process.exit(code);
