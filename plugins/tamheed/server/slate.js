/* Tamheed interview page (plan 227). The ONE script of the page, the same for every slate.
   It reads ids from data attributes, sets values and classes, and writes no markup.
   It loads nothing and sends nothing. The page's content policy names this text by hash. */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var slateName = body.getAttribute('data-slate');
  var slateDigest = body.getAttribute('data-digest');
  var KEY = 'tamheed-slate:' + slateName + ':' + slateDigest;
  var FORMAT = 'tamheed-slate-answers';
  var statusLine = document.getElementById('status');
  var questions = list('fieldset.question');
  var current = 0;
  var clearArmed = false;

  function list(selector, within) {
    return Array.prototype.slice.call((within || document).querySelectorAll(selector));
  }

  function field(within, name) {
    return within.querySelector('[data-field="' + name + '"]');
  }

  function text(value) {
    return typeof value === 'string' ? value : '';
  }

  function say(message) {
    statusLine.textContent = message;
  }

  /* id -> element, on an object with no prototype, so a hostile id finds no built-in. */
  function byAttribute(selector, attribute) {
    var map = Object.create(null);
    list(selector).forEach(function (el) { map[el.getAttribute(attribute)] = el; });
    return map;
  }

  function collect() {
    var out = {
      format: FORMAT, version: 1, slate: slateName, slate_digest: slateDigest,
      exported_at: new Date().toISOString(), rounds: [], answers: []
    };
    list('section.round').forEach(function (section) {
      out.rounds.push({
        id: section.getAttribute('data-round'),
        attendance: field(section, 'attendance').value,
        closed: field(section, 'closed').checked,
        closed_by: field(section, 'closed_by').value,
        closure_note: field(section, 'closure_note').value
      });
      list('fieldset.question', section).forEach(function (question) {
        var picked = question.querySelector('input[type="radio"]:checked');
        var other = field(question, 'other');
        out.answers.push({
          question: question.getAttribute('data-question'),
          selected: picked ? picked.value : null,
          other: other ? other.value : '',
          note: field(question, 'note').value
        });
      });
    });
    return out;
  }

  function apply(data) {
    var sections = byAttribute('section.round', 'data-round');
    var fieldsets = byAttribute('fieldset.question', 'data-question');
    (Array.isArray(data.rounds) ? data.rounds : []).forEach(function (item) {
      var section = item && sections[item.id];
      if (!section) { return; }
      field(section, 'attendance').value = text(item.attendance);
      field(section, 'closed').checked = item.closed === true;
      field(section, 'closed_by').value = text(item.closed_by);
      field(section, 'closure_note').value = text(item.closure_note);
    });
    (Array.isArray(data.answers) ? data.answers : []).forEach(function (item) {
      var question = item && fieldsets[item.question];
      if (!question) { return; }
      list('input[type="radio"]', question).forEach(function (radio) {
        radio.checked = radio.value === item.selected;
      });
      var other = field(question, 'other');
      if (other) { other.value = text(item.other); }
      field(question, 'note').value = text(item.note);
    });
  }

  function isAnswered(question) {
    var picked = question.querySelector('input[type="radio"]:checked');
    if (!picked) { return false; }
    if (picked.value !== 'other') { return true; }
    return field(question, 'other').value.trim() !== '';
  }

  function show() {
    var answered = 0;
    questions.forEach(function (question, at) {
      var done = isAnswered(question);
      if (done) { answered += 1; }
      question.classList.toggle('answered', done);
      question.classList.toggle('current', at === current);
    });
    list('section.round').forEach(function (section) {
      section.classList.toggle('current-round',
        questions.length > 0 && section.contains(questions[current]));
    });
    document.getElementById('progress').textContent =
      answered + ' of ' + questions.length + ' answered.';
    document.getElementById('position').textContent =
      questions.length ? 'Question ' + (current + 1) + ' of ' + questions.length : '';
    document.getElementById('answers-text').value = JSON.stringify(collect(), null, 1) + '\n';
    document.getElementById('view-all').setAttribute('aria-pressed',
      String(!root.classList.contains('one')));
    document.getElementById('view-one').setAttribute('aria-pressed',
      String(root.classList.contains('one')));
    document.getElementById('audience').setAttribute('aria-pressed',
      String(root.classList.contains('audience')));
  }

  function keep() {
    try {
      localStorage.setItem(KEY, JSON.stringify({
        answers: collect(), one: root.classList.contains('one'),
        audience: root.classList.contains('audience'), current: current
      }));
    } catch (error) {
      say('This browser does not keep the answers between visits. Save them to a file.');
    }
  }

  function restore() {
    var kept = null;
    try { kept = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (error) { kept = null; }
    if (!kept || typeof kept !== 'object') { return; }
    if (kept.answers && typeof kept.answers === 'object') { apply(kept.answers); }
    root.classList.toggle('one', kept.one === true);
    root.classList.toggle('audience', kept.audience === true);
    if (typeof kept.current === 'number' && kept.current >= 0 && kept.current < questions.length) {
      current = Math.floor(kept.current);
    }
  }

  function changed() {
    disarm();
    keep();
    show();
  }

  function move(step) {
    if (!questions.length) { return; }
    current = Math.min(questions.length - 1, Math.max(0, current + step));
    changed();
    questions[current].scrollIntoView({block: 'start'});
  }

  function disarm() {
    clearArmed = false;
    document.getElementById('clear').textContent = 'Clear';
  }

  function saveFile() {
    var content = JSON.stringify(collect(), null, 1) + '\n';
    var link = document.getElementById('download');
    try {
      link.href = URL.createObjectURL(new Blob([content], {type: 'application/json'}));
      link.download = slateName + '.answers.json';
      link.click();
      say('Saved as ' + slateName + '.answers.json. If no file appears, copy the text at the'
        + ' end of this page.');
    } catch (error) {
      say('The download did not start. Copy the text at the end of this page.');
    }
  }

  function loadFile(file) {
    if (!file) { return; }
    file.text().then(function (content) {
      var data = null;
      try { data = JSON.parse(content); } catch (error) { data = null; }
      if (!data || typeof data !== 'object' || data.format !== FORMAT
          || data.slate !== slateName || data.slate_digest !== slateDigest) {
        say('That file is not an answers file of this slate, or it is of another version of'
          + ' it. Nothing was loaded.');
        return;
      }
      apply(data);
      changed();
      say('Loaded ' + file.name + '.');
    }, function () {
      say('That file could not be read. Nothing was loaded.');
    });
  }

  function clearAll() {
    if (!clearArmed) {
      clearArmed = true;
      document.getElementById('clear').textContent = 'Click again to clear every answer';
      return;
    }
    list('input[type="radio"], input[type="checkbox"]').forEach(function (el) {
      el.checked = false;
    });
    list('textarea[data-field], input[type="text"][data-field]').forEach(function (el) {
      el.value = '';
    });
    changed();
    say('Every answer was cleared.');
  }

  function on(id, handler) {
    document.getElementById(id).addEventListener('click', handler);
  }

  document.addEventListener('input', function (event) {
    /* Text typed into the free answer selects it. Without this, an answer that was typed
       and never selected read as no answer. */
    var target = event.target;
    if (target && target.getAttribute && target.getAttribute('data-field') === 'other'
        && target.value.trim() !== '') {
      var radio = target.closest('fieldset').querySelector('input[type="radio"][value="other"]');
      if (radio) { radio.checked = true; }
    }
    changed();
  });
  document.addEventListener('change', function (event) {
    if (event.target && event.target.id === 'load') {
      loadFile(event.target.files[0]);
      event.target.value = '';
      return;
    }
    changed();
  });
  on('view-all', function () { root.classList.remove('one'); changed(); });
  on('view-one', function () { root.classList.add('one'); changed(); });
  on('audience', function () { root.classList.toggle('audience'); changed(); });
  on('save', saveFile);
  on('print', function () { window.print(); });
  on('clear', clearAll);
  on('prev', function () { move(-1); });
  on('next', function () { move(1); });

  restore();
  /* `ready` shows the recommendation. It is set only now, after the stored audience mode
     was applied. So a page that was left in audience mode never paints the pick. A page
     opened for the first time shows it: set audience mode before the screen is shared. */
  root.classList.add('ready');
  show();
}());
