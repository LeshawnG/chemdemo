(function () {
  const $ = (id) => document.getElementById(id);
  const stage = $("stage"), labelsEl = $("labels"), info = $("info"), toast = $("toast"), walkEl = $("walk"), chipsEl = $("chips");
  const scrub = $("scrub"), bPlay = $("bPlay"), cntEl = $("cnt");
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  stage.insertBefore(renderer.domElement, labelsEl);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 200);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8892a6, 0.85));
  const dl = new THREE.DirectionalLight(0xffffff, 0.75); dl.position.set(3, 5, 8); scene.add(dl);
  const root = new THREE.Group(); scene.add(root);
  const molG = new THREE.Group(), elG = new THREE.Group(), ghostG = new THREE.Group(); root.add(ghostG); root.add(molG); root.add(elG);
  const sphereGeo = new THREE.SphereGeometry(1, 28, 20), cylGeo = new THREE.CylinderGeometry(1, 1, 1, 14);
  const UP = new THREE.Vector3(0, 1, 0), EZ = new THREE.Vector3(0, 0, 1);

  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function applyTheme() { renderer.setClearColor(new THREE.Color(cssVar("--stage") || "#e9edf3")); }
  applyTheme();
  try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {}
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  // ------------------------------------------------------------ state
  let cur = null, atoms = [], bonds = [], P = [], P0 = [], faceMesh = null, edgeLines = null, R0 = 1;
  let shown = new Set(), labelSpans = [], elLabels = [], showLabels = true, memberIdx = {}, lastCi = -1;
  let anim = null, slow = false, student = false, present = false;
  let net = I3(), valid = true, found = new Map();
  let walk = null; // { i, revealed }

  // ------------------------------------------------------------ 3x3 helpers (molecule frame)
  function I3() { return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]; }
  function mul(A, B) { return A.map((r, i) => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j])); }
  function rotM(v, a) { const [x, y, z] = v, c = Math.cos(a), s = Math.sin(a), t = 1 - c;
    return [[t * x * x + c, t * x * y - s * z, t * x * z + s * y], [t * x * y + s * z, t * y * y + c, t * y * z - s * x], [t * x * z - s * y, t * y * z + s * x, t * z * z + c]]; }
  function refM(v) { const [x, y, z] = v; return [[1 - 2 * x * x, -2 * x * y, -2 * x * z], [-2 * x * y, 1 - 2 * y * y, -2 * y * z], [-2 * x * z, -2 * y * z, 1 - 2 * z * z]]; }
  function opM(cl, v) {
    if (cl.kind === "C") return rotM(v, 2 * Math.PI / cl.n);
    if (cl.kind === "s") return refM(v);
    if (cl.kind === "i") return [[-1, 0, 0], [0, -1, 0], [0, 0, -1]];
    return mul(refM(v), rotM(v, 2 * Math.PI / cl.n));
  }
  function key(M) { return M.flat().map(x => (Math.round(x * 100) / 100 + 0).toFixed(2)).join(","); }
  function v3(a) { return new THREE.Vector3(a[0], a[1], a[2]); }
  function unitArr(a) { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }
  function clear(g) { while (g.children.length) { const c = g.children.pop(); if (c.geometry && c.geometry !== sphereGeo && c.geometry !== cylGeo) c.geometry.dispose(); } }

  function setView(M) {
    const m = new THREE.Matrix4();
    m.set(M[0][0], M[0][1], M[0][2], 0, M[1][0], M[1][1], M[1][2], 0, M[2][0], M[2][1], M[2][2], 0, 0, 0, 0, 1);
    root.quaternion.setFromRotationMatrix(m);
  }
  function fit() {
    const Rb = R0 * 1.4 + 0.45, vf = camera.fov * Math.PI / 180, hf = 2 * Math.atan(Math.tan(vf / 2) * camera.aspect);
    camera.position.set(0, 0, Rb / Math.sin(Math.min(vf, hf) / 2) * 1.12);
  }

  // ------------------------------------------------------------ load a shape
  function load(item) {
    cur = item; clear(molG); clear(elG); clear(ghostG); atoms = []; bonds = []; shown = new Set(); memberIdx = {}; anim = null; lastCi = -1; walk = null;
    P0 = item.atoms.map(a => v3(a.x)); P = P0.map(p => p.clone());
    R0 = Math.max(...P0.map(p => p.length())) || 1;
    for (const a of item.atoms) {
      const m = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: a.c, roughness: 0.55 }));
      m.scale.setScalar(item.poly ? 0.055 * Math.max(1, R0) : a.r * 0.82); molG.add(m); atoms.push(m);
    }
    if (item.poly) {
      const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(item.faces.length * 9), 3));
      faceMesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x9fb3cf, transparent: true, opacity: 0.38, side: THREE.DoubleSide, depthWrite: false }));
      molG.add(faceMesh);
      const lg = new THREE.BufferGeometry(); lg.setAttribute("position", new THREE.BufferAttribute(new Float32Array(item.bonds.length * 6), 3));
      edgeLines = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0x1f2937 })); molG.add(edgeLines);
    } else {
      faceMesh = null; edgeLines = null;
      for (const b of item.bonds) {
        const m = new THREE.Mesh(cylGeo, new THREE.MeshStandardMaterial({ color: 0x3b4252, roughness: 0.6 }));
        molG.add(m); bonds.push({ m, i: b[0], j: b[1], o: b[2] });
      }
    }
    labelsEl.innerHTML = "";
    labelSpans = item.atoms.map(a => { const s = document.createElement("span"); s.innerHTML = a.label; labelsEl.appendChild(s); return s; });
    elLabels = [];
    net = I3(); valid = true; found = new Map([[key(net), "E"]]);
    setView(item.view); fit(); update(); renderInfo(); renderDock(); setScrub(0); setToast(""); renderWalk(); renderCount();
    document.querySelectorAll("#pick button").forEach(b => b.setAttribute("aria-pressed", b.dataset.key === item.key ? "true" : "false"));
    $("shapeSel").value = item.key;
  }

  function update() {
    atoms.forEach((m, k) => m.position.copy(P[k]));
    for (const b of bonds) {
      const a = P[b.i], c = P[b.j], d = new THREE.Vector3().subVectors(c, a), L = d.length();
      b.m.position.copy(a).addScaledVector(d, 0.5);
      b.m.quaternion.setFromUnitVectors(UP, d.clone().normalize());
      const w = b.o > 1 ? 0.085 : 0.06; b.m.scale.set(w, L, w);
    }
    if (faceMesh) {
      const pos = faceMesh.geometry.attributes.position.array; let k = 0;
      for (const f of cur.faces) for (const i of f) { pos[k++] = P[i].x; pos[k++] = P[i].y; pos[k++] = P[i].z; }
      faceMesh.geometry.attributes.position.needsUpdate = true; faceMesh.geometry.computeVertexNormals();
      const lp = edgeLines.geometry.attributes.position.array; k = 0;
      for (const b of cur.bonds) for (const i of [b[0], b[1]]) { lp[k++] = P[i].x; lp[k++] = P[i].y; lp[k++] = P[i].z; }
      edgeLines.geometry.attributes.position.needsUpdate = true;
    }
  }

  // ------------------------------------------------------------ ghosts: where the atoms started this move
  function makeGhosts(start) {
    clear(ghostG);
    start.forEach((p, k) => {
      const a = cur.atoms[k];
      const m = new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: a.c, transparent: true, opacity: cur.poly ? 0.5 : 0.28, depthWrite: false }));
      m.scale.setScalar(cur.poly ? 0.07 * Math.max(1, R0) : a.r * 0.86); m.position.copy(p); ghostG.add(m);
    });
    if (cur.poly) {
      const lp = new Float32Array(cur.bonds.length * 6); let k = 0;
      for (const b of cur.bonds) for (const i of [b[0], b[1]]) { lp[k++] = start[i].x; lp[k++] = start[i].y; lp[k++] = start[i].z; }
      const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(lp, 3));
      ghostG.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0x64748b, transparent: true, opacity: 0.45 })));
    }
  }

  // ------------------------------------------------------------ element geometry
  function elementObject(cl, mi) {
    const g = new THREE.Group(), col = new THREE.Color(cl.color), v = v3(cl.members[mi]).normalize();
    const L = R0 * 1.35 + 0.3;
    if (cl.kind === "C" || cl.kind === "S") {
      const rr = (cl.kind === "S" ? 0.014 : 0.022) * Math.max(1, R0 * 0.8);
      const m = new THREE.Mesh(cylGeo, new THREE.MeshBasicMaterial({ color: col })); m.scale.set(rr, 2 * L, rr);
      m.quaternion.setFromUnitVectors(UP, v); g.add(m);
      if (cl.kind === "S") {
        const disc = new THREE.Mesh(new THREE.CircleGeometry(R0 * 0.75, 48), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false }));
        disc.quaternion.setFromUnitVectors(EZ, v); g.add(disc);
      }
      g.userData.tip = v.clone().multiplyScalar(L + 0.18);
    } else if (cl.kind === "s") {
      const s = 2 * (R0 * 1.15 + 0.25);
      const pl = new THREE.Mesh(new THREE.PlaneGeometry(s, s), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false }));
      const edge = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(s, s)), new THREE.LineBasicMaterial({ color: col, transparent: true, opacity: 0.7 }));
      const q = new THREE.Quaternion().setFromUnitVectors(EZ, v); pl.quaternion.copy(q); edge.quaternion.copy(q); g.add(pl); g.add(edge);
      g.userData.tip = new THREE.Vector3(s / 2, s / 2, 0).applyQuaternion(q);
    } else {
      const m = new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: col })); m.scale.setScalar(0.09); g.add(m);
      g.userData.tip = new THREE.Vector3(0.22, 0.22, 0);
    }
    return g;
  }
  function refreshElements(extra) {
    clear(elG); labelsEl.querySelectorAll(".el").forEach(s => s.remove()); elLabels = [];
    const add = (cl, ci, mi) => {
      const o = elementObject(cl, mi); elG.add(o);
      const s = document.createElement("span"); s.className = "el"; s.style.color = cl.color; s.innerHTML = cl.fake ? "?" : nameOf(ci);
      labelsEl.appendChild(s); elLabels.push({ s, o });
    };
    for (const ci of shown) { const cl = cur.classes[ci]; if (cl.fake) continue; cl.members.forEach((_, mi) => add(cl, ci, mi)); }
    if (extra) add(extra.cl, extra.ci, extra.mi);
  }

  // student mode hides names: elements become "Axis A", "Plane set B" ...
  function nameOf(ci) {
    const cl = cur.classes[ci];
    if (!student || cl.fake) return cl.label;
    const same = cur.classes.filter((c, k) => !c.fake && c.kind === cl.kind && k <= ci).length;
    const L = String.fromCharCode(64 + same);
    return { C: "Axis ", s: "Plane set ", i: "Centre", S: "Turn+reflect axis " }[cl.kind] + (cl.kind === "i" ? "" : L);
  }

  // ------------------------------------------------------------ playing a move
  function posAt(kind, n, v, p, t) {
    if (kind === "C") return p.clone().applyAxisAngle(v, (2 * Math.PI / n) * t);
    if (kind === "s") return p.clone().addScaledVector(v, -2 * t * p.dot(v));
    if (kind === "i") return p.clone().multiplyScalar(1 - 2 * t);
    if (t <= 0.5) return p.clone().applyAxisAngle(v, (2 * Math.PI / n) * (2 * t));
    const q = p.clone().applyAxisAngle(v, 2 * Math.PI / n), s = 2 * (t - 0.5);
    return q.addScaledVector(v, -2 * s * q.dot(v));
  }
  function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  function play(ci) {
    if (anim) {
      if (!anim.done) finish(true);
      else if (anim.t < 1) { const a = anim; P = a.start.map(p => posAt(a.cl.kind, a.cl.n, a.v, p, 1)); update(); }
    }
    const cl = cur.classes[ci];
    const mi = (memberIdx[ci] || 0) % cl.members.length; memberIdx[ci] = mi + 1; lastCi = ci;
    const v = v3(unitArr(cl.members[mi]));
    const start = P.map(p => p.clone()), end = start.map(p => posAt(cl.kind, cl.n, v, p, 1));
    makeGhosts(start);
    const moved = start.map((p, k) => p.distanceTo(end[k]) > 1e-3);
    labelSpans.forEach((s, k) => { s.classList.toggle("mv", moved[k]); s.classList.toggle("st", !moved[k]); });
    anim = { cl, ci, mi, v, start, t: 0, playing: true, done: false, dur: reduce ? 1 : (slow ? 4200 : 1600), last: performance.now() };
    refreshElements({ cl, ci, mi });
    const count = cl.members.length > 1 ? ` (${mi + 1} of ${cl.members.length})` : "";
    setToast(`<b style="color:${cl.color}">${nameOf(ci)}</b>${count} · ${cl.what} …`);
    bPlay.textContent = "❚❚";
  }
  function setT(t) {
    anim.t = Math.max(0, Math.min(1, t));
    const e = ease(anim.t);
    P = anim.start.map(p => posAt(anim.cl.kind, anim.cl.n, anim.v, p, e)); update(); setScrub(anim.t);
    if (anim.t >= 1 && !anim.done) finish(false);
  }
  function finish(silent) {
    const { cl, ci, mi, v, start } = anim;
    anim.done = true; anim.playing = false; anim.t = 1;
    P = start.map(p => posAt(cl.kind, cl.n, v, p, 1)); update(); setScrub(1); bPlay.textContent = "▶";
    refreshElements({ cl, ci, mi });
    const vv = unitArr(cl.members[mi]);
    if (cl.fake) valid = false;
    else { net = mul(opM(cl, vv), net); if (valid && same()) { const k = key(net); if (!found.has(k)) found.set(k, cl.label); } }
    renderCount();
    if (silent) return;
    const count = cl.members.length > 1 ? ` (${mi + 1} of ${cl.members.length})` : "";
    let msg = `<b style="color:${cl.color}">${nameOf(ci)}</b>${count} · ${cl.what}. `;
    if (cl.fake) msg += cl.msg + `<br>Press <b>Put back</b> to carry on counting.`;
    else {
      if (cl.moves[mi]) msg += `<br><b>Moves:</b> ${cl.moves[mi]}`;
      msg += same() ? `<br><span class="ok">✓ Every atom landed on an identical atom: a symmetry operation.</span>` : `<br><span class="no">Arrangement changed.</span>`;
      if (cl.kind === "C" && cl.n === 4) msg += ` Press again: two 90° turns make the C<sub>2</sub> on the same line.`;
      if (cl.kind === "C" && cl.n === 3) msg += ` Press again for the 240° turn (C<sub>3</sub><sup>2</sup>).`;
    }
    setToast(msg); showRead(msg);
  }
  function same() { return P.every((q, k) => cur.atoms.some((a) => a.s === cur.atoms[k].s && q.distanceTo(v3(a.x)) < 1e-3 * Math.max(1, R0))); }

  function putBack() {
    if (anim && !anim.done) finish(true);
    anim = null; P = P0.map(p => p.clone()); update(); clear(ghostG); net = I3(); valid = true; memberIdx = {};
    labelSpans.forEach(s => s.classList.remove("mv", "st")); setScrub(0); setToast(""); showRead(""); renderCount();
  }
  function setScrub(t) { scrub.value = String(Math.round(t * 1000)); }
  scrub.addEventListener("input", () => { if (!anim) return; anim.playing = false; bPlay.textContent = "▶"; setT(+scrub.value / 1000); });
  bPlay.addEventListener("click", togglePlay);
  function togglePlay() {
    if (anim && !anim.done) { anim.playing = !anim.playing; anim.last = performance.now(); bPlay.textContent = anim.playing ? "❚❚" : "▶"; return; }
    const ci = lastCi >= 0 ? lastCi : cur.classes.findIndex(c => !c.fake);
    if (ci >= 0) play(ci);
  }
  $("bSlow").addEventListener("click", (e) => { slow = !slow; e.currentTarget.setAttribute("aria-pressed", slow ? "true" : "false");
    if (anim && !anim.done) anim.dur = slow ? 4200 : 1600; });
  $("bBack2").addEventListener("click", putBack);

  // ------------------------------------------------------------ counter
  function renderCount() {
    if (!cur) return;
    const k = found.size, n = cur.order;
    cntEl.classList.toggle("all", k === n);
    cntEl.innerHTML = n === 1 ? `Only E: <b>1</b> move` : student ? `Moves found: <b>${k}</b>` : (k === n ? `All <b>${n}</b> moves found ✓` : `Moves found: <b>${k}</b> of ${n}`);
    const d = $("cntInfo");
    if (d) d.innerHTML = cntEl.innerHTML + (valid ? "" : ` <span class="no">· put the atoms back to keep counting</span>`);
  }

  // ------------------------------------------------------------ chart walk-through
  function renderWalk() {
    if (!walk) { walkEl.hidden = true; return; }
    const steps = cur.walk, s = steps[walk.i];
    let h = `<div class="wq">Step ${walk.i + 1} of ${steps.length} · ${s.end ? "Point group" : s.q}</div>`;
    if (walk.revealed) {
      h += s.end ? `<div class="wa"><span class="res">${s.a}</span> ${s.detail || ""}</div>`
                 : `<div class="wa"><b>${s.a}</b>${s.detail ? ` <span class="wd">${s.detail}</span>` : ""}</div>`;
    }
    const done = steps.slice(0, walk.i).filter(x => !x.end);
    if (done.length) h += `<div class="wp">` + done.map(x => `<span>${x.q.replace(/^\d · /, "")} <b class="${/^Yes/.test(x.a) ? "y" : "n"}">${x.a}</b></span>`).join("") + `</div>`;
    h += `<div class="wb"><button type="button" id="wBack">Back</button>` +
         (walk.revealed ? (walk.i < steps.length - 1 ? `<button type="button" id="wNext" aria-pressed="true">Next question</button>` : "")
                        : `<button type="button" id="wShow" aria-pressed="true">${s.end ? "Show result" : "Show answer"}</button>`) +
         `<button type="button" id="wExit">Close</button></div>`;
    walkEl.innerHTML = h; walkEl.hidden = false; setToast("");
    $("wBack").addEventListener("click", () => { if (walk.i > 0) { walk.i--; walk.revealed = true; applyWalkShow(); renderWalk(); } });
    const ns = $("wShow"); if (ns) ns.addEventListener("click", () => { walk.revealed = true; applyWalkShow(); renderWalk(); });
    const nx = $("wNext"); if (nx) nx.addEventListener("click", () => { walk.i++; walk.revealed = false; shown = new Set(); refreshElements(); syncShowButtons(); renderWalk(); });
    $("wExit").addEventListener("click", stopWalk);
  }
  function applyWalkShow() { shown = new Set(cur.walk[walk.i].show); refreshElements(); syncShowButtons(); }
  function startWalk() { walk = { i: 0, revealed: false }; shown = new Set(); refreshElements(); syncShowButtons(); renderWalk(); }
  function stopWalk() { walk = null; renderWalk(); }

  // ------------------------------------------------------------ panels
  function setToast(html) { toast.hidden = !html; toast.innerHTML = html; }
  function showRead(html) { const r = $("read"); if (r) r.innerHTML = html || "Press ▶ next to an element to watch its move. Labels travel with the atoms: blue = moved, green ring = stayed put."; }
  function syncShowButtons() { info.querySelectorAll("[data-show]").forEach(b => b.setAttribute("aria-pressed", shown.has(+b.dataset.show) ? "true" : "false")); }

  function renderDock() {
    chipsEl.innerHTML = "";
    const w = document.createElement("button"); w.type = "button"; w.textContent = "Walk the chart"; w.addEventListener("click", () => walk ? stopWalk() : startWalk());
    chipsEl.appendChild(w);
    const all = document.createElement("button"); all.type = "button"; all.textContent = "All elements"; all.id = "dockAll";
    all.setAttribute("aria-pressed", "false"); all.addEventListener("click", toggleAll); chipsEl.appendChild(all);
    cur.classes.forEach((cl, ci) => {
      const b = document.createElement("button"); b.type = "button"; if (cl.fake) b.className = "fake";
      b.innerHTML = `▶ ${cl.fake ? cl.label : nameOf(ci)}`; if (!cl.fake) b.style.borderColor = cl.color;
      b.addEventListener("click", () => play(ci)); chipsEl.appendChild(b);
    });
  }
  function toggleAll() {
    const on = shown.size === 0; shown = new Set(); if (on) cur.classes.forEach((c, ci) => { if (!c.fake) shown.add(ci); });
    refreshElements(); syncShowButtons();
    document.querySelectorAll("#dockAll, #bAll").forEach(b => b.setAttribute("aria-pressed", on ? "true" : "false"));
  }

  function renderInfo() {
    const it = cur, real = it.classes.filter(c => !c.fake);
    let h = `<div class="ttl"><div><div class="part">${it.part}</div><h3>${it.title}</h3></div>` +
            `<div class="badge ans"><b>${it.pg}</b><span>order ${it.order}</span></div>` +
            `<button type="button" class="reveal" id="bReveal">Reveal answers</button></div>`;
    h += `<div class="sheet ans"><div class="k">On the sheet: symmetry elements</div><div class="v">${it.sheet}</div></div>`;
    h += `<div class="note ans">${it.note}</div>`;
    h += `<div class="els">`;
    if (!real.length) h += `<div class="note">Only E: nothing to show. Try the dashed moves to see why.</div>`;
    it.classes.forEach((cl, ci) => {
      const n = cl.members.length;
      h += `<div class="row${cl.fake ? " fake" : ""}"><span class="sw" style="background:${cl.color}"></span>` +
           `<span class="nm" style="color:${cl.fake ? "var(--muted)" : cl.color}">${cl.fake ? cl.label : nameOf(ci)}${n > 1 ? ` <span class="ct">× ${n}</span>` : ""}</span>` +
           (cl.fake ? `<span></span>` : `<button type="button" data-show="${ci}" aria-pressed="false">Show</button>`) +
           `<button type="button" data-play="${ci}">▶ Play</button></div>`;
    });
    h += `</div><div class="read" id="read"></div><div class="note" id="cntInfo"></div>`;
    h += `<div class="foot"><button type="button" id="bBack">Put atoms back</button><button type="button" id="bAll" aria-pressed="false">Show all elements</button>` +
         `<button type="button" id="bWalk">Walk the chart</button></div>`;
    h += `<div class="keys">Keys: <kbd>Space</kbd> play/pause · <kbd>N</kbd> next element · <kbd>R</kbd> put back · <kbd>W</kbd> chart · <kbd>D</kbd> down axis · <kbd>V</kbd> reset view · <kbd>P</kbd> present · <kbd>S</kbd> student</div>`;
    info.innerHTML = h; showRead(""); renderCount();
    info.querySelectorAll("[data-show]").forEach(b => b.addEventListener("click", () => {
      const ci = +b.dataset.show; if (shown.has(ci)) shown.delete(ci); else shown.add(ci); syncShowButtons(); refreshElements();
    }));
    info.querySelectorAll("[data-play]").forEach(b => b.addEventListener("click", () => play(+b.dataset.play)));
    $("bBack").addEventListener("click", putBack);
    $("bAll").addEventListener("click", toggleAll);
    $("bWalk").addEventListener("click", () => walk ? stopWalk() : startWalk());
    $("bReveal").addEventListener("click", () => setStudent(false));
  }

  function setStudent(on) {
    student = on; document.body.classList.toggle("student-on", on); $("bStudent").setAttribute("aria-pressed", on ? "true" : "false");
    document.querySelectorAll("#pick .g").forEach(g => g.hidden = on);
    if (cur) { renderInfo(); renderDock(); refreshElements(); syncShowButtons(); }
  }
  function setPresent(on) {
    present = on; document.documentElement.classList.toggle("present", on); $("bPresent").setAttribute("aria-pressed", on ? "true" : "false");
    $("bPresent").textContent = on ? "Exit present" : "Present";
    requestAnimationFrame(resize);
  }

  // ------------------------------------------------------------ shape pickers
  const pick = $("pick"), sel = $("shapeSel");
  for (const part of ["Part 2", "Part 3", "Part 1"]) {
    const g = document.createElement("div"); g.className = "grp"; g.innerHTML = `<h2>${part}</h2>`;
    const og = document.createElement("optgroup"); og.label = part;
    for (const it of DATA.filter(d => d.part === part)) {
      const b = document.createElement("button"); b.type = "button"; b.dataset.key = it.key; b.setAttribute("aria-pressed", "false");
      b.innerHTML = `<span>${it.title}</span><span class="g">${it.pg}</span>`; b.addEventListener("click", () => load(it)); g.appendChild(b);
      const o = document.createElement("option"); o.value = it.key; o.textContent = it.title; og.appendChild(o);
    }
    pick.appendChild(g); sel.appendChild(og);
  }
  sel.addEventListener("change", () => load(DATA.find(d => d.key === sel.value)));

  // ------------------------------------------------------------ view controls
  $("bReset").addEventListener("click", () => { setView(cur.view); fit(); });
  function downAxis() {
    if (!cur.principal) { setToast("No rotation axis: nothing to look down."); return; }
    root.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(v3(unitArr(cur.principal)), EZ));
  }
  $("bDown").addEventListener("click", downAxis);
  $("bLabels").addEventListener("click", (e) => { showLabels = !showLabels; e.currentTarget.setAttribute("aria-pressed", showLabels ? "true" : "false"); labelsEl.hidden = !showLabels; });
  $("bStudent").addEventListener("click", () => setStudent(!student));
  $("bPresent").addEventListener("click", () => setPresent(!present));

  const ptrs = new Map(); let pinch0 = 0, camZ0 = 9;
  stage.addEventListener("pointerdown", (e) => {
    if (e.target.closest("button, input, .walk, .toast")) return;
    stage.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = Math.hypot(a.x - b.x, a.y - b.y); camZ0 = camera.position.z; }
  });
  stage.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return; const prev = ptrs.get(e.pointerId); const dx = e.clientX - prev.x, dy = e.clientY - prev.y;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 1) {
      root.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(UP, dx * 0.008)).premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), dy * 0.008));
    } else if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch0 > 0) camera.position.z = Math.min(60, Math.max(3, camZ0 * pinch0 / d));
    }
  });
  const endPtr = (e) => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = 0; };
  stage.addEventListener("pointerup", endPtr); stage.addEventListener("pointercancel", endPtr);
  stage.addEventListener("wheel", (e) => { e.preventDefault(); camera.position.z = Math.min(60, Math.max(3, camera.position.z * (1 + e.deltaY * 0.001))); }, { passive: false });

  document.addEventListener("keydown", (e) => {
    if (e.target.closest && e.target.closest("input, select, textarea")) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key.toLowerCase();
    if (k === " ") { e.preventDefault(); togglePlay(); }
    else if (k === "n") { const real = cur.classes.map((c, i) => i); const nxt = real[(lastCi + 1) % real.length]; play(nxt); }
    else if (k === "r") putBack();
    else if (k === "w") { if (!walk) startWalk(); else if (!walk.revealed) { walk.revealed = true; applyWalkShow(); renderWalk(); }
                          else if (walk.i < cur.walk.length - 1) { walk.i++; walk.revealed = false; shown = new Set(); refreshElements(); syncShowButtons(); renderWalk(); } }
    else if (k === "d") downAxis();
    else if (k === "v") { setView(cur.view); fit(); }
    else if (k === "p") setPresent(!present);
    else if (k === "s") setStudent(!student);
    else if (k === "escape") { if (walk) stopWalk(); else if (present) setPresent(false); }
  });

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(1, h); camera.updateProjectionMatrix(); if (cur) fit();
  }
  new ResizeObserver(resize).observe(stage);

  const tmp = new THREE.Vector3();
  function placeLabels() {
    if (!showLabels) return;
    const w = stage.clientWidth, h = stage.clientHeight;
    const proj = (v) => { tmp.copy(v).applyQuaternion(root.quaternion).project(camera); return [(tmp.x + 1) / 2 * w, (1 - tmp.y) / 2 * h]; };
    labelSpans.forEach((s, k) => {
      const p = P[k].clone();
      if (cur.poly) { const dir = p.length() > 1e-6 ? p.clone().normalize() : UP.clone(); p.addScaledVector(dir, 0.16 * Math.max(1, R0)); }
      const [x, y] = proj(p); s.style.left = x + "px"; s.style.top = y + "px"; s.style.fontSize = cur.poly ? "13px" : "11px";
    });
    for (const { s, o } of elLabels) { const [x, y] = proj(o.userData.tip); s.style.left = x + "px"; s.style.top = y + "px"; }
  }
  function loop(now) {
    if (anim && anim.playing && !anim.done) { const dt = now - anim.last; anim.last = now; setT(anim.t + dt / anim.dur); }
    renderer.render(scene, camera); placeLabels(); requestAnimationFrame(loop);
  }
  resize(); load(DATA[1]); requestAnimationFrame(loop);
})();
