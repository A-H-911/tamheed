/* The standup page's one script (plan 251 v2, U1). Named by its SHA-256 in the page's content
   policy. It loads nothing, sends nothing and writes no markup: it reads data attributes and sets
   `hidden`, `open`, `aria-pressed`, a status text and one stored colour choice. */
(() => {
  'use strict';
  const doc = document;
  doc.documentElement.dataset.js = 'on';

  // The colour choice: auto, light or dark. A stored value outside the three is ignored.
  const KEY = 'tamheed-standup-colours';
  const CHOICES = ['auto', 'light', 'dark'];
  try {
    const stored = window.localStorage.getItem(KEY);
    if (CHOICES.includes(stored)) {
      const radio = doc.getElementById('theme-' + stored);
      if (radio) radio.checked = true;
    }
  } catch (e) { /* storage refused: the page keeps Auto */ }
  doc.querySelectorAll('input[name="theme"]').forEach((radio) => {
    radio.addEventListener('change', () => {
      const value = radio.id.replace('theme-', '');
      if (!CHOICES.includes(value)) return;
      try { window.localStorage.setItem(KEY, value); } catch (e) { /* not stored */ }
    });
  });

  // The plan tree: filters, search, expand and collapse.
  const tree = doc.getElementById('tree');
  const controls = doc.getElementById('tree-controls');
  if (!tree || !controls) return;
  controls.hidden = false;
  const items = Array.from(tree.querySelectorAll('[data-item]'));
  const folds = Array.from(tree.querySelectorAll('details'));
  const opened = new Map(folds.map((d) => [d, d.open]));
  const status = doc.getElementById('tree-status');
  const search = doc.getElementById('tree-search');
  const phaseSelect = doc.getElementById('tree-phase');
  const chosen = { state: 'all', kind: 'all' };

  function matches(el) {
    const query = search.value.trim().toLowerCase();
    return (chosen.state === 'all' || el.dataset.state === chosen.state)
      && (chosen.kind === 'all' || el.dataset.kind === chosen.kind)
      && (phaseSelect.value === 'all' || el.dataset.phase === phaseSelect.value)
      && (!query || (el.dataset.text || '').includes(query));
  }

  function apply() {
    const filtering = chosen.state !== 'all' || chosen.kind !== 'all'
      || phaseSelect.value !== 'all' || search.value.trim() !== '';
    tree.querySelectorAll('[data-row]').forEach((row) => { row.hidden = filtering; });
    if (!filtering) {
      opened.forEach((wasOpen, d) => { d.open = wasOpen; });
      status.textContent = 'Showing all ' + items.length + ' items.';
      return;
    }
    let shown = 0;
    items.forEach((el) => {
      if (!matches(el)) return;
      shown += 1;
      let node = el;
      while (node && node !== tree) {
        if (node.dataset && node.dataset.row !== undefined) node.hidden = false;
        if (node.tagName === 'DETAILS' && node !== el) node.open = true;
        node = node.parentElement;
      }
    });
    status.textContent = 'Showing ' + shown + ' of ' + items.length + ' items.';
  }

  controls.querySelectorAll('button[data-filter]').forEach((button) => {
    button.addEventListener('click', () => {
      const group = button.dataset.filter;
      chosen[group] = button.dataset.value;
      controls.querySelectorAll('button[data-filter="' + group + '"]').forEach((b) => {
        b.setAttribute('aria-pressed', String(b === button));
      });
      apply();
    });
  });
  search.addEventListener('input', apply);
  phaseSelect.addEventListener('change', apply);
  doc.getElementById('tree-open').addEventListener('click', () => {
    folds.forEach((d) => { d.open = true; });
  });
  doc.getElementById('tree-close').addEventListener('click', () => {
    folds.forEach((d) => { d.open = false; });
  });
  apply();
})();
