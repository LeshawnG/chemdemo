// ============================================================ PART 2 · BCC and FCC unit cells, density
(function () {
  const $ = (id) => document.getElementById(id);
  const stage = $("cStage"), labelsEl = $("cLabelsEl"), info = $("cInfo"), toast = $("cToast"), chipsEl = $("cChips");
  let active = false, student = false;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.localClippingEnabled = true;
  stage.insertBefore(renderer.domElement, labelsEl);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 400);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8892a6, 0.85));
  const dl = new THREE.DirectionalLight(0xffffff, 0.75); dl.position.set(4, 7, 9); scene.add(dl);
  const root = new THREE.Group(); scene.add(root);
  const sphereGeo = new THREE.SphereGeometry(1, 40, 28), cylGeo = new THREE.CylinderGeometry(1, 1, 1, 14);
  const UP = new THREE.Vector3(0, 1, 0);
  const S = 4;
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  let built = false;
  function applyTheme() { renderer.setClearColor(new THREE.Color(cssVar("--stage") || "#e9edf3")); if (built) build(); }
  try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {}
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  const W = (f) => new THREE.Vector3((f[0] - 0.5) * S, (f[2] - 0.5) * S, -(f[1] - 0.5) * S);
  let kind = "bcc", style = "small", focus = null, mistake = false, metal = "Cu";
  const custom = { r: 124.9, A: 52.00, rho: 7.19 };
  const METALS = { Cu: { name: "Copper", r: 128, A: 63.55, rho: 8.93 }, W: { name: "Tungsten", r: 137.1, A: 183.84, rho: 19.25 } };
  const NA = 6.022e23;

  function sites() {
    const out = [];
    for (const i of [0, 1]) for (const j of [0, 1]) for (const k of [0, 1]) out.push({ f: [i, j, k], site: "corner" });
    if (kind === "bcc") out.push({ f: [.5, .5, .5], site: "body" });
    else for (const f of [[.5, .5, 0], [.5, .5, 1], [.5, 0, .5], [.5, 1, .5], [0, .5, .5], [1, .5, .5]]) out.push({ f, site: "face" });
    return out;
  }
  const LINE = () => kind === "bcc" ? [[0, 0, 0], [1, 1, 1]] : [[0, 0, 0], [1, 0, 1]];
  const onLine = (f) => { const [p, q] = LINE(); const d = [q[0] - p[0], q[1] - p[1], q[2] - p[2]]; const t = (f[0] * d[0] + f[1] * d[1] + f[2] * d[2]) / (d[0] * d[0] + d[1] * d[1] + d[2] * d[2]); return Math.hypot(f[0] - t * d[0], f[1] - t * d[1], f[2] - t * d[2]) < 1e-6; };
  const rHard = () => kind === "bcc" ? Math.sqrt(3) / 4 * S : Math.SQRT2 / 4 * S;

  const atomG = new THREE.Group(), cellG = new THREE.Group(), extraG = new THREE.Group();
  root.add(cellG, atomG, extraG);
  function clear(g) { while (g.children.length) { const c = g.children.pop(); if (c.geometry && c.geometry !== sphereGeo && c.geometry !== cylGeo) c.geometry.dispose(); } }
  let spans = [];
  function label(f, txt, cls) { const sp = document.createElement("span"); sp.innerHTML = txt; if (cls) sp.className = cls; labelsEl.appendChild(sp); spans.push({ sp, f }); }
  function stick(p, q, w, color, op) {
    const m = new THREE.Mesh(cylGeo, new THREE.MeshStandardMaterial({ color, roughness: 0.6, transparent: op < 1, opacity: op })); const d = new THREE.Vector3().subVectors(q, p), L = d.length();
    m.position.copy(p).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(UP, d.normalize()); m.scale.set(w, L, w); extraG.add(m);
  }
  function planes() {
    const h = S / 2 + 0.002;
    return [new THREE.Plane(new THREE.Vector3(1, 0, 0), h), new THREE.Plane(new THREE.Vector3(-1, 0, 0), h), new THREE.Plane(new THREE.Vector3(0, 1, 0), h),
            new THREE.Plane(new THREE.Vector3(0, -1, 0), h), new THREE.Plane(new THREE.Vector3(0, 0, 1), h), new THREE.Plane(new THREE.Vector3(0, 0, -1), h)];
  }
  function quad(fs, color, op) {
    const v = fs.map(W); const g = new THREE.BufferGeometry().setFromPoints([v[0], v[1], v[2], v[0], v[2], v[3]]); g.computeVertexNormals();
    extraG.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color, transparent: true, opacity: op, side: THREE.DoubleSide, depthWrite: false })));
    const e = new THREE.BufferGeometry().setFromPoints([v[0], v[1], v[1], v[2], v[2], v[3], v[3], v[0]]);
    extraG.add(new THREE.LineSegments(e, new THREE.LineBasicMaterial({ color })));
  }

  function build() {
    built = true;
    clear(atomG); clear(cellG); clear(extraG); labelsEl.innerHTML = ""; spans = [];
    const list = sites(), cut = style === "cut" && !mistake, hard = (style !== "small") || mistake;
    const clip = cut ? planes() : [];
    // cell edges
    const pts = []; for (const a of [0, 1]) for (const b of [0, 1]) { pts.push([0, a, b], [1, a, b], [a, 0, b], [a, 1, b], [a, b, 0], [a, b, 1]); }
    const arr = new Float32Array(pts.length * 3); pts.forEach((p, i) => { const v = W(p); arr.set([v.x, v.y, v.z], i * 3); });
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
    cellG.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: new THREE.Color(cssVar("--ink") || "#121826"), transparent: true, opacity: hard ? 0.6 : 0.35 })));
    const lineFocus = focus === "line" || focus === "pyth";
    list.forEach((s) => {
      const isCorner = s.site === "corner";
      const base = new THREE.Color(cssVar(isCorner ? "--cu" : "--ctr") || (isCorner ? "#c8743f" : "#4865b0"));
      const colr = mistake && !isCorner ? new THREE.Color(cssVar("--bad") || "#b42318") : base;
      const dim = lineFocus && !onLine(s.f);
      const r = mistake ? S / 2 : hard ? rHard() : (isCorner ? 0.3 : 0.34);
      const op = dim ? (hard ? 0.08 : 0.18) : (mistake ? 0.55 : 1);
      const m = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: colr, roughness: 0.42, metalness: 0.05, clippingPlanes: clip, transparent: op < 1, opacity: op, depthWrite: op >= 1 }));
      m.scale.setScalar(r); m.position.copy(W(s.f)); atomG.add(m);
      if (cut && !dim) { const b = new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: base.clone().multiplyScalar(0.55), side: THREE.BackSide, clippingPlanes: clip })); b.scale.setScalar(r * 0.999); b.position.copy(m.position); atomG.add(b); }
      if (focus === "shares") label(s.f, isCorner ? "⅛" : s.site === "face" ? "½" : "1", "fr");
    });
    const green = new THREE.Color(cssVar("--good") || "#15803d"), amber = new THREE.Color(cssVar("--warn") || "#b45309");
    if (lineFocus) {
      const [p, q] = LINE(); stick(W(p), W(q), 0.06, green, 1);
      const at = (t) => [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t];
      if (focus === "line") {
        label(at(0.125), "r", "dg"); label(at(0.5), "2r", "dg"); label(at(0.875), "r", "dg");
        for (const t of [0.25, 0.75]) { const m = new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: green })); m.scale.setScalar(0.09); m.position.copy(W(at(t))); extraG.add(m); }
      } else {
        if (kind === "bcc") { stick(W([0, 0, 0]), W([1, 1, 0]), 0.045, amber, 1); stick(W([1, 1, 0]), W([1, 1, 1]), 0.045, amber, 1); label([.5, .5, -0.08], "a√2", "dg"); label([1.08, 1.08, .5], "a", "dg"); label([.42, .42, .6], "√3 a = 4r", "dg"); }
        else { stick(W([0, 0, 0]), W([1, 0, 0]), 0.045, amber, 1); stick(W([1, 0, 0]), W([1, 0, 1]), 0.045, amber, 1); label([.5, 0, -0.1], "a", "dg"); label([1.1, 0, .5], "a", "dg"); label([.4, 0, .62], "√2 a = 4r", "dg"); }
      }
    }
    if (focus === "slice") quad(kind === "bcc" ? [[0, 0, 0], [1, 1, 0], [1, 1, 1], [0, 0, 1]] : [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]], green, 0.16);
    syncControls(); renderChips(); renderInfo(); setToast(toastFor()); placeLabels();
  }

  function toastFor() {
    const b = kind === "bcc";
    if (mistake) return `<span class="no">a = 2r doesn't work here.</span> Corners touching along the edge leaves the ${b ? "centre atom" : "face atoms"} overlapping the corners (red). a = 2r is <b>simple cubic</b>. In ${b ? "BCC" : "FCC"} the atoms touch along the ${b ? "body" : "face"} diagonal.`;
    if (focus === "line") return b ? `<b>Body diagonal</b> = r + 2r + r = <b>4r</b>. It is also √3 a, so <b>a = 4r/√3</b>.` : `<b>Face diagonal</b> = r + 2r + r = <b>4r</b>. It is also √2 a, so <b>a = 2√2 r</b>.`;
    if (focus === "pyth") return b ? `Face diagonal a√2 (amber), then up one edge a: (body diagonal)² = (a√2)² + a² = 3a², so body diagonal = √3 a.` : `Two edges a (amber): (face diagonal)² = a² + a² = 2a², so face diagonal = √2 a.`;
    if (focus === "shares") return b ? `Corners 8 × ⅛ = 1, centre 1: <b>n = 2 atoms</b> per cell.` : `Corners 8 × ⅛ = 1, faces 6 × ½ = 3: <b>n = 4 atoms</b> per cell.`;
    if (focus === "slice") return b ? `The slice through two opposite edges holds the body diagonal: an a × a√2 rectangle. Draw this for 2.1: the labels are easy to place.` : `One face of the cube holds the touching line: an a × a square with the face-centre atom in the middle.`;
    if (style === "cut") return `Each atom is cut where the cell ends: you see exactly the share inside this cell.`;
    return "";
  }
  function setToast(h) { toast.hidden = !h; toast.innerHTML = h || ""; }

  function renderChips() {
    chipsEl.innerHTML = "";
    const L = [["line", "Touching line"], ["pyth", "Pythagoras"], ["shares", "Shares"], ["slice", "Slice for 2.1"]];
    for (const [k, t] of L) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = t; b.setAttribute("aria-pressed", focus === k && !mistake ? "true" : "false");
      b.addEventListener("click", () => { focus = focus === k ? null : k; mistake = false; build(); }); chipsEl.appendChild(b);
    }
    const mb = document.createElement("button"); mb.type = "button"; mb.className = "fake"; mb.textContent = "a = 2r?"; mb.setAttribute("aria-pressed", mistake ? "true" : "false");
    mb.addEventListener("click", () => { mistake = !mistake; build(); }); chipsEl.appendChild(mb);
  }
  function syncControls() {
    document.querySelectorAll("#cStruct button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === kind ? "true" : "false"));
    document.querySelectorAll("#cStyle button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === style ? "true" : "false"));
  }
  document.querySelectorAll("#cStruct button").forEach(b => b.addEventListener("click", () => { kind = b.dataset.v; mistake = false; build(); }));
  document.querySelectorAll("#cStyle button").forEach(b => b.addEventListener("click", () => { style = b.dataset.v; mistake = false; build(); }));
  $("cReset").addEventListener("click", () => { resetView(); fit(); });

  // ------------------------------------------------------------ density
  function sci(x, d) {
    if (!isFinite(x) || x === 0) return "—";
    const e = Math.floor(Math.log10(Math.abs(x))), m = x / Math.pow(10, e);
    return `${m.toFixed(d === undefined ? 3 : d)} × 10<sup>${e < 0 ? "−" + (-e) : e}</sup>`;
  }
  function calc(m) {
    const rcm = m.r * 1e-10;
    const out = {};
    for (const [k, n, f] of [["bcc", 2, 4 / Math.sqrt(3)], ["fcc", 4, 2 * Math.SQRT2]]) {
      const a = f * m.r, V = Math.pow(f * rcm, 3), rho = n * m.A / (V * NA);
      out[k] = { a, V, n, rho, dev: (rho - m.rho) / m.rho * 100 };
    }
    out.best = Math.abs(out.bcc.dev) < Math.abs(out.fcc.dev) ? "bcc" : "fcc";
    return out;
  }
  function numberLine(m, c) {
    const vals = [m.rho, c.bcc.rho, c.fcc.rho], lo = Math.min(...vals) * 0.96, hi = Math.max(...vals) * 1.04;
    const X = (v) => 16 + (v - lo) / (hi - lo) * 288;
    const ink = "var(--ink)", mut = "var(--muted)";
    let s = `<svg viewBox="0 0 320 78" role="img" aria-label="Measured density against BCC and FCC predictions">`;
    s += `<line x1="16" y1="40" x2="304" y2="40" stroke="${mut}" stroke-width="1.2"/>`;
    const mark = (v, lab, color, up) => `<line x1="${X(v)}" y1="${up ? 30 : 40}" x2="${X(v)}" y2="${up ? 40 : 50}" stroke="${color}" stroke-width="2.4"/><circle cx="${X(v)}" cy="40" r="4.5" fill="${color}"/>` +
      `<text x="${X(v)}" y="${up ? 22 : 66}" font-size="11" font-weight="700" text-anchor="middle" fill="${color}">${lab}</text>`;
    s += mark(c.bcc.rho, `BCC ${c.bcc.rho.toFixed(2)}`, c.best === "bcc" ? "var(--good)" : mut, true);
    s += mark(c.fcc.rho, `FCC ${c.fcc.rho.toFixed(2)}`, c.best === "fcc" ? "var(--good)" : mut, true);
    s += mark(m.rho, `measured ${m.rho}`, ink, false);
    return s + `</svg>`;
  }
  function infoHTML() {
    const b = kind === "bcc";
    let h = `<div class="ttl"><div><div class="part">Part 2 · 2.1 and 2.2 · 4 + 6 marks</div><h3>${b ? "Body-centred cubic" : "Face-centred cubic"}</h3></div><div class="badge ans"><b>${b ? 2 : 4}</b><span>atoms per cell</span></div></div>`;
    h += `<div class="sheet"><div class="k">Where the atoms touch</div><div class="eqn">${b ? "Body diagonal" : "Face diagonal"} = r + 2r + r = 4r<br>${b ? "√3 a = 4r &nbsp;⇒&nbsp; a = 4r/√3" : "√2 a = 4r &nbsp;⇒&nbsp; a = 2√2 r"}</div>`;
    h += `<div class="eqn ans">V = a³ = ${b ? "(4r/√3)³ = 64r³/(3√3) ≈ <b>12.32 r³</b>" : "(2√2 r)³ = 16√2 r³ ≈ <b>22.63 r³</b>"}</div>`;
    h += `<div class="note">Scheme's form: BCC V = (4R/√3)³; FCC V = 16R³√2, with R the atomic radius. 2.2 gives 3 marks per expression.</div></div>`;
    h += `<div class="sheet"><div class="k">Count the atoms</div><table class="t"><thead><tr><th>Site</th><th class="n">Number × share</th><th class="n ans">Total</th></tr></thead><tbody>`;
    h += `<tr><td>Corners</td><td class="n">8 × ⅛</td><td class="n ans">1</td></tr>` + (b ? `<tr><td>Body centre</td><td class="n">1 × 1</td><td class="n ans">1</td></tr>` : `<tr><td>Face centres</td><td class="n">6 × ½</td><td class="n ans">3</td></tr>`);
    h += `<tr class="tot ans"><td>n</td><td></td><td class="n">${b ? 2 : 4}</td></tr></tbody></table></div>`;
    // density
    const m = metal === "Other" ? custom : METALS[metal], c = calc(m);
    h += `<div class="sheet"><div class="k">2.3 and 2.4 · Volume, density, lattice</div><div class="seg" id="mSel" role="group" aria-label="Metal">` +
      ["Cu", "W", "Other"].map(k => `<button type="button" data-m="${k}" aria-pressed="${metal === k}">${k === "Other" ? "Other metal" : k}</button>`).join("") + `</div>`;
    if (metal === "Other") h += `<div class="inp"><label>r / pm<input id="iR" type="number" step="any" value="${custom.r}"></label><label>A / g mol⁻¹<input id="iA" type="number" step="any" value="${custom.A}"></label><label>measured ρ<input id="iRho" type="number" step="any" value="${custom.rho}"></label></div>`;
    else h += `<div class="note">Sheet (Wednesday): ${m.name}, r = ${m.r} pm, measured ${m.rho} g cm⁻³. A = ${m.A} g mol⁻¹ from the periodic table.</div>`;
    const cls = (k) => c.best === k ? "best" : "";
    h += `<div class="calc"><div class="h"></div><div class="h">BCC</div><div class="h">FCC</div>`;
    h += `<div>r = ${m.r} pm</div><div class="n" style="grid-column:span 2">${sci(m.r * 1e-10)} cm</div>`;
    h += `<div>a / pm</div><div class="n ans">${c.bcc.a.toFixed(1)}</div><div class="n ans">${c.fcc.a.toFixed(1)}</div>`;
    h += `<div>V / cm³</div><div class="n ans">${sci(c.bcc.V)}</div><div class="n ans">${sci(c.fcc.V)}</div>`;
    h += `<div>n</div><div class="n">2</div><div class="n">4</div>`;
    h += `<div>ρ = nA / (V N<sub>A</sub>)</div><div class="n ans ${cls("bcc")}">${c.bcc.rho.toFixed(2)}</div><div class="n ans ${cls("fcc")}">${c.fcc.rho.toFixed(2)}</div>`;
    h += `<div>vs measured</div><div class="n ans ${cls("bcc")}">${c.bcc.dev >= 0 ? "+" : "−"}${Math.abs(c.bcc.dev).toFixed(1)} %</div><div class="n ans ${cls("fcc")}">${c.fcc.dev >= 0 ? "+" : "−"}${Math.abs(c.fcc.dev).toFixed(1)} %</div></div>`;
    h += `<div class="nl ans">${numberLine(m, c)}</div>`;
    h += `<div class="read ans"><b>${metal === "Other" ? "This metal" : m.name}: ${c.best.toUpperCase()}</b> fits (${c[c.best].dev >= 0 ? "+" : "−"}${Math.abs(c[c.best].dev).toFixed(1)} %). ` +
         `${c.best === kind ? "" : `<button type="button" id="goBest">Show ${c.best.toUpperCase()}</button>`}</div>`;
    h += `<div class="note">N<sub>A</sub> = 6.022 × 10²³ mol⁻¹. Rounding A or N<sub>A</sub> moves ρ by a few hundredths: treat ±0.05 g cm⁻³ as the same answer.</div></div>`;
    h += `<div class="sheet"><div class="k">Why the answer is never close</div><div class="note" style="color:var(--ink)">For the same r, FCC is always <b>8.9 %</b> denser than BCC (packing 74 % against 68 %). Any metal's two candidates sit about 9 % apart, so a match within 1 % settles it.</div></div>`;
    h += `<div class="call"><b class="h">Units:</b> convert r to cm first (1 pm = 10⁻¹⁰ cm), then cube: the 10⁻¹⁰ becomes 10⁻³⁰. Skipping either throws ρ off by 10²⁰ or more.</div>`;
    h += `<div class="call"><b class="h">Manual's hint:</b> it calls the cube side R, then asks for "the radius of the unit cell (half the length of the cube)". Students who follow it write a/2 = r: simple cubic. Use a for the edge, r for the atom.</div>`;
    return h;
  }
  function renderInfo() {
    info.innerHTML = infoHTML();
    info.querySelectorAll("button[data-m]").forEach(bt => bt.addEventListener("click", () => { metal = bt.dataset.m; renderInfo(); }));
    const g = $("goBest"); if (g) g.addEventListener("click", () => { kind = calc(metal === "Other" ? custom : METALS[metal]).best; mistake = false; build(); });
    for (const [id, key] of [["iR", "r"], ["iA", "A"], ["iRho", "rho"]]) {
      const el = $(id); if (!el) continue;
      el.addEventListener("change", () => { const v = parseFloat(el.value); if (v > 0) { custom[key] = v; renderInfo(); } else el.value = custom[key]; });
    }
  }

  // ------------------------------------------------------------ view
  function fit() { const R = S * Math.sqrt(3) / 2 + 1.2, vf = camera.fov * Math.PI / 180, hf = 2 * Math.atan(Math.tan(vf / 2) * camera.aspect); camera.position.set(0, 0, R / Math.sin(Math.min(vf, hf) / 2) * 1.02); }
  function resetView() { root.quaternion.setFromEuler(new THREE.Euler(0.42, -0.62, 0, "XYZ")); }
  const ptrs = new Map(); let pinch0 = 0, camZ0 = 20;
  stage.addEventListener("pointerdown", (e) => {
    if (e.target.closest("button, input, .toast")) return;
    stage.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) { const [p, q] = [...ptrs.values()]; pinch0 = Math.hypot(p.x - q.x, p.y - q.y); camZ0 = camera.position.z; }
  });
  stage.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return; const prev = ptrs.get(e.pointerId); const dx = e.clientX - prev.x, dy = e.clientY - prev.y;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 1) root.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(UP, dx * 0.008)).premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), dy * 0.008));
    else if (ptrs.size === 2) { const [p, q] = [...ptrs.values()]; const d = Math.hypot(p.x - q.x, p.y - q.y); if (pinch0 > 0) camera.position.z = Math.min(150, Math.max(5, camZ0 * pinch0 / d)); }
  });
  const endPtr = (e) => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = 0; };
  stage.addEventListener("pointerup", endPtr); stage.addEventListener("pointercancel", endPtr);
  stage.addEventListener("wheel", (e) => { e.preventDefault(); camera.position.z = Math.min(150, Math.max(5, camera.position.z * (1 + e.deltaY * 0.001))); }, { passive: false });
  function resize() { const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); fit(); }
  new ResizeObserver(resize).observe(stage);
  const tmp = new THREE.Vector3();
  function placeLabels() {
    const w = stage.clientWidth, h = stage.clientHeight; if (!w) return;
    for (const o of spans) { tmp.copy(W(o.f)).applyQuaternion(root.quaternion).project(camera); o.sp.style.left = ((tmp.x + 1) / 2 * w) + "px"; o.sp.style.top = ((1 - tmp.y) / 2 * h) + "px"; }
  }
  function loop() { if (active) { renderer.render(scene, camera); placeLabels(); } requestAnimationFrame(loop); }
  resetView(); applyTheme(); build(); resize(); requestAnimationFrame(loop);
  window.P2 = { setActive(v) { active = v; if (v) { applyTheme(); resize(); } }, refresh() { renderInfo(); } };
})();
