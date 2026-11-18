/* Browser check of the standup page's script and look (plan 251 v2, U4).

   The gate reads the script as text. This file checks what the page DOES in a real browser:
   the filters, the search, expand and collapse, the remembered colour choice, and the contrast
   of the state words in both themes. tests/run_standup_browser_check.mjs runs it, and also
   checks the phone width and print. The page comes from tests/standup_browser_page.py.

   The file is ONE async function. It answers {passed, failed, lines}. It changes nothing but
   the page's own controls and its stored colour choice. */
async () => {
  const lines = [];
  const check = (name, ok, more) => lines.push((ok ? 'pass ' : 'FAIL ') + name + (ok || !more ? '' : ' (' + more + ')'));
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const status = () => ($('#tree-status') || {}).textContent || '';
  const visible = (el) => !el.closest('[hidden]');
  const items = () => $$('#tree [data-item]');
  const press = (group, value) => $(`button[data-filter="${group}"][data-value="${value}"]`).click();

  check('the script ran under the page policy', document.documentElement.dataset.js === 'on');
  check('the tree controls are shown', !!$('#tree-controls') && !$('#tree-controls').hidden);
  const total = items().length;
  check('the status counts every item', status() === `Showing all ${total} items.`, status());

  // each state chip shows exactly the rows of its state, and says how many
  $$('button[data-filter="state"]').filter((b) => b.dataset.value !== 'all').forEach((b) => {
    const state = b.dataset.value;
    const n = Number((b.querySelector('.n') || {}).textContent);
    b.click();
    const shown = items().filter(visible).filter((el) => el.dataset.state === state).length;
    check(`chip "${state}" shows its ${n} rows`, shown === n && status() === `Showing ${n} of ${total} items.`,
          `shown ${shown}, ${status()}`);
  });
  press('state', 'all');

  press('kind', 'check');
  const checks = items().filter(visible);
  check('the kind filter keeps checks only', checks.length > 0 && checks.every((el) => el.dataset.kind === 'check'));
  press('kind', 'all');

  const phase = $('#tree-phase');
  phase.value = phase.options[1].value;
  phase.dispatchEvent(new Event('change'));
  const inPhase = items().filter(visible);
  check('the phase filter keeps that phase', inPhase.length > 0 && inPhase.every((el) => el.dataset.phase === phase.value));
  phase.value = 'all';
  phase.dispatchEvent(new Event('change'));

  const search = $('#tree-search');
  const sample = items().filter((el) => el.dataset.kind === 'task').pop();
  const wanted = sample.dataset.text.split(' ').pop();      // the row's own id
  search.value = wanted;
  search.dispatchEvent(new Event('input'));
  const found = items().filter(visible).filter((el) => el.dataset.text.split(' ').pop() === wanted);
  check('the search finds a row by its id', found.length === 1, status());
  check('the search opens the branch above the match', found.length === 1 && !!found[0].closest('details[open]'));
  search.value = '';
  search.dispatchEvent(new Event('input'));
  check('clearing the filters shows every item again', status() === `Showing all ${total} items.`);

  $('#tree-open').click();
  check('expand all opens every fold', $$('#tree details').every((d) => d.open));
  $('#tree-close').click();
  check('collapse all closes every fold', $$('#tree details').every((d) => !d.open));

  // the colours: the switch, the stored choice, and contrast in both themes
  const rgb = (c) => (c.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
  const lum = ([r, g, b]) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => { const [x, y] = [lum(rgb(a)), lum(rgb(b))].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const card = () => getComputedStyle($('section.card')).backgroundColor;
  for (const theme of ['light', 'dark']) {
    $(`#theme-${theme}`).click();
    const body = getComputedStyle(document.body).backgroundColor;
    check(`the ${theme} switch sets the ${theme} colours`, theme === 'dark' ? lum(rgb(body)) < 0.1 : lum(rgb(body)) > 0.8);
    let stored = null;
    try { stored = window.localStorage.getItem('tamheed-standup-colours'); } catch (e) { stored = 'unavailable'; }
    check(`the ${theme} choice is stored`, stored === theme || stored === 'unavailable', stored);
    const seen = new Set();
    $$('#tree .state').forEach((el) => {
      const cls = Array.from(el.classList).find((c) => c.startsWith('s-'));
      if (!cls || seen.has(cls) || cls === 's-now') return;
      seen.add(cls);
      const r = ratio(getComputedStyle(el).color, card());
      check(`${theme}: "${cls.slice(2)}" text contrast is at least 4.5:1`, r >= 4.5, r.toFixed(2));
    });
    const fill = $('#tree .bar > span');
    if (fill) {
      const r = ratio(getComputedStyle(fill).backgroundColor, getComputedStyle(fill.parentElement).backgroundColor);
      check(`${theme}: a progress bar is at least 3:1 against its track`, r >= 3, r.toFixed(2));
    }
  }
  $('#theme-auto').click();
  const passed = lines.filter((l) => l.startsWith('pass')).length;
  return { passed, failed: lines.length - passed, lines };
}
