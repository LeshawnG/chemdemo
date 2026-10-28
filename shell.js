// ============================================================ shell: tabs, student mode, present
(function () {
  const $ = (id) => document.getElementById(id);
  const TABS = { "symmetry": ["p1", window.P1], "unit-cells": ["p2", window.P2], "lattices": ["p3", window.P3] };
  let student = false, present = false, tab = "symmetry";
  function show(name) {
    if (!TABS[name]) name = "symmetry"; tab = name;
    for (const [k, [pid, api]] of Object.entries(TABS)) {
      const on = k === name; $(pid).hidden = !on; $("t-" + k).setAttribute("aria-selected", on ? "true" : "false");
      if (api) api.setActive(false);
    }
    requestAnimationFrame(() => { const api = TABS[name][1]; if (api) api.setActive(true); });
    if (location.hash !== "#" + name) { try { history.replaceState(null, "", "#" + name); } catch (e) { location.hash = name; } }
    try { localStorage.setItem("lab3-tab", name); } catch (e) {}
  }
  document.querySelectorAll(".tabs button").forEach(b => b.addEventListener("click", () => show(b.dataset.tab)));
  window.addEventListener("hashchange", () => show(location.hash.slice(1)));
  $("bStudent").addEventListener("click", () => {
    student = !document.body.classList.contains("student-on"); document.body.classList.toggle("student-on", student); $("bStudent").setAttribute("aria-pressed", student ? "true" : "false");
    if (window.P1) window.P1.setStudent(student); if (window.P2) window.P2.refresh(); if (window.P3) window.P3.refresh();
  });
  $("bPresent").addEventListener("click", () => {
    present = !present; document.documentElement.classList.toggle("present", present); $("bPresent").setAttribute("aria-pressed", present ? "true" : "false");
    $("bPresent").textContent = present ? "Exit present" : "Present";
    requestAnimationFrame(() => { const api = TABS[tab][1]; if (api) { api.setActive(false); api.setActive(true); } });
  });
  let start = location.hash.slice(1);
  if (!TABS[start]) { try { start = localStorage.getItem("lab3-tab") || "symmetry"; } catch (e) { start = "symmetry"; } }
  show(start);
})();
