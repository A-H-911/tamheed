// Print the width of every visible element of the reading column at a given viewport.
// Plan 257 (R151): the local width evidence. node widths_257.mjs <page.html> <width> <out.json>
// Chrome: the CHROME variable, or the default Windows path.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [page, width, out] = process.argv.slice(2);
const chrome = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const profile = mkdtempSync(join(tmpdir(), 'w-'));
const port = 9900 + Math.floor(Math.random() * 90);
const browser = spawn(chrome, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  '--no-first-run', `--window-size=${width},900`, pathToFileURL(resolve(page)).href], { stdio: 'ignore' });
const sleep = (ms) => new Promise((d) => setTimeout(d, ms));
let ws;
for (let n = 0; n < 100 && !ws; n += 1) {
  try { const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
        const f = l.find((i) => i.type === 'page' && i.url.startsWith('file:')); if (f) ws = f.webSocketDebuggerUrl; } catch (e) {}
  await sleep(200);
}
const socket = new WebSocket(ws);
await new Promise((d) => { socket.onopen = d; });
let id = 0; const wait = new Map();
socket.onmessage = (e) => { const m = JSON.parse(e.data); if (wait.has(m.id)) { wait.get(m.id)(m.result); wait.delete(m.id); } };
const send = (method, params) => { id += 1; socket.send(JSON.stringify({ id, method, params })); return new Promise((d) => wait.set(id, d)); };
await sleep(1500);
const r = await send('Runtime.evaluate', { returnByValue: true, expression: `(() => {
  document.getElementById('view-all').click();
  const path = (el) => { const p = []; while (el && el.classList && !el.classList.contains('column')) {
    const sib = el.parentElement ? Array.from(el.parentElement.children).indexOf(el) : 0;
    p.unshift(el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '') + ':' + sib); el = el.parentElement; }
    return p.join('>'); };
  const all = {}; document.querySelectorAll('.column *').forEach((el) => { const w = el.getBoundingClientRect().width; if (w) all[path(el)] = Math.round(w * 10) / 10; });
  const nav = {}; document.querySelectorAll('.roundnav *, .bar *').forEach((el, i) => { const w = el.getBoundingClientRect().width; if (w) nav[i + ':' + el.className] = Math.round(w * 10) / 10; });
  return { all, nav, inner: window.innerWidth };
})()` });
writeFileSync(out, JSON.stringify(r.result.value));
socket.close(); browser.kill(); await sleep(300); try { rmSync(profile, { recursive: true, force: true }); } catch (e) {}
