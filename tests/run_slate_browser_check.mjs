/* Run tests/slate_browser_check.js against one exported interview page (plan 227c, R114).

     node tests/run_slate_browser_check.mjs <path to the page.html> [path to chrome]

   It starts a headless Chrome with a fresh, temporary profile, opens the page from its file,
   evaluates the check file as it stands through the DevTools protocol, prints each line, and
   exits 1 when a check fails. It needs Node 22 or later (for the built-in WebSocket) and a
   Chrome or Chromium. It loads no package. CI does not run it. */
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
  const answer = new Promise((done) => {
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id === 1) { done(message.result); }
    };
  });
  await sleep(500);                       // the page's own script has run
  socket.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate', params: {
    expression: `(${check})()`, awaitPromise: true, returnByValue: true } }));
  const result = await answer;
  if (result.exceptionDetails) { throw new Error(JSON.stringify(result.exceptionDetails).slice(0, 400)); }
  const value = result.result.value;
  value.lines.forEach((line) => console.log(line));
  console.log(`${value.passed} passed, ${value.failed} failed`);
  code = value.failed === 0 ? 0 : 1;
  socket.close();
} catch (error) {
  console.error('the check did not run: ' + error.message);
} finally {
  browser.kill();
  await sleep(300);
  try { rmSync(profile, { recursive: true, force: true }); } catch (error) { /* the profile is temporary */ }
}
process.exit(code);
