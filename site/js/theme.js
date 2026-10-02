(function () {
  "use strict";
  var KEY = "acity-theme";

  function preferred() {
    try {
      var stored = localStorage.getItem(KEY);
      if (stored === "light" || stored === "dark") return stored;
    } catch (e) {}
    try {
      if (window.matchMedia("(prefers-color-scheme: light)").matches) return "light";
    } catch (e) {}
    return "dark";
  }

  function paint(mode) {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    var light = mode === "light";
    btn.hidden = false;
    btn.setAttribute("aria-pressed", light ? "true" : "false");
    btn.setAttribute("aria-label", light ? "Switch to dark mode" : "Switch to light mode");
  }

  function apply(mode, save) {
    var next = mode === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    if (save) {
      try { localStorage.setItem(KEY, next); } catch (e) {}
    }
    paint(next);
    return next;
  }

  var current = document.documentElement.getAttribute("data-theme");
  if (current !== "light" && current !== "dark") current = preferred();
  apply(current, false);

  var btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.addEventListener("click", function () {
    var now = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
    apply(now === "light" ? "dark" : "light", true);
  });
})();
