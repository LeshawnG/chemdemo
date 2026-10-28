// ============================================================ PART 2 · 2D unit cells
(function () {
  const $ = (id) => document.getElementById(id);
  const stage = $("uStage"), cv = $("uCanvas"), ctx = cv.getContext("2d"), info = $("uInfo"), toast = $("uToast"), sel = $("uPat");
  let active = false, dpr = 1, Wd = 0, Hd = 0;
  const S3 = Math.sqrt(3);
  const INK = "#1f2937", PAPER = "#fbfaf6";

  // ---------------------------------------------------------- sample patterns (made for this tool, not the lab's sheets)
  // Each: lattice basis a, b (world units, y down) · motif drawn at a lattice point · answer cells · a typical wrong cell.
  const SAMPLES = [
    { key: "checker", name: "Checkerboard", type: "Square (turned 45°)", a: [1, 1], b: [1, -1], per: "1 dark + 1 light square",
      motif(c) { c.fillStyle = INK; c.fillRect(0, 0, 1, 1); },
      answers: [{ a: [1, 1], b: [1, -1], kind: "prim", note: "Primitive: a square turned 45°, holding 1 dark and 1 light square." },
                { a: [2, 0], b: [0, 2], kind: "conv", note: "Also valid: the 2 × 2 square. It holds 2 lattice points, so it is not primitive." }],
      wrong: { a: [1, 0], b: [0, 1], why: "One square is not a unit cell: shifting by one square lands dark on light." } },
    { key: "brick", name: "Brick wall", type: "Centred rectangular", a: [2, 0], b: [1, 0.7], per: "1 brick",
      motif(c) { c.fillStyle = "#b85c38"; c.fillRect(0, 0, 2, 0.7); c.strokeStyle = "#e9e4da"; c.lineWidth = 0.08; c.strokeRect(0, 0, 2, 0.7); },
      answers: [{ a: [2, 0], b: [1, 0.7], kind: "prim", note: "Primitive: a parallelogram, one brick long, leaning half a brick. Holds 1 brick." },
                { a: [2, 0], b: [0, 1.4], kind: "conv", note: "Conventional: a rectangle 1 brick by 2 courses. Holds 2 bricks (2 lattice points): centred rectangular." }],
      wrong: { a: [2, 0], b: [0, 0.7], why: "One brick is not a unit cell: shifting straight up by one course lands on a joint, because the rows are offset." } },
    { key: "hex", name: "Chicken wire", type: "Hexagonal", a: [S3, 0], b: [S3 / 2, 1.5], per: "2 corners (a Y and an upside-down Y)",
      motif(c) {
        const A = [0, 0], B = [0, 1], B2 = [S3 / 2, -0.5], B3 = [-S3 / 2, -0.5];
        c.strokeStyle = INK; c.lineWidth = 0.09; c.lineCap = "round"; c.beginPath();
        for (const P of [B, B2, B3]) { c.moveTo(A[0], A[1]); c.lineTo(P[0], P[1]); } c.stroke();
        c.fillStyle = INK; for (const P of [A, B]) { c.beginPath(); c.arc(P[0], P[1], 0.1, 0, 2 * Math.PI); c.fill(); } },
      answers: [{ a: [S3, 0], b: [S3 / 2, 1.5], kind: "prim", note: "Primitive: a 60°/120° rhombus. Holds 2 corners, because neighbouring corners point opposite ways." },
                { a: [S3, 0], b: [0, 3], kind: "conv", note: "Also valid: a rectangle holding 2 lattice points." }],
      wrong: { a: [0, 1], b: [S3, 0], why: "Corner-to-neighbouring-corner is not a lattice step: a Y lands on an upside-down Y." } },
    { key: "leaf", name: "Leaf grid", type: "Rectangular", a: [1.6, 0], b: [0, 1.15], per: "1 leaf",
      motif(c) {
        c.save(); c.translate(0.8, 0.6); c.fillStyle = "#2f7d4f"; c.beginPath(); c.moveTo(0, -0.42);
        c.quadraticCurveTo(0.34, -0.05, 0, 0.38); c.quadraticCurveTo(-0.34, -0.05, 0, -0.42); c.fill();
        c.strokeStyle = "#d9f2e2"; c.lineWidth = 0.035; c.beginPath(); c.moveTo(0, -0.34); c.lineTo(0, 0.5); c.stroke(); c.restore(); },
      answers: [{ a: [1.6, 0], b: [0, 1.15], kind: "prim", note: "Primitive and rectangular: 1 leaf per cell. Any origin works, on a leaf or between leaves." }],
      wrong: { a: [3.2, 0], b: [0, 1.15], why: "This cell does repeat the pattern, but it holds 2 leaves. It is valid, not the simplest." } },
    { key: "flag", name: "Flags", type: "Oblique", a: [1.5, 0], b: [0.4, 1.2], per: "1 flag",
      motif(c) {
        c.save(); c.translate(0.35, 0.85); c.strokeStyle = INK; c.lineWidth = 0.05; c.beginPath(); c.moveTo(0, 0); c.lineTo(0, -0.62); c.stroke();
        c.fillStyle = "#c2410c"; c.beginPath(); c.moveTo(0, -0.62); c.lineTo(0.46, -0.48); c.lineTo(0, -0.32); c.fill(); c.restore(); },
      answers: [{ a: [1.5, 0], b: [0.4, 1.2], kind: "prim", note: "Primitive: a parallelogram. No rectangle fits, because each row is shifted along." },
                { a: [1.5, 0], b: [-1.1, 1.2], kind: "conv", note: "Also primitive: a differently-leaning parallelogram with the same area. Both are right." }],
      wrong: { a: [1.5, 0], b: [0, 1.2], why: "Forcing a rectangle fails: straight up is not a translation of this pattern." } },
    { key: "arrows", name: "Arrows", type: "Rectangular, 2 motifs", a: [2, 0], b: [0, 1], per: "2 arrows (one each way)",
      motif(c) {
        const arrow = (x, dir) => { c.save(); c.translate(x, 0.5); c.scale(dir, 1); c.fillStyle = "#1e3a8a"; c.beginPath();
          c.moveTo(-0.32, -0.08); c.lineTo(0.08, -0.08); c.lineTo(0.08, -0.2); c.lineTo(0.34, 0); c.lineTo(0.08, 0.2); c.lineTo(0.08, 0.08); c.lineTo(-0.32, 0.08); c.closePath(); c.fill(); c.restore(); };
        arrow(0.5, 1); arrow(1.5, -1); },
      answers: [{ a: [2, 0], b: [0, 1], kind: "prim", note: "Primitive: 2 wide, 1 high. It must hold one right arrow and one left arrow." }],
      wrong: { a: [1, 0], b: [0, 1], why: "One arrow per cell fails: shifting by one arrow turns → into ←." } },
  ];
  const photos = [];
  // Lab tile sheets, added once photos arrive: { key, name, src (data URI), a, b, o (a lattice point, px), type, per, answers[], wrong? }
  const SHEETS = (window.LAB3_SHEETS || []).map(s => { const img = new Image(); img.src = s.src; return Object.assign({ photo: true, sheet: true, img }, s); });
  SAMPLES.unshift(...SHEETS);
  let cur = SAMPLES[0];
  let view = { cx: 0, cy: 0, sc: 60 };
  let cell = null, tile = false, shift = null, snap = true, answer = false, mistake = false;

  // ---------------------------------------------------------- maths
  const sub = (p, q) => [p[0] - q[0], p[1] - q[1]], add = (p, q) => [p[0] + q[0], p[1] + q[1]];
  const cross = (u, v) => u[0] * v[1] - u[1] * v[0], len = (u) => Math.hypot(u[0], u[1]);
  const keyed = () => !!cur.a, org = () => cur.o || [0, 0];
  function coeffs(v) { const a = cur.a, b = cur.b, D = cross(a, b); return [cross(v, b) / D, cross(a, v) / D]; }
  function nearestLatticeVec(v) { const c = coeffs(v).map(Math.round); return [c[0] * cur.a[0] + c[1] * cur.b[0], c[0] * cur.a[1] + c[1] * cur.b[1]]; }
  function isLatticeVec(v) { const c = coeffs(v); return Math.abs(c[0] - Math.round(c[0])) < 0.04 && Math.abs(c[1] - Math.round(c[1])) < 0.04; }
  const toS = (p) => [(p[0] - view.cx) * view.sc + Wd / 2, (p[1] - view.cy) * view.sc + Hd / 2];
  const toW = (s) => [(s[0] - Wd / 2) / view.sc + view.cx, (s[1] - Hd / 2) / view.sc + view.cy];

  // ---------------------------------------------------------- drawing
  function drawPattern(off, alpha) {
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.setTransform(dpr * view.sc, 0, 0, dpr * view.sc, dpr * (Wd / 2 - (view.cx - off[0]) * view.sc), dpr * (Hd / 2 - (view.cy - off[1]) * view.sc));
    if (cur.photo) { ctx.drawImage(cur.img, 0, 0, cur.w, cur.h); ctx.restore(); return; }
    const corners = [toW([0, 0]), toW([Wd, 0]), toW([0, Hd]), toW([Wd, Hd])].map(p => coeffs(sub(p, off)));
    const i0 = Math.floor(Math.min(...corners.map(c => c[0]))) - 2, i1 = Math.ceil(Math.max(...corners.map(c => c[0]))) + 2;
    const j0 = Math.floor(Math.min(...corners.map(c => c[1]))) - 2, j1 = Math.ceil(Math.max(...corners.map(c => c[1]))) + 2;
    for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
      ctx.save(); ctx.translate(i * cur.a[0] + j * cur.b[0], i * cur.a[1] + j * cur.b[1]); cur.motif(ctx); ctx.restore();
    }
    ctx.restore();
  }
  function poly(O, a, b, stroke, fill, w, dash) {
    const P = [O, add(O, a), add(add(O, a), b), add(O, b)].map(toS);
    ctx.save(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.beginPath(); P.forEach((p, k) => k ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    ctx.setLineDash(dash || []); ctx.strokeStyle = stroke; ctx.lineWidth = w; ctx.stroke(); ctx.restore();
  }
  function arrow(O, v, col, lab) {
    const p = toS(O), q = toS(add(O, v)), d = [q[0] - p[0], q[1] - p[1]], L = Math.hypot(d[0], d[1]) || 1, u = [d[0] / L, d[1] / L];
    ctx.save(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 3.2;
    ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0] - u[0] * 10, q[1] - u[1] * 10); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(q[0], q[1]); ctx.lineTo(q[0] - u[0] * 14 - u[1] * 7, q[1] - u[1] * 14 + u[0] * 7); ctx.lineTo(q[0] - u[0] * 14 + u[1] * 7, q[1] - u[1] * 14 - u[0] * 7); ctx.fill();
    const m = [(p[0] + q[0]) / 2 - u[1] * 16, (p[1] + q[1]) / 2 + u[0] * 16];
    ctx.font = "italic 700 17px 'IBM Plex Sans', system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.lineWidth = 4; ctx.strokeStyle = PAPER; ctx.strokeText(lab, m[0], m[1]); ctx.fillText(lab, m[0], m[1]); ctx.restore();
  }
  function handle(p, col) {
    const s = toS(p); ctx.save(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.beginPath(); ctx.arc(s[0], s[1], 11, 0, 2 * Math.PI); ctx.fillStyle = "rgba(255,255,255,.92)"; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = col; ctx.stroke();
    ctx.beginPath(); ctx.arc(s[0], s[1], 3.5, 0, 2 * Math.PI); ctx.fillStyle = col; ctx.fill(); ctx.restore();
  }
  function nearLatticePoint(p) {
    if (!keyed()) return p;
    const o = org(), c = coeffs(sub(p, o)).map(Math.round); return add(o, [c[0] * cur.a[0] + c[1] * cur.b[0], c[0] * cur.a[1] + c[1] * cur.b[1]]);
  }
  const BLUE = "#1d4ed8", GREEN = "#15803d", AMBER = "#b45309";
  function draw() {
    if (!Wd) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.fillStyle = cur.photo ? "#d6dae1" : PAPER; ctx.fillRect(0, 0, Wd, Hd);
    drawPattern([0, 0], 1);
    const va = sub(cell.A, cell.O), vb = sub(cell.B, cell.O);
    if (shift) drawPattern(shift === "a" ? va : vb, 0.45);
    if (tile) {
      const corners = [toW([0, 0]), toW([Wd, 0]), toW([0, Hd]), toW([Wd, Hd])];
      const D = cross(va, vb);
      if (Math.abs(D) > 1e-6) {
        const cf = corners.map(p => { const v = sub(p, cell.O); return [cross(v, vb) / D, cross(va, v) / D]; });
        const i0 = Math.floor(Math.min(...cf.map(c => c[0]))) - 1, i1 = Math.ceil(Math.max(...cf.map(c => c[0]))) + 1;
        const j0 = Math.floor(Math.min(...cf.map(c => c[1]))) - 1, j1 = Math.ceil(Math.max(...cf.map(c => c[1]))) + 1;
        if ((i1 - i0) * (j1 - j0) < 4000)
          for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
            const O = add(cell.O, [i * va[0] + j * vb[0], i * va[1] + j * vb[1]]);
            poly(O, va, vb, "rgba(29,78,216,.55)", null, 1.4);
            const s = toS(O); ctx.save(); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.fillStyle = BLUE; ctx.beginPath(); ctx.arc(s[0], s[1], 3, 0, 7); ctx.fill(); ctx.restore();
          }
      }
    }
    if (answer && keyed()) {
      const O = nearLatticePoint([view.cx, view.cy]);
      cur.answers.forEach((an) => poly(O, an.a, an.b, an.kind === "prim" ? GREEN : AMBER, an.kind === "prim" ? "rgba(21,128,61,.10)" : null, 3, an.kind === "prim" ? [] : [9, 6]));
    }
    poly(cell.O, va, vb, BLUE, "rgba(29,78,216,.14)", 2.6);
    arrow(cell.O, va, BLUE, "a"); arrow(cell.O, vb, BLUE, "b");
    handle(cell.O, BLUE); handle(cell.A, BLUE); handle(cell.B, BLUE);
  }

  // ---------------------------------------------------------- cell feedback
  function feedback() {
    const va = sub(cell.A, cell.O), vb = sub(cell.B, cell.O), D = cross(va, vb);
    const ang = Math.abs(Math.atan2(cross(va, vb), va[0] * vb[0] + va[1] * vb[1]) * 180 / Math.PI);
    const unit = cur.photo ? " px" : "";
    let h = `<div class="check"><div>|a| = <b>${len(va).toFixed(2)}${unit}</b> · |b| = <b>${len(vb).toFixed(2)}${unit}</b> · angle <b>${ang.toFixed(0)}°</b></div>`;
    if (Math.abs(D) < 1e-6) return h + `<div class="no">a and b point the same way: no area.</div></div>`;
    if (!keyed()) return h + `<div class="note">No answer key for a photo. Use the shift test: when a is a true repeat, the faded copy lands exactly on the pattern everywhere. Then do the same for b.</div></div>`;
    const okA = isLatticeVec(va), okB = isLatticeVec(vb);
    h += `<div>${okA ? '<span class="ok">✓</span>' : '<span class="no">✗</span>'} a ${okA ? "is a repeat of the pattern" : "is not a repeat: the shifted copy does not line up"}</div>`;
    h += `<div>${okB ? '<span class="ok">✓</span>' : '<span class="no">✗</span>'} b ${okB ? "is a repeat of the pattern" : "is not a repeat: the shifted copy does not line up"}</div>`;
    if (okA && okB) {
      const n = Math.round(Math.abs(D) / Math.abs(cross(cur.a, cur.b)));
      h += n === 1 ? `<div class="ok">Valid primitive cell: 4 corners × ¼ = 1 lattice point. It holds ${cur.per}.</div>`
                   : `<div><b>Valid but not primitive:</b> it holds ${n} lattice points. A cell ${n} times smaller also works.</div>`;
    } else h += `<div class="no">Not a unit cell: copies of it by translation would not rebuild the pattern.</div>`;
    return h + `</div>`;
  }
  function renderInfo() {
    let h = `<div class="ttl"><div><div class="part">Part 2 · Find the unit cell</div><h3>${cur.name}</h3></div>` +
            (!cur.type ? "" : `<div class="badge ans"><b style="font-size:15px">${cur.type}</b><span>lattice</span></div>`) + `</div>`;
    h += `<div class="sheet"><div class="k">Your cell (blue) · drag the three handles</div><div id="uFb"></div></div>`;
    if (keyed() && answer) h += `<div class="sheet ans"><div class="k">Answer</div>` + cur.answers.map(a => `<div><span class="dot" style="background:${a.kind === "prim" ? GREEN : AMBER}"></span>${a.note}</div>`).join("") + `</div>`;
    if (cur.wrong && mistake) h += `<div class="call"><b class="h">Common mistake:</b> ${cur.wrong.why}</div>`;
    h += `<div class="sheet"><div class="k">The rules students apply</div><ul class="rules">
      <li>A 2D unit cell is a <b>parallelogram</b> set by two edges, a and b.</li>
      <li>It must rebuild the whole pattern by <b>sliding copies only</b>: no turning, no flipping.</li>
      <li>All four corners land on <b>identical points</b> (same motif, same orientation). The origin can be anywhere.</li>
      <li>Many cells are possible. The <b>primitive</b> one holds 1 lattice point (4 × ¼); a bigger one is still valid.</li>
      <li>Count what is inside: a cell holds a whole number of motifs.</li></ul></div>`;
    h += `<div class="sheet"><div class="k">Typical errors</div><ul class="rules">
      <li>Boxing one motif when its neighbours are turned or mirrored copies.</li>
      <li>Drawing a hexagon or triangle as the cell.</li>
      <li>Corners on points that look alike but differ (e.g. a Y and an upside-down Y).</li></ul></div>`;
    h += `<div class="note">Sample patterns were made for this tool. Load a photo of the real sheet to check students' cells on it.</div>`;
    info.innerHTML = h; $("uFb").innerHTML = feedback();
  }
  function setToast(h) { toast.hidden = !h; toast.innerHTML = h || ""; }

  // ---------------------------------------------------------- view & cell setup
  function fitView() {
    if (cur.photo) { view.cx = cur.w / 2; view.cy = cur.h / 2; view.sc = Math.min(Wd / cur.w, Hd / cur.h) * 0.96 || 1; }
    else { view.cx = 0; view.cy = 0; view.sc = Math.max(34, Math.min(Wd, Hd) / 7.5); }
  }
  function resetCell() {
    mistake = false;
    if (cur.photo) { const s = Math.min(cur.w, cur.h) / 5, O = [cur.w / 2 - s / 2, cur.h / 2 - s / 2]; cell = { O, A: add(O, [s, 0]), B: add(O, [0, s]) }; }
    else { const O = nearLatticePoint([view.cx - 1, view.cy - 0.6]); cell = { O, A: add(O, [1.2, 0]), B: add(O, [0.3, 1.1]) }; if (snap) { cell.A = add(O, nearestLatticeVec([1.2, 0])); cell.B = add(O, nearestLatticeVec([0.3, 1.1])); } }
    if (cur.photo && keyed()) {
      const O = nearLatticePoint([cur.w / 2, cur.h / 2]), ga = [len(cur.a) * 1.1, 0], gb = [len(cur.b) * 0.3, len(cur.b) * 1.05];
      const sa = nearestLatticeVec(ga), sb = nearestLatticeVec(gb);
      cell = { O, A: add(O, snap && len(sa) > 1e-6 ? sa : ga), B: add(O, snap && len(sb) > 1e-6 && Math.abs(cross(sa, sb)) > 1e-6 ? sb : gb) };
    }
    update();
  }
  function setPattern(p) {
    cur = p; answer = false; shift = null; tile = false; mistake = false;
    $("uAnswer").setAttribute("aria-pressed", "false"); $("uAnswer").hidden = !p.a; $("uMistake").hidden = !p.wrong; $("uSnap").hidden = !p.a;
    fitView(); resetCell(); syncChips(); setToast(p.photo && !p.a ? "Photo loaded. Drag the handles onto matching points, then use the shift test." : "");
  }
  function syncChips() {
    $("uTile").setAttribute("aria-pressed", tile ? "true" : "false");
    $("uShiftA").setAttribute("aria-pressed", shift === "a" ? "true" : "false");
    $("uShiftB").setAttribute("aria-pressed", shift === "b" ? "true" : "false");
    $("uSnap").setAttribute("aria-pressed", snap ? "true" : "false");
    $("uAnswer").setAttribute("aria-pressed", answer ? "true" : "false");
  }
  function update() { draw(); renderInfo(); }

  function fillSelect() {
    sel.innerHTML = (SHEETS.length ? `<optgroup label="Lab sheets">` + SHEETS.map(s => `<option value="s:${s.key}">${s.name}</option>`).join("") + `</optgroup>` : "") +
      `<optgroup label="Practice patterns">` + SAMPLES.filter(s => !s.sheet).map(s => `<option value="s:${s.key}">${s.name}</option>`).join("") + `</optgroup>` +
      (photos.length ? `<optgroup label="Your photos">` + photos.map((p, i) => `<option value="p:${i}">${p.name}</option>`).join("") + `</optgroup>` : "");
    sel.value = cur.sheet || !cur.photo ? "s:" + cur.key : "p:" + photos.indexOf(cur);
  }
  sel.addEventListener("change", () => {
    const [t, k] = sel.value.split(":"); setPattern(t === "s" ? SAMPLES.find(s => s.key === k) : photos[+k]);
  });
  $("uFile").addEventListener("change", (e) => {
    const f = e.target.files && e.target.files[0]; if (!f) return;
    const url = URL.createObjectURL(f), img = new Image();
    img.onload = () => { const p = { photo: true, img, w: img.naturalWidth, h: img.naturalHeight, name: "Photo " + (photos.length + 1) }; photos.push(p); cur = p; fillSelect(); setPattern(p); };
    img.onerror = () => setToast('<span class="no">That file could not be opened as an image.</span> Try a JPEG or PNG.');
    img.src = url; e.target.value = "";
  });
  $("uFit").addEventListener("click", () => { fitView(); update(); });
  $("uResetCell").addEventListener("click", resetCell);
  $("uTile").addEventListener("click", () => { tile = !tile; syncChips(); update(); });
  $("uShiftA").addEventListener("click", () => { shift = shift === "a" ? null : "a"; syncChips(); update();
    setToast(shift ? "The faded copy is the pattern slid along <b>a</b>. If it sits exactly on top everywhere, a is a true repeat." : ""); });
  $("uShiftB").addEventListener("click", () => { shift = shift === "b" ? null : "b"; syncChips(); update();
    setToast(shift ? "The faded copy is the pattern slid along <b>b</b>. If it sits exactly on top everywhere, b is a true repeat." : ""); });
  $("uSnap").addEventListener("click", () => { snap = !snap; syncChips(); });
  $("uAnswer").addEventListener("click", () => { answer = !answer; syncChips(); update(); });
  $("uMistake").addEventListener("click", () => {
    if (!cur.wrong) return; mistake = true; const O = cell.O; cell = { O, A: add(O, cur.wrong.a), B: add(O, cur.wrong.b) };
    tile = true; shift = isLatticeVec(cur.wrong.a) ? "b" : "a"; syncChips(); update();
    setToast(`<b>Common mistake.</b> ${cur.wrong.why}`);
  });

  // ---------------------------------------------------------- pointer: drag handles, pan, pinch
  const ptrs = new Map(); let drag = null, pinch = null;
  function hit(sx, sy) {
    for (const k of ["A", "B", "O"]) { const s = toS(cell[k]); if (Math.hypot(s[0] - sx, s[1] - sy) < 26) return k; }
    return null;
  }
  function local(e) { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }
  cv.addEventListener("pointerdown", (e) => {
    cv.setPointerCapture(e.pointerId); const p = local(e); ptrs.set(e.pointerId, p);
    if (ptrs.size === 1) { const k = hit(p[0], p[1]); drag = k ? { k, start: toW(p), cell: { ...cell } } : { k: "pan", p0: p, c0: [view.cx, view.cy] }; }
    else if (ptrs.size === 2) { drag = null; const [a, b] = [...ptrs.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), sc: view.sc }; }
  });
  cv.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return; const p = local(e); ptrs.set(e.pointerId, p);
    if (pinch && ptrs.size === 2) { const [a, b] = [...ptrs.values()]; view.sc = Math.max(4e-3, pinch.sc * Math.hypot(a[0] - b[0], a[1] - b[1]) / pinch.d); draw(); return; }
    if (!drag) return;
    if (drag.k === "pan") { view.cx = drag.c0[0] - (p[0] - drag.p0[0]) / view.sc; view.cy = drag.c0[1] - (p[1] - drag.p0[1]) / view.sc; draw(); return; }
    const w = toW(p), d = sub(w, drag.start);
    if (drag.k === "O") { cell = { O: add(drag.cell.O, d), A: add(drag.cell.A, d), B: add(drag.cell.B, d) }; }
    else {
      let q = add(drag.cell[drag.k], d);
      if (snap && keyed()) { const v = sub(q, cell.O), L = nearestLatticeVec(v); if (len(sub(v, L)) * view.sc < 22 && len(L) > 1e-6) q = add(cell.O, L); }
      cell = { ...cell, [drag.k]: q };
    }
    draw(); const fb = $("uFb"); if (fb) fb.innerHTML = feedback();
  });
  const end = (e) => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch = null; if (!ptrs.size) { if (drag && drag.k !== "pan") { mistake = false; renderInfo(); } drag = null; } };
  cv.addEventListener("pointerup", end); cv.addEventListener("pointercancel", end);
  cv.addEventListener("wheel", (e) => { e.preventDefault(); const p = local(e), w0 = toW(p); view.sc *= Math.exp(-e.deltaY * 0.0015); const w1 = toW(p); view.cx += w0[0] - w1[0]; view.cy += w0[1] - w1[1]; draw(); }, { passive: false });

  function resize() {
    const r = stage.getBoundingClientRect(); if (!r.width || !r.height) return;
    const first = !Wd; dpr = Math.min(window.devicePixelRatio || 1, 2); Wd = r.width; Hd = r.height;
    cv.width = Math.round(Wd * dpr); cv.height = Math.round(Hd * dpr); cv.style.width = Wd + "px"; cv.style.height = Hd + "px";
    if (first) { fitView(); resetCell(); } else draw();
  }
  new ResizeObserver(resize).observe(stage);
  for (const sh of SHEETS) sh.img.onload = () => { sh.w = sh.img.naturalWidth; sh.h = sh.img.naturalHeight; if (cur === sh && Wd) { fitView(); resetCell(); } };
  fillSelect();
  window.P2 = { setActive(v) { active = v; if (v) resize(); }, refresh() { if (cell) update(); },
    addPattern(p) { SAMPLES.push(p); fillSelect(); } };
})();
