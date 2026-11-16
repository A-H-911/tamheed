/* Browser check of the interview page's script (plan 227c, R114; plan 244, R126).

   The gate reads the script as text, and CI runs no browser. This file checks what the
   script DOES. It is not loaded by the page: the page's content policy admits one script.
   Run it from a browser's developer tools, or through the DevTools protocol, against a page
   that `slate_export` wrote.

   THE PAGE'S SHAPE. The page needs at least one ready round with a question of the room. A
   page without one is refused BEFORE anything changes, and its answers stay as they were.
   Each other part of the page gates the checks that read it: a second ready round, a round
   that is not ready, participants, a question of the operator, a recommendation. When a part
   is missing, its checks print SKIP with the part they need. The demo slate of
   plans/evidence/scripts-227/demo_227c.py has every part, so nothing skips on it.

   The file is ONE async function. It answers {passed, skipped, failed, lines}. It starts no
   download. ON A PAGE IT ACCEPTS, IT CLEARS EVERY ANSWER THAT THE PAGE HOLDS, first and again
   at its end. Save the answers to a file before you run it on a page that people have
   answered. */
async () => {
  const lines = [];
  const check = (name, ok) => lines.push((ok ? 'pass ' : 'FAIL ') + name);
  const $ = (selector, within) => (within || document).querySelector(selector);
  const $$ = (selector, within) => Array.from((within || document).querySelectorAll(selector));
  const root = document.documentElement;
  const shown = (el) => !!el && getComputedStyle(el).display !== 'none' && el.offsetParent !== null;
  const click = (id) => document.getElementById(id).click();
  const fire = (el, type) => el.dispatchEvent(new Event(type, { bubbles: true }));
  const key = (target, name) => {
    const event = new KeyboardEvent('keydown', { key: name, bubbles: true, cancelable: true });
    target.dispatchEvent(event);
    return event;
  };
  const position = () => document.getElementById('position').textContent;
  const word = (name) => document.body.getAttribute('data-w-' + name);
  const status = () => document.getElementById('status').textContent;
  const set = (name, on) => {
    if (root.classList.contains(name) === on) { return; }
    click(name === 'session' ? 'lock' : name === 'one' ? (on ? 'view-one' : 'view-all') : name);
  };
  const clearAll = () => { click('clear'); click('clear'); };
  const saved = () => JSON.parse(document.getElementById('answers-text').value);
  const load = async (inputId, data, name) => {
    const transfer = new DataTransfer();
    transfer.items.add(new File([JSON.stringify(data)], name || 'x.json', { type: 'application/json' }));
    const input = document.getElementById(inputId);
    input.files = transfer.files;
    document.getElementById('status').textContent = '';
    fire(input, 'change');
    /* the page reads the file and then says what it did: wait for that word */
    for (let n = 0; n < 100 && status() === ''; n += 1) {
      await new Promise((done) => setTimeout(done, 50));
    }
  };
  /* the page's shape, read from its classes BEFORE anything changes (plan 244, FB-018): a
     page with no ready round that asks the room a question is refused, untouched */
  const sections = $$('section.round');
  const ready = sections.filter((s) => !s.classList.contains('notready'));
  const first = ready.filter((s) => $('fieldset.question[data-owner="room"]', s))[0];
  if (!first) {
    return { passed: 0, skipped: 0, failed: 1, lines: ['FAIL the page has no ready round with a'
      + ' question of the room. The check changed nothing on it.'] };
  }
  const second = ready.filter((s) => s !== first)[0];
  const later = ready[ready.indexOf(first) + 1];
  /* looked up in the ready rounds only: a round that is not ready shows nothing */
  const within = (selector) => ready.map((s) => $(selector, s)).filter(Boolean)[0] || null;
  const operator = within('fieldset.question[data-owner="operator"]');
  const recmark = within('.recmark');
  const recreason = within('.recreason');
  const needs = {
    second: second ? '' : 'a second ready round',
    later: later ? '' : 'a ready round after the first',
    notReady: sections.length > ready.length ? '' : 'a round that is not ready',
    operator: operator ? '' : 'a question of the operator',
    rec: recmark ? '' : 'a recommendation',
  };
  const skip = (name, need) => lines.push('SKIP ' + name + ' (needs ' + need + ')');
  const gated = (need, name, ok) => (need ? skip(name, need) : check(name, ok()));

  /* the check starts no download: the link's click is replaced while it runs */
  const link = document.getElementById('download');
  let downloads = 0;
  link.click = () => { downloads += 1; };

  try {
    set('one', false); set('presenter', false); set('recs', false); set('session', false);
    click('f-all');
    clearAll();
    const room = $('fieldset.question[data-owner="room"]', first);
    const open = (section) => {
      const id = section.getAttribute('data-round');
      const jump = $('.jump[data-jump="' + id + '"]');
      if (shown(jump)) { jump.click(); } else { $('#round-pick').value = id; fire($('#round-pick'), 'change'); }
    };
    open(first);
    const firstId = first.getAttribute('data-round');

    check('the page holds one script', $$('script').length === 1);
    gated(needs.operator, 'room view hides the operator question', () => !shown(operator));
    check('room view hides attendance and closure', $$('.oponly').every((el) => !shown(el)));
    gated(needs.rec, 'recommendations are hidden until they are shown', () => !shown(recmark));
    set('presenter', true);
    gated(needs.operator, 'presenter view shows the operator question', () => shown(operator));
    check('presenter view shows attendance and closure', shown($('.attendance')) && shown($('.closure')));
    check('presenter view shows the controls', shown($('.controls')));
    gated(needs.rec, 'the presenter switch does not show recommendations', () => !shown(recmark));
    set('recs', true);
    gated(needs.rec, 'Show recommendations shows the badge and the reason',
      () => shown(recmark) && shown(recreason));

    const radio = $('input[type="radio"]', room);
    radio.click();
    check('a chosen option marks the question answered', room.classList.contains('answered'));
    const fill = (name, values) => Object.keys(values).reduce(
      (text, key) => text.split('{' + key + '}').join(String(values[key])), word(name));
    const total = $$('fieldset.question').filter((q) => !q.closest('.notready')).length;
    check('progress counts the answer',
      document.getElementById('progress').textContent === fill('progress', { n: 1, total: total }));
    const unknown = $('input[value="unknown"]', room);
    if (unknown) { unknown.click(); }
    check('Unknown is a valid answer', !unknown || room.classList.contains('answered'));
    const other = $('[data-field="other"]', room);
    if (other) { other.value = 'a third way'; fire(other, 'input'); }
    check('typing a free answer selects it', !other || $('input[value="other"]', room).checked);
    radio.click();

    window.scrollTo(0, 400);
    click('view-one');
    check('the view of one step starts at the top of the step', window.scrollY === 0);
    const before = position();
    radio.focus();
    const onRadio = key(radio, 'ArrowRight');
    check('an arrow key on a focused option does not turn the step',
      position() === before && !onRadio.defaultPrevented);
    radio.blur();
    /* the key that goes forward follows the page's direction */
    const rtl = root.getAttribute('dir') === 'rtl';
    key(document.body, rtl ? 'ArrowLeft' : 'ArrowRight');
    const moved = position();
    check('an arrow key on the page turns the step', moved !== before);
    key(document.body, rtl ? 'ArrowRight' : 'ArrowLeft');
    check('the other arrow key turns it back', position() === before);
    check('one step is on the screen', $$('.step').filter(shown).length === 1);
    if (later) {
      for (let n = 0; n < 400 && $('section.round.current-round') === first; n += 1) { click('next'); }
    }
    const after = $('section.round.current-round');
    gated(needs.later, 'Next crosses to the next ready round',
      () => after !== first && ready.indexOf(after) === ready.indexOf(first) + 1);
    gated(needs.later, 'the position line names the round',
      () => position().indexOf($('h2 bdi', after).textContent) === 0);
    click('view-all');
    open(first);
    check('a round can be opened from the list', $('section.round.current-round') === first);
    const notReady = $$('.jump').filter((b) => b.disabled).length + $$('#round-pick option').filter((o) => o.disabled).length;
    gated(needs.notReady, 'a round that is not ready cannot be opened', () => notReady > 0);

    const row = $('.attrow', first);
    if (row) {
      const state = $('[data-field="state"]', row);
      state.value = 'covered'; fire(state, 'change');
      check('a covered participant asks who covers', shown($('[data-field="covered_by"]', row)));
      $('[data-field="covered_by"]', row).value = 'Someone'; fire($('[data-field="covered_by"]', row), 'input');
    } else {
      skip('a covered participant asks who covers', 'participants in the first round');
    }
    $('[data-action="add-point"]', first).click();
    const point = $('.pointlist .point', first);
    check('Add a line copies one row from the template', $$('.pointlist .point', first).length === 1 && !!point);
    $('[data-field="text"]', point).value = 'A point'; fire($('[data-field="text"]', point), 'input');

    click('f-operator');
    gated(needs.operator, 'the owner filter hides the room questions',
      () => !shown(room) && shown(operator));
    check('a block heading hides with its questions', $$('.blockhead').filter(shown).every((head) => {
      for (let el = head.nextElementSibling; el && !el.classList.contains('blockhead'); el = el.nextElementSibling) {
        if (el.classList.contains('question') && shown(el)) { return true; }
      }
      return false;
    }));
    click('f-all');
    const group = $('#group-pick');
    const people = (room.getAttribute('data-people') || '').split('|').filter(Boolean);
    const stranger = people.length && !group.hidden
      ? $$('option', group).map((o) => o.value).filter((v) => v && people.indexOf(v) < 0)[0] : '';
    if (stranger) {
      group.value = stranger; fire(group, 'change');
      check('the participant filter hides a question that does not name them', !shown(room));
      group.value = ''; fire(group, 'change');
    } else {
      skip('the participant filter hides a question that does not name them',
        'participants, one of them not named by the question');
    }
    check('the filters reset', shown(room));
    set('session', true); set('presenter', false);
    gated(needs.second, 'the session lock shows the room one round',
      () => $$('.step', first).some(shown) && $$('.step', second).every((el) => !shown(el)));
    if (second) { open(second); }
    gated(needs.second, 'the room cannot open another round in a session',
      () => $('section.round.current-round') === first);
    click('view-one');
    for (let n = 0; n < 400; n += 1) { click('next'); }
    gated(needs.second, 'and Next stops at the end of the open round',
      () => $('section.round.current-round') === first);
    click('view-all');
    set('session', false); set('presenter', true);

    const stored = Object.keys(localStorage).filter((k) => k.indexOf('tamheed-slate:') === 0);
    check('answers are kept under this page\'s own address', stored.some((k) => k.indexOf(document.URL.split('#')[0].split('?')[0]) > 0));

    $('[data-action="save-round"]', first).click();
    let file = saved();
    const roomId = room.getAttribute('data-question');
    const mine = file.answers.filter((a) => a.question === roomId)[0];
    check('a round file names its round and holds only it',
      file.round === firstId && file.rounds.length === 1
      && file.answers.length === $$('fieldset.question', first).length);
    check('a round file is version 2 with a digest per answer',
      file.version === 2 && !!mine && mine.question_digest === room.getAttribute('data-digest'));
    check('the round file keeps the point and the attendance',
      file.rounds[0].points.length === 1 && (!row || Object.keys(file.rounds[0].attendance).length === 1));
    check('the round file has its own name', link.download === document.body.getAttribute('data-slate') + '.' + firstId + '.answers.json');
    click('save');
    const whole = saved();
    check('the file of the whole page names no round and holds every ready round',
      whole.round === undefined && whole.rounds.length === ready.length);
    check('saving started the two downloads, and the check stopped them', downloads === 2);

    const old = JSON.parse(JSON.stringify(file));
    old.answers.forEach((a) => { a.question_digest = 'an-earlier-version'; });
    await load('load', old, 'old.json');
    check('an answer of an earlier version is marked on its card', !$('.stale', room).hidden);
    check('and a banner counts such answers', !$('.stalebanner').hidden);
    await load('load', Object.assign({}, file, { slate: 'another-slate' }));
    check('a file of another slate is refused', status() === word('notfit'));
    if (second) {
      open(second);
      await load('load-round', file);
    }
    gated(needs.second, 'a round refuses the file of another round',
      () => status() === word('notround'));

    const clear = $('[data-action="clear-round"]', first);
    clear.click();
    check('Clear this round asks for a second click', room.classList.contains('answered'));
    clear.click();
    check('the second click clears the round', !room.classList.contains('answered') && $$('.pointlist .point', first).length === 0);

    const theme = root.getAttribute('data-theme');
    click('theme');
    check('the scheme switch sets the scheme', root.getAttribute('data-theme') !== theme);
    click('theme');
    const folds = $$('details.quote, details.ctx');
    window.dispatchEvent(new Event('beforeprint'));
    const allOpen = folds.every((el) => el.open);
    window.dispatchEvent(new Event('afterprint'));
    check('print opens the folds and closes them after', folds.length === 0 || (allOpen && folds.some((el) => !el.open)));
    check('the page does not scroll sideways', root.scrollWidth <= root.clientWidth);
    /* an id that every object inherits is no answer, and a file that names one loads */
    await load('load', Object.assign({}, whole, { answers: [{ question: 'constructor', selected: 'A' }],
      rounds: [{ id: firstId, attendance: { constructor: { state: 'present' } }, closure: {} }] }));
    check('a file that names an inherited id loads and marks nothing', status().indexOf('x.json') >= 0
      && $$('.stale').every((el) => el.hidden) && $$('.attrow.covered', first).length === 0);
  } catch (error) {
    lines.push('FAIL the check threw: ' + error.message);
  } finally {
    try { clearAll(); set('presenter', false); set('recs', false); set('one', false); } catch (error) { /* the page is as it was left */ }
    delete link.click;
  }
  const failed = lines.filter((line) => line.indexOf('FAIL') === 0).length;
  const skipped = lines.filter((line) => line.indexOf('SKIP') === 0).length;
  return { passed: lines.length - failed - skipped, skipped: skipped, failed: failed, lines: lines };
}
