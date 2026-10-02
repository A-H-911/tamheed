/* Tamheed user guide — page script (inlined). Everything degrades: without JS the page is
   English, LTR, system theme, diagrams in their end state, registers closed. */
(function () {
  "use strict";
  var KEY = "tamheed-guide";
  var root = document.documentElement;
  root.classList.add("js");
  var tocDetails = document.querySelector("nav.toc details");
  if (tocDetails && window.innerWidth < 960) tocDetails.open = false;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function save(patch) {
    try { var s = load(); for (var k in patch) s[k] = patch[k]; localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* storage unavailable */ }
  }

  // ---- language -------------------------------------------------------------
  function setLang(lang, persist) {
    root.lang = lang;
    root.dir = lang === "ar" ? "rtl" : "ltr";
    var t = document.querySelector("title");
    if (t) t.textContent = t.getAttribute("data-" + lang) || t.textContent;
    document.querySelectorAll("[data-lang-btn]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang-btn") === lang ? "true" : "false");
    });
    if (persist) save({ lang: lang });
    document.querySelectorAll("svg.dia.in").forEach(function (s) { s.classList.remove("in"); });
    requestAnimationFrame(observeDiagrams);
  }
  document.querySelectorAll("[data-lang-btn]").forEach(function (b) {
    b.addEventListener("click", function () { setLang(b.getAttribute("data-lang-btn"), true); });
  });

  // ---- theme ----------------------------------------------------------------
  function setTheme(theme, persist) {
    if (theme === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", theme);
    document.querySelectorAll("[data-theme-btn]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-theme-btn") === theme ? "true" : "false");
    });
    if (persist) save({ theme: theme });
  }
  document.querySelectorAll("[data-theme-btn]").forEach(function (b) {
    b.addEventListener("click", function () { setTheme(b.getAttribute("data-theme-btn"), true); });
  });
  setTheme(root.getAttribute("data-theme") || "system", false);
  setLang(root.lang || "en", false);

  // ---- section list highlight ----------------------------------------------
  var links = Array.prototype.slice.call(document.querySelectorAll("nav.toc a[href^='#']"));
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  if ("IntersectionObserver" in window && links.length) {
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && byId[e.target.id]) {
          if (current) current.classList.remove("active");
          current = byId[e.target.id]; current.classList.add("active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    document.querySelectorAll("section.sec[id]").forEach(function (s) { io.observe(s); });
  }

  // ---- diagrams: draw-in on view, dim-on-click, steps -----------------------
  function observeDiagrams() {
    var dias = document.querySelectorAll("svg.dia");
    if (reduce || !("IntersectionObserver" in window)) { dias.forEach(function (s) { s.classList.add("in"); }); return; }
    var io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io2.unobserve(e.target); } });
    }, { threshold: 0.25 });
    dias.forEach(function (s) { if (!s.classList.contains("in")) io2.observe(s); });
  }
  observeDiagrams();

  // click a keyed element: highlight every element with the same key (in both language copies)
  document.querySelectorAll("figure[data-isolate]").forEach(function (fig) {
    fig.addEventListener("click", function (ev) {
      var el = ev.target.closest("[data-key]");
      var svgs = fig.querySelectorAll("svg.dia");
      if (!el) { svgs.forEach(function (s) { s.classList.remove("dim"); s.querySelectorAll("[data-active]").forEach(function (x) { x.removeAttribute("data-active"); }); }); return; }
      var key = el.getAttribute("data-key");
      var group = el.getAttribute("data-group") || "";
      svgs.forEach(function (s) {
        s.classList.add("dim");
        s.querySelectorAll("[data-active]").forEach(function (x) { x.removeAttribute("data-active"); });
        s.querySelectorAll("[data-key='" + key + "']").forEach(function (x) { x.setAttribute("data-active", ""); });
        if (group) s.querySelectorAll("[data-group~='" + key + "']").forEach(function (x) { x.setAttribute("data-active", ""); });
        s.querySelectorAll("[data-links~='" + key + "']").forEach(function (x) { x.setAttribute("data-active", ""); });
      });
      var detail = fig.querySelector(".stage-detail");
      if (detail) {
        var src = fig.querySelector("[data-detail='" + key + "']");
        detail.innerHTML = src ? src.innerHTML : "";
      }
    });
  });

  // step controls: show steps up to the pressed one
  document.querySelectorAll(".steps").forEach(function (bar) {
    var btns = Array.prototype.slice.call(bar.querySelectorAll("button[data-step]"));
    var fig = bar.closest("figure");
    function show(n) {
      btns.forEach(function (b) { b.setAttribute("aria-pressed", parseInt(b.getAttribute("data-step"), 10) === n ? "true" : "false"); });
      fig.querySelectorAll("svg.dia .step").forEach(function (el) {
        var k = parseInt(el.getAttribute("data-step"), 10);
        if (k <= n) el.setAttribute("data-on", ""); else el.removeAttribute("data-on");
      });
      var detail = fig.querySelector(".stage-detail");
      if (detail) { var src = fig.querySelector("[data-detail='s" + n + "']"); detail.innerHTML = src ? src.innerHTML : ""; }
    }
    btns.forEach(function (b) { b.addEventListener("click", function () { show(parseInt(b.getAttribute("data-step"), 10)); }); });
    if (reduce) show(btns.length); else show(1);
  });

  // keyboard on the stage track: arrows move the pressed step
  document.querySelectorAll(".steps[data-keys]").forEach(function (bar) {
    bar.addEventListener("keydown", function (ev) {
      if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
      var btns = Array.prototype.slice.call(bar.querySelectorAll("button[data-step]"));
      var i = btns.findIndex(function (b) { return b.getAttribute("aria-pressed") === "true"; });
      var fwd = (ev.key === "ArrowRight") !== (root.dir === "rtl");
      var j = Math.min(btns.length - 1, Math.max(0, i + (fwd ? 1 : -1)));
      btns[j].click(); btns[j].focus(); ev.preventDefault();
    });
  });

  // ---- family explorer: class filter + search --------------------------------
  var famChips = document.querySelectorAll("#fam-filter button.chip");
  var search = document.getElementById("fam-search");
  function applyFamFilter() {
    var cls = null;
    famChips.forEach(function (b) { if (b.getAttribute("aria-pressed") === "true") cls = b.getAttribute("data-class"); });
    var q = (search && search.value || "").trim().toLowerCase();
    document.querySelectorAll("details.fam").forEach(function (d) {
      var okClass = !cls || cls === "all" || d.getAttribute("data-class") === cls;
      var hay = (d.getAttribute("data-search") || "").toLowerCase();
      var okText = !q || hay.indexOf(q) !== -1;
      d.hidden = !(okClass && okText);
    });
  }
  famChips.forEach(function (b) {
    b.addEventListener("click", function () {
      famChips.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      applyFamFilter();
    });
  });
  if (search) search.addEventListener("input", applyFamFilter);

  // ---- copy buttons on command blocks --------------------------------------
  document.querySelectorAll("pre[data-copy]").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy"; btn.type = "button";
    var en = document.createElement("span"); en.lang = "en"; en.textContent = "Copy";
    var ar = document.createElement("span"); ar.lang = "ar"; ar.textContent = "نسخ";
    btn.appendChild(en); btn.appendChild(ar);
    btn.addEventListener("click", function () {
      var text = pre.querySelector("code").textContent;
      function done() { en.textContent = "Copied"; ar.textContent = "تم النسخ"; setTimeout(function () { en.textContent = "Copy"; ar.textContent = "نسخ"; }, 1500); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { selectText(pre); });
      else selectText(pre);
    });
    pre.appendChild(btn);
  });
  function selectText(el) {
    var r = document.createRange(); r.selectNodeContents(el.querySelector("code"));
    var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
  }

  // open the <details> that an anchor points into
  function openTarget() {
    var id = location.hash.slice(1);
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var d = el.closest("details");
    while (d) { d.open = true; d = d.parentElement && d.parentElement.closest("details"); }
    if (el.tagName === "DETAILS") el.open = true;
  }
  window.addEventListener("hashchange", openTarget);
  openTarget();
})();
