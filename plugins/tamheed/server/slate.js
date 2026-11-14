/* Tamheed interview page (plans 227, 227b, 227c). ONE static script, the same for every
   slate. It reads ids and its words from data attributes, sets values, classes and a few
   fixed attributes, and copies markup only from a template that the server rendered. It
   loads nothing and sends nothing. The answers file is a record of this page. */
(function () {
  'use strict';
  var root = document.documentElement;
  var body = document.body;
  var slateName = body.getAttribute('data-slate');
  var slateDigest = body.getAttribute('data-digest');
  /* Every local page shares one storage area in a browser, so the key is this page's own
     address: it differs per folder, and it stays the same when the page is exported again. */
  var KEY = 'tamheed-slate:' + document.URL.split('#')[0].split('?')[0];
  var FORMAT = 'tamheed-slate-answers';
  var VERSION = 2;
  var ui = { presenter: false, recs: false, session: body.getAttribute('data-opens') === 'session',
             one: false, theme: '', owner: 'all', group: '', round: '', step: 0 };
  /* An id may be a name that every object inherits, such as `constructor`. A map that is
     keyed by an id has no prototype, so it holds only what was put into it. */
  function emptyMap() { return Object.create(null); }
  function own(map, id) {
    return map !== null && typeof map === 'object'
      && Object.prototype.hasOwnProperty.call(map, id) ? map[id] : undefined;
  }
  var made = emptyMap();  /* question id -> the digest of the question when it was answered */
  var storageWorks = true;
  var armed = null;

  function byId(id) { return document.getElementById(id); }
  function list(selector, within) {
    return Array.prototype.slice.call((within || document).querySelectorAll(selector));
  }
  function field(within, name) { return within.querySelector('[data-field="' + name + '"]'); }
  function text(value) { return typeof value === 'string' ? value : ''; }
  function word(name, values) {
    var out = body.getAttribute('data-w-' + name) || '';
    Object.keys(values || {}).forEach(function (key) {
      out = out.split('{' + key + '}').join(String(values[key]));
    });
    return out;
  }
  function say(message) { byId('status').textContent = message; }
  function pressed(id, on) { byId(id).setAttribute('aria-pressed', on ? 'true' : 'false'); }

  var sections = list('section.round');
  var readySections = sections.filter(function (s) { return !s.classList.contains('notready'); });
  var questions = list('fieldset.question');
  function sectionOf(id) {
    return sections.filter(function (s) { return s.getAttribute('data-round') === id; })[0];
  }
  function currentSection() { return sectionOf(ui.round) || readySections[0]; }
  /* R104: in a session the room sees the round that the presenter opened, and no other */
  function locked() { return ui.session && !ui.presenter; }

  /* ---------------------------------------------------------------- what is on the page */

  function selectedOf(question) {
    var picked = question.querySelector('input[type="radio"]:checked');
    return picked ? picked.value : null;
  }
  function isAnswered(question) {
    var picked = selectedOf(question);
    if (picked === null) { return false; }
    return picked !== 'other' || text(field(question, 'other').value).trim() !== '';
  }
  function readAnswer(question) {
    var id = question.getAttribute('data-question');
    var other = field(question, 'other');
    return { question: id, selected: selectedOf(question), other: other ? other.value : '',
             note: field(question, 'note').value, answered_by: field(question, 'answered_by').value,
             question_digest: made[id] || question.getAttribute('data-digest') };
  }
  function readRound(section) {
    var attendance = emptyMap();
    list('.attrow', section).forEach(function (row) {
      var state = field(row, 'state').value;
      if (state) {
        attendance[row.getAttribute('data-person')] = {
          state: state, covered_by: state === 'covered' ? field(row, 'covered_by').value : '' };
      }
    });
    var closure = emptyMap();
    list('[data-closure]', section).forEach(function (el) {
      closure[el.getAttribute('data-closure')] = el.value;
    });
    var points = list('.pointlist .point', section).map(function (row) {
      return { kind: field(row, 'kind').value, by: field(row, 'by').value,
               text: field(row, 'text').value };
    }).filter(function (point) { return point.text.trim() !== ''; });
    function value(name) { var el = field(section, name); return el ? el.value : ''; }
    var closed = field(section, 'closed');
    return { id: section.getAttribute('data-round'), attendance: attendance,
             guests: value('guests'), points: points, closure: closure, reopen: value('reopen'),
             closed: closed ? closed.checked : false, closed_by: value('closed_by') };
  }
  function collect(section) {
    var scope = section ? [section] : readySections;
    var data = { format: FORMAT, version: VERSION, slate: slateName, slate_digest: slateDigest,
                 exported_at: new Date().toISOString() };
    if (section) { data.round = section.getAttribute('data-round'); }
    data.rounds = scope.map(readRound);
    data.answers = [];
    scope.forEach(function (one) {
      list('fieldset.question', one).forEach(function (q) { data.answers.push(readAnswer(q)); });
    });
    return data;
  }

  /* ---------------------------------------------------------------- putting values back */

  function addPoint(section, point) {
    var template = section.querySelector('template.pointrow');
    var row = template.content.firstElementChild.cloneNode(true);
    if (point) {
      field(row, 'kind').value = text(point.kind);
      field(row, 'by').value = text(point.by);
      field(row, 'text').value = text(point.text);
    }
    section.querySelector('.pointlist').appendChild(row);
    return row;
  }
  function applyRound(section, item) {
    function put(name, value) { var el = field(section, name); if (el) { el.value = text(value); } }
    var attendance = item.attendance && typeof item.attendance === 'object' ? item.attendance : {};
    list('.attrow', section).forEach(function (row) {
      var got = own(attendance, row.getAttribute('data-person')) || {};
      field(row, 'state').value = text(got.state);
      field(row, 'covered_by').value = text(got.covered_by);
      row.classList.toggle('covered', field(row, 'state').value === 'covered');
    });
    var closure = item.closure && typeof item.closure === 'object' ? item.closure : {};
    list('[data-closure]', section).forEach(function (el) {
      el.value = text(own(closure, el.getAttribute('data-closure')));
    });
    put('guests', item.guests); put('reopen', item.reopen); put('closed_by', item.closed_by);
    var closed = field(section, 'closed');
    if (closed) { closed.checked = item.closed === true; }
    var holder = section.querySelector('.pointlist');
    if (holder) {
      while (holder.firstChild) { holder.removeChild(holder.firstChild); }
      (Array.isArray(item.points) ? item.points : []).slice(0, 200).forEach(function (point) {
        if (point && typeof point === 'object') { addPoint(section, point); }
      });
    }
  }
  function applyAnswer(question, item) {
    var id = question.getAttribute('data-question');
    list('input[type="radio"]', question).forEach(function (radio) {
      radio.checked = radio.value === item.selected;
    });
    var other = field(question, 'other');
    if (other) { other.value = text(item.other); }
    field(question, 'note').value = text(item.note);
    field(question, 'answered_by').value = text(item.answered_by);
    if (typeof item.question_digest === 'string') { made[id] = item.question_digest; }
  }
  function apply(data) {
    (Array.isArray(data.rounds) ? data.rounds : []).forEach(function (item) {
      var section = item && sectionOf(item.id);
      if (section && readySections.indexOf(section) >= 0) { applyRound(section, item); }
    });
    var byQuestion = emptyMap();
    questions.forEach(function (q) { byQuestion[q.getAttribute('data-question')] = q; });
    (Array.isArray(data.answers) ? data.answers : []).forEach(function (item) {
      var question = item && byQuestion[item.question];
      if (question) { applyAnswer(question, item); }
    });
  }

  /* ---------------------------------------------------------------- what a view shows */

  function inView(el) {
    /* true when the view's rules show this step or this question */
    if (el.classList.contains('filtered')) { return false; }
    if (ui.presenter) { return true; }
    return !(el.classList.contains('oponly') || el.getAttribute('data-owner') === 'operator');
  }
  function stepsOf(section) { return list('.step', section).filter(inView); }
  function applyFilter() {
    var shown = 0;
    questions.forEach(function (q) {
      var people = (q.getAttribute('data-people') || '').split('|');
      var hide = (ui.owner !== 'all' && q.getAttribute('data-owner') !== ui.owner)
        || (ui.group !== '' && people.indexOf(ui.group) < 0);
      q.classList.toggle('filtered', hide);
      if (!hide) { shown += 1; }
    });
    ['all', 'operator', 'room'].forEach(function (owner) { pressed('f-' + owner, ui.owner === owner); });
    byId('group-pick').value = ui.group;
    return shown;
  }
  function show() {
    root.classList.toggle('presenter', ui.presenter);
    root.classList.toggle('recs', ui.recs);
    root.classList.toggle('session', ui.session);
    root.classList.toggle('one', ui.one);
    pressed('presenter', ui.presenter); pressed('recs', ui.recs); pressed('lock', ui.session);
    pressed('view-one', ui.one); pressed('view-all', !ui.one);
    var here = currentSection();
    ui.round = here ? here.getAttribute('data-round') : '';
    var answeredAll = 0, countAll = 0, stale = 0, readyCount = 0;
    sections.forEach(function (section) {
      var mine = section === here;
      section.classList.toggle('current-round', mine);
      section.classList.toggle('open-round', mine);
      var jump = document.querySelector('.jump[data-jump="' + section.getAttribute('data-round') + '"]');
      var isReady = readySections.indexOf(section) >= 0;
      var shut = isReady && locked() && !mine;
      var option = byId('round-pick').querySelector(
        'option[value="' + section.getAttribute('data-round') + '"]');
      if (option) { option.disabled = !isReady || shut; }
      if (jump) {
        jump.classList.toggle('current-jump', mine);
        jump.classList.toggle('lockedjump', shut);
        jump.disabled = !isReady || shut;
      }
      if (!isReady) { return; }
      readyCount += 1;
      var answered = 0, count = 0;
      list('fieldset.question', section).forEach(function (q) {
        var id = q.getAttribute('data-question');
        var done = isAnswered(q);
        var old = done && made[id] && made[id] !== q.getAttribute('data-digest');
        q.classList.toggle('answered', done);
        q.querySelector('.stale').hidden = !old;
        if (old) { stale += 1; }
        var other = q.querySelector('.other');
        if (other) { other.classList.toggle('has-text', field(q, 'other').value.trim() !== ''); }
        var note = q.querySelector('.noteblock');
        var hasNote = field(q, 'note').value.trim() !== '';
        note.classList.toggle('has-text', hasNote);
        if (hasNote) { note.open = true; }
        if (!ui.presenter && q.getAttribute('data-owner') === 'operator') { return; }
        count += 1;
        if (done) { answered += 1; }
      });
      section.querySelector('.roundcount').textContent =
        shut ? word('locked') : word('roundcount', { n: answered, total: count });
      if (jump) { jump.querySelector('.jstate').textContent = shut ? word('locked') : ''; }
      section.querySelector('.meter span').style.width =
        (count ? Math.round(100 * answered / count) : 0) + '%';
      if (jump) { jump.classList.toggle('done', count > 0 && answered === count); }
      answeredAll += answered; countAll += count;
    });
    /* a block's heading goes with its questions: it hides when the view shows none of them */
    list('.blockhead').forEach(function (head) {
      var any = false;
      for (var el = head.nextElementSibling; el && !el.classList.contains('blockhead');
           el = el.nextElementSibling) {
        if (el.classList.contains('question') && inView(el)) { any = true; }
      }
      head.classList.toggle('filtered', !any);
    });
    byId('progress').textContent = word('progress', { n: answeredAll, total: countAll });
    var ready = document.querySelector('.navready');
    if (ready) { ready.textContent = word('ready', { n: readyCount, total: sections.length }); }
    var banner = document.querySelector('.stalebanner');
    banner.hidden = stale === 0;
    banner.textContent = stale ? word('stale', { n: stale }) : '';
    byId('round-pick').value = ui.round;
    list('.step.current').forEach(function (el) { el.classList.remove('current'); });
    if (here) {
      var steps = stepsOf(here);
      ui.step = Math.max(0, Math.min(ui.step, steps.length - 1));
      if (steps[ui.step]) { steps[ui.step].classList.add('current'); }
      byId('position').textContent = word('position', {
        round: here.querySelector('h2 bdi').textContent, n: steps.length ? ui.step + 1 : 0,
        total: steps.length });
    }
  }
  function keep() {
    if (!storageWorks) { return; }
    try {
      localStorage.setItem(KEY, JSON.stringify({ answers: collect(), made: made, ui: ui }));
    } catch (error) {
      storageWorks = false;
      var banner = document.querySelector('.storebanner');
      banner.textContent = word('nostorage');
      banner.hidden = false;
    }
  }
  function restore() {
    var kept = null;
    try { kept = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (error) { kept = null; }
    if (!kept || typeof kept !== 'object') { return; }
    if (kept.answers && typeof kept.answers === 'object') { apply(kept.answers); }
    if (kept.made && typeof kept.made === 'object') {
      Object.keys(kept.made).forEach(function (id) {
        if (typeof kept.made[id] === 'string') { made[id] = kept.made[id]; }
      });
    }
    if (kept.ui && typeof kept.ui === 'object') {
      ['presenter', 'recs', 'session', 'one'].forEach(function (name) {
        if (typeof kept.ui[name] === 'boolean') { ui[name] = kept.ui[name]; }
      });
      ['theme', 'owner', 'group', 'round'].forEach(function (name) {
        if (typeof kept.ui[name] === 'string') { ui[name] = kept.ui[name]; }
      });
      if (typeof kept.ui.step === 'number') { ui.step = kept.ui.step; }
      if (['all', 'operator', 'room'].indexOf(ui.owner) < 0) { ui.owner = 'all'; }
    }
  }
  function changed() { show(); keep(); }

  /* ---------------------------------------------------------------- moving */

  function goRound(id, last) {
    var section = sectionOf(id);
    if (!section || readySections.indexOf(section) < 0) { return; }
    if (locked() && section !== currentSection()) { return; }
    ui.round = id;
    ui.step = last ? stepsOf(section).length - 1 : 0;
    changed();
    if (!ui.one) { section.scrollIntoView(); }
  }
  function move(by) {
    var here = currentSection();
    if (!here) { return; }
    var next = ui.step + by;
    var at = readySections.indexOf(here);
    if (next >= stepsOf(here).length) {
      if (at < readySections.length - 1) {
        goRound(readySections[at + 1].getAttribute('data-round'), false);
      }
      return;
    }
    if (next < 0) {
      if (at > 0) { goRound(readySections[at - 1].getAttribute('data-round'), true); }
      return;
    }
    ui.step = next;
    changed();
    window.scrollTo(0, 0);
  }
  function setOne(on) {
    if (on && !ui.one) {
      /* start at the step that is on the screen now */
      var here = currentSection();
      var steps = here ? stepsOf(here) : [];
      steps.forEach(function (step, at) {
        if (step.getBoundingClientRect().top < window.innerHeight / 2) { ui.step = at; }
      });
    }
    ui.one = on;
    changed();
    if (on) { window.scrollTo(0, 0); }      /* the step starts at its top */
    if (!on) {
      var current = document.querySelector('.step.current');
      if (current) { current.scrollIntoView(); }
    }
  }
  function applyTheme() {
    if (ui.theme) { root.setAttribute('data-theme', ui.theme); }
  }
  function toggleTheme() {
    var now = root.getAttribute('data-theme')
      || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    ui.theme = now === 'light' ? 'dark' : 'light';
    applyTheme();
    keep();
  }

  /* ---------------------------------------------------------------- files */

  function fileName(section) {
    return slateName + (section ? '.' + section.getAttribute('data-round') : '') + '.answers.json';
  }
  function saveFile(section) {
    var data = collect(section);
    var content = JSON.stringify(data, null, 1);
    var name = fileName(section);
    byId('answers-text').value = content;
    byId('answers-name').textContent = name;
    try {
      var link = byId('download');
      var url = URL.createObjectURL(new Blob([content], { type: 'application/json' }));
      link.href = url;
      link.download = name;
      link.click();      /* the address is not revoked: a revoke can cancel the download */
      say(word('saved', { file: name }));
    } catch (error) {
      byId('trouble').open = true;
      say(word('savefail'));
    }
  }
  function loadFile(file, section) {
    if (!file) { return; }
    file.text().then(function (content) {
      var data = null;
      try { data = JSON.parse(content); } catch (error) { data = null; }
      if (!data || data.format !== FORMAT || data.version !== VERSION || data.slate !== slateName) {
        say(word('notfit'));
        return;
      }
      if (section && data.round !== section.getAttribute('data-round')) {
        say(word('notround'));
        return;
      }
      apply(data);
      changed();
      say(word('loaded', { file: file.name }));
    }, function () { say(word('unreadable')); });
  }
  function clearSection(section) {
    list('input[type="radio"], input[type="checkbox"]', section).forEach(function (el) {
      el.checked = false;
    });
    list('textarea, input[type="text"], select', section).forEach(function (el) { el.value = ''; });
    list('.pointlist .point', section).forEach(function (row) { row.parentNode.removeChild(row); });
    list('.attrow', section).forEach(function (row) { row.classList.remove('covered'); });
    list('details.noteblock', section).forEach(function (el) { el.open = false; });
    list('fieldset.question', section).forEach(function (q) {
      delete made[q.getAttribute('data-question')];
    });
  }
  function disarm() {
    if (armed) { armed.button.textContent = armed.label; armed = null; }
  }
  function twice(button, act) {
    /* a clear needs two clicks on the same button */
    if (armed && armed.button === button) { disarm(); act(); return; }
    disarm();
    armed = { button: button, label: button.textContent };
    button.textContent = word('clear2');
  }

  /* ---------------------------------------------------------------- print */

  var opened = [];
  function beforePrint() {
    opened = list('details.quote, details.fields, details.about, details.ctx').filter(
      function (el) { return !el.open; });
    opened.forEach(function (el) { el.open = true; });
  }
  function afterPrint() {
    opened.forEach(function (el) { el.open = false; });
    opened = [];
  }

  /* ---------------------------------------------------------------- events */

  function typing(target) {
    /* true when a key belongs to a control: a text, a choice or a list */
    var tag = target && target.tagName;
    return tag === 'TEXTAREA' || tag === 'INPUT' || tag === 'SELECT';
  }
  function on(id, handler) { byId(id).addEventListener('click', handler); }
  function roundOf(el) { return el.closest('section.round'); }

  document.addEventListener('input', function (event) {
    var target = event.target;
    if (!target || target.id === 'answers-text') { return; }
    var question = target.closest('fieldset.question');
    if (question) {
      made[question.getAttribute('data-question')] = question.getAttribute('data-digest');
      if (target.getAttribute('data-field') === 'other' && target.value.trim() !== '') {
        question.querySelector('input[value="other"]').checked = true;
      }
    }
    disarm();
    changed();
  });
  document.addEventListener('change', function (event) {
    var target = event.target;
    if (!target) { return; }
    if (target.id === 'load') { loadFile(target.files[0], null); target.value = ''; return; }
    if (target.id === 'load-round') {
      loadFile(target.files[0], currentSection());
      target.value = '';
      return;
    }
    if (target.id === 'round-pick') { goRound(target.value, false); return; }
    if (target.id === 'group-pick') { ui.group = target.value; applyFilter(); ui.step = 0; changed(); return; }
    var row = target.closest('.attrow');
    if (row && target.getAttribute('data-field') === 'state') {
      row.classList.toggle('covered', target.value === 'covered');
    }
    var question = target.closest('fieldset.question');
    if (question) {
      made[question.getAttribute('data-question')] = question.getAttribute('data-digest');
    }
    changed();
  });
  document.addEventListener('keydown', function (event) {
    /* In the view of one step the arrow keys turn the step. A key that belongs to a control
       stays with the control: an arrow moves between the options of a question. */
    if (!ui.one || typing(event.target) || event.altKey || event.ctrlKey || event.metaKey
        || event.shiftKey) { return; }
    var forward = root.getAttribute('dir') === 'rtl' ? 'ArrowLeft' : 'ArrowRight';
    var back = forward === 'ArrowLeft' ? 'ArrowRight' : 'ArrowLeft';
    if (event.key === forward || event.key === 'PageDown') { event.preventDefault(); move(1); }
    if (event.key === back || event.key === 'PageUp') { event.preventDefault(); move(-1); }
  });
  document.addEventListener('click', function (event) {
    var target = event.target;
    var more = document.querySelector('details.more');
    if (more.open && !more.contains(target)) { more.open = false; }
    var button = target.closest ? target.closest('button') : null;
    if (!button) { return; }
    var jump = button.getAttribute('data-jump');
    if (jump) { goRound(jump, false); return; }
    var action = button.getAttribute('data-action');
    if (!action) { return; }
    var section = roundOf(button);
    if (action === 'add-point') { addPoint(section, null).querySelector('textarea').focus(); }
    if (action === 'remove-point') {
      var row = button.closest('.point');
      row.parentNode.removeChild(row);
      changed();
    }
    if (action === 'save-round') { saveFile(section); }
    if (action === 'load-round') {
      ui.round = section.getAttribute('data-round');
      byId('load-round').click();
    }
    if (action === 'clear-round') {
      twice(button, function () { clearSection(section); changed(); say(word('roundcleared')); });
    }
  });
  window.addEventListener('beforeprint', beforePrint);
  window.addEventListener('afterprint', afterPrint);
  on('view-all', function () { setOne(false); });
  on('view-one', function () { setOne(true); });
  on('presenter', function () { ui.presenter = !ui.presenter; ui.step = 0; changed(); });
  on('recs', function () { ui.recs = !ui.recs; changed(); });
  on('lock', function () { ui.session = !ui.session; changed(); });
  ['all', 'operator', 'room'].forEach(function (owner) {
    on('f-' + owner, function () {
      ui.owner = owner;
      ui.step = 0;
      var shown = applyFilter();
      changed();
      say(word('shown', { n: shown }));
    });
  });
  on('theme', toggleTheme);
  on('save', function () { saveFile(null); });
  on('load-button', function () { byId('load').click(); });
  on('print', function () { window.print(); });
  on('clear', function () {
    twice(byId('clear'), function () {
      sections.forEach(clearSection);
      changed();
      say(word('cleared'));
    });
  });
  on('prev', function () { move(-1); });
  on('next', function () { move(1); });

  restore();
  applyTheme();
  applyFilter();
  show();
  root.classList.add('ready');
}());
