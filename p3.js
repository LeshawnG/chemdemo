// ============================================================ PART 3 · NaCl and CsCl unit cells
(function () {
  const $ = (id) => document.getElementById(id);
  const stage = $("lStage"), labelsEl = $("lLabels"), info = $("lInfo"), toast = $("lToast"), chipsEl = $("lChips");
  let active = false;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.localClippingEnabled = true;
  stage.insertBefore(renderer.domElement, labelsEl);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 400);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8892a6, 0.85));
  const dl = new THREE.DirectionalLight(0xffffff, 0.75); dl.position.set(4, 7, 9); scene.add(dl);
  const root = new THREE.Group(); scene.add(root);
  const sphereGeo = new THREE.SphereGeometry(1, 36, 24), cylGeo = new THREE.CylinderGeometry(1, 1, 1, 12);
  const UP = new THREE.Vector3(0, 1, 0);
  const S = 4; // cell edge in scene units
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function applyTheme() { renderer.setClearColor(new THREE.Color(cssVar("--stage") || "#e9edf3")); }
  applyTheme();
  try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {}
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  // Colours follow the lab manual's figures: NaCl Cl⁻ blue / Na⁺ red; CsCl Cl⁻ green / Cs⁺ magenta.
  const ST = {
    nacl: { key: "nacl", name: "Sodium chloride", f: "NaCl", aA: 5.64, nn: 0.5, perCell: 4,
      an: { sym: "Cl⁻", r: 1.81, c: "#3b82f6", bench: 0.34 }, cat: { sym: "Na⁺", r: 1.02, c: "#ef4444", bench: 0.27 } },
    cscl: { key: "cscl", name: "Caesium chloride", f: "CsCl", aA: 4.12, nn: Math.sqrt(3) / 2, perCell: 1,
      an: { sym: "Cl⁻", r: 1.81, c: "#22c55e", bench: 0.36 }, cat: { sym: "Cs⁺", r: 1.74, c: "#d946ef", bench: 0.32 } },
  };
  let st = ST.nacl, style = "bench", ext = 1, focus = null, shares = false;
  let ions = [], spans = [], markers = [];
  const ionG = new THREE.Group(), stickG = new THREE.Group(), cellG = new THREE.Group(), polyG = new THREE.Group();
  root.add(cellG, stickG, ionG, polyG);

  function clear(g) { while (g.children.length) { const c = g.children.pop(); if (c.geometry && c.geometry !== sphereGeo && c.geometry !== cylGeo) c.geometry.dispose(); } }
  const W = (f) => new THREE.Vector3((f[0] - ext / 2) * S, (f[2] - ext / 2) * S, -(f[1] - ext / 2) * S); // z-up fractional → y-up scene
  const FR = { 3: "⅛", 2: "¼", 1: "½", 0: "1" };
  const SITE = { 3: "corner", 2: "edge", 1: "face", 0: "body" };

  function sites() {
    const out = [];
    if (st.key === "nacl") {
      for (let i = 0; i <= 2 * ext; i++) for (let j = 0; j <= 2 * ext; j++) for (let k = 0; k <= 2 * ext; k++)
        out.push({ f: [i / 2, j / 2, k / 2], kind: (i + j + k) % 2 === 0 ? "an" : "cat" });
    } else {
      for (let i = 0; i <= ext; i++) for (let j = 0; j <= ext; j++) for (let k = 0; k <= ext; k++) out.push({ f: [i, j, k], kind: "an" });
      for (let i = 0; i < ext; i++) for (let j = 0; j < ext; j++) for (let k = 0; k < ext; k++) out.push({ f: [i + .5, j + .5, k + .5], kind: "cat" });
    }
    for (const s of out) { const b = s.f.filter(x => x === 0 || x === ext).length; s.b = b; s.site = SITE[b]; }
    return out;
  }
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

  function lineMat(op) { return new THREE.LineBasicMaterial({ color: new THREE.Color(cssVar("--ink") || "#121826"), transparent: true, opacity: op }); }
  function cellOutline() {
    const pts = [];
    for (let a = 0; a <= ext; a++) for (let b = 0; b <= ext; b++) {
      pts.push([0, a, b], [ext, a, b]); pts.push([a, 0, b], [a, ext, b]); pts.push([a, b, 0], [a, b, ext]);
    }
    const arr = new Float32Array(pts.length * 3); pts.forEach((p, i) => { const v = W(p); arr.set([v.x, v.y, v.z], i * 3); });
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
    cellG.add(new THREE.LineSegments(g, lineMat(style === "bench" ? 0.25 : 0.55)));
  }
  function stick(p, q, w, color, op) {
    const m = new THREE.Mesh(cylGeo, new THREE.MeshStandardMaterial({ color, roughness: 0.7, transparent: op < 1, opacity: op }));
    const d = new THREE.Vector3().subVectors(q, p), L = d.length();
    m.position.copy(p).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(UP, d.normalize()); m.scale.set(w, L, w);
    stickG.add(m); return m;
  }
  function planes() {
    const h = ext * S / 2 + 0.002;
    return [new THREE.Plane(new THREE.Vector3(1, 0, 0), h), new THREE.Plane(new THREE.Vector3(-1, 0, 0), h),
            new THREE.Plane(new THREE.Vector3(0, 1, 0), h), new THREE.Plane(new THREE.Vector3(0, -1, 0), h),
            new THREE.Plane(new THREE.Vector3(0, 0, 1), h), new THREE.Plane(new THREE.Vector3(0, 0, -1), h)];
  }

  // which ions are in focus, and the coordination centre if any
  function focusSet(list) {
    if (!focus) return null;
    const on = new Set();
    if (["corner", "edge", "face", "body"].includes(focus)) list.forEach((s, i) => { if (s.site === focus) on.add(i); });
    else if (focus === "cat" || focus === "an") {
      const c = focus === "cat" ? [.5, .5, .5] : [1, 1, 1];
      list.forEach((s, i) => { const d = dist(s.f, c); if (d < 1e-6 || Math.abs(d - st.nn) < 1e-6) on.add(i); });
    } else if (focus === "tet") list.forEach((s, i) => { if (s.kind === "an") on.add(i); });
    else if (focus === "lat") list.forEach((s, i) => { if (s.kind === "an") on.add(i); });
    return on;
  }

  function build() {
    clear(ionG); clear(stickG); clear(cellG); clear(polyG); labelsEl.innerHTML = ""; spans = []; markers = [];
    ions = sites();
    const on = focusSet(ions), cut = style === "cut", fill = style !== "bench";
    const scale = S / st.aA, clip = cut ? planes() : [];
    cellOutline();
    ions.forEach((s, i) => {
      const spec = st[s.kind], dim = on && !on.has(i);
      const r = fill ? spec.r * scale : spec.bench;
      const col = new THREE.Color(spec.c);
      const front = new THREE.MeshStandardMaterial({ color: col, roughness: 0.45, metalness: 0.02, clippingPlanes: clip,
        transparent: dim, opacity: dim ? (fill ? 0.07 : 0.14) : 1, depthWrite: !dim });
      const m = new THREE.Mesh(sphereGeo, front); m.scale.setScalar(r); m.position.copy(W(s.f)); ionG.add(m);
      if (cut && !dim) {
        const back = new THREE.MeshBasicMaterial({ color: col.clone().multiplyScalar(0.55), side: THREE.BackSide, clippingPlanes: clip });
        const mb = new THREE.Mesh(sphereGeo, back); mb.scale.setScalar(r * 0.999); mb.position.copy(m.position); ionG.add(mb);
      }
      s.r = r;
    });
    if (style === "bench") {
      const dimAll = !!on;
      if (st.key === "nacl") {
        ions.forEach((a, i) => ions.forEach((b, j) => {
          if (j <= i) return;
          if (Math.abs(dist(a.f, b.f) - 0.5) < 1e-6) stick(W(a.f), W(b.f), 0.055, 0x8b93a5, dimAll && !(on.has(i) && on.has(j)) ? 0.15 : 1);
        }));
      } else {
        ions.forEach((a, i) => ions.forEach((b, j) => {
          if (j <= i) return; const d = dist(a.f, b.f);
          if (a.kind === "an" && b.kind === "an" && Math.abs(d - 1) < 1e-6) stick(W(a.f), W(b.f), 0.06, 0x8b93a5, dimAll ? 0.18 : 1);
          if (a.kind !== b.kind && Math.abs(d - st.nn) < 1e-6) stick(W(a.f), W(b.f), 0.035, 0xb6bccb, dimAll && !(on.has(i) && on.has(j)) ? 0.12 : 0.7);
        }));
      }
    }
    // coordination polyhedron
    if (focus === "cat" || focus === "an") {
      const c = W(focus === "cat" ? [.5, .5, .5] : [1, 1, 1]);
      const col = new THREE.Color(st[focus === "cat" ? "cat" : "an"].c);
      const geo = st.key === "nacl" ? new THREE.OctahedronGeometry(S / 2) : new THREE.BoxGeometry(S, S, S);
      const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.16, side: THREE.DoubleSide, depthWrite: false }));
      mesh.position.copy(c); polyG.add(mesh);
      const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: col })); e.position.copy(c); polyG.add(e);
    }
    if (focus === "tet") {
      const tp = []; for (const x of [.25, .75]) for (const y of [.25, .75]) for (const z of [.25, .75]) tp.push([x, y, z]);
      tp.forEach((f, k) => {
        const m = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0xf8fafc, emissive: 0x334155, roughness: .4 }));
        m.scale.setScalar(0.13); m.position.copy(W(f)); polyG.add(m); markers.push({ f, t: k === 0 ? "hole" : "" });
      });
      const v = [[0, 0, 0], [.5, .5, 0], [.5, 0, .5], [0, .5, .5]].map(W);
      const g = new THREE.BufferGeometry().setFromPoints([v[0], v[1], v[2], v[0], v[1], v[3], v[0], v[2], v[3], v[1], v[2], v[3]]);
      g.computeVertexNormals();
      polyG.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.25, side: THREE.DoubleSide, depthWrite: false })));
      polyG.add(new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ color: 0xb45309 })));
    }
    if (focus === "lat") {
      ions.forEach((s) => {
        if (s.kind !== "an") return;
        const m = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0x7c2d12, roughness: .3 }));
        m.scale.setScalar(0.16); m.position.copy(W(s.f)); polyG.add(m);
      });
      if (st.key === "cscl") for (const s of ions) if (s.kind === "cat") markers.push({ f: s.f, t: "not a lattice point" });
    }
    // labels
    ions.forEach((s, i) => {
      const sp = document.createElement("span"); let txt = "", cls = "";
      const isOn = on && on.has(i);
      if (["corner", "edge", "face", "body"].includes(focus) && isOn) { txt = FR[s.b]; cls = "fr"; }
      else if (shares && ext === 1 && !on) { txt = FR[s.b]; cls = "fr"; }
      else if ((focus === "cat" || focus === "an") && isOn) {
        const c = focus === "cat" ? [.5, .5, .5] : [1, 1, 1];
        if (dist(s.f, c) < 1e-6) { txt = st[s.kind].sym; cls = "fr"; }
      }
      sp.textContent = txt; if (cls) sp.className = cls; sp.hidden = !txt; labelsEl.appendChild(sp); spans.push({ sp, s });
    });
    if (focus === "cat" || focus === "an") {
      let n = 0; spans.forEach(o => { if (!o.sp.textContent && on.has(ions.indexOf(o.s))) { o.sp.textContent = String(++n); o.sp.className = "nb"; o.sp.hidden = false; } });
    }
    markers.forEach(mk => { if (!mk.t) return; const sp = document.createElement("span"); sp.className = "fr"; sp.textContent = mk.t; labelsEl.appendChild(sp); mk.sp = sp; });
    fit(); syncControls(); renderInfo(); renderChips(); setToast(toastFor());
  }

  function toastFor() {
    const n = st.key === "nacl", an = st.an.sym, cat = st.cat.sym;
    const T = {
      corner: `<b>Corners:</b> 8 ${an}, each shared by 8 cells → 8 × ⅛ = <b>1 ${an}</b>`,
      edge: `<b>Edge centres:</b> 12 ${cat}, each shared by 4 cells → 12 × ¼ = <b>3 ${cat}</b>`,
      face: `<b>Face centres:</b> 6 ${an}, each shared by 2 cells → 6 × ½ = <b>3 ${an}</b>`,
      body: `<b>Body centre:</b> 1 ${cat}, wholly inside → <b>1 ${cat}</b>`,
      cat: n ? `<b>Na⁺ at the body centre</b> touches 6 Cl⁻ at the face centres: an octahedron. Na⁺ sits in an <b>octahedral hole</b> of the Cl⁻ array.`
             : `<b>Cs⁺ at the body centre</b> touches all 8 Cl⁻ at the corners: a cube. A <b>cubic hole</b> (CN 8), neither octahedral nor tetrahedral.`,
      an: n ? `<b>Cl⁻ where 8 cells meet</b> touches 6 Na⁺: also an <b>octahedron</b>. You need neighbouring cells to see this, which is why the manual says to join models.`
            : `<b>Cl⁻ where 8 cells meet</b> touches the 8 Cs⁺ at the 8 body centres: also <b>cubic</b>, CN 8. Eight CsCl cells pushed together show it.`,
      tet: `<b>8 tetrahedral holes per cell</b> (white), one in each small cube. Each has 4 Cl⁻ around it (amber tetrahedron). All <b>empty</b> in NaCl; zinc blende (ZnS) fills half of them.`,
      lat: n ? `<b>Lattice points</b> (gold) sit on the Cl⁻ positions: a face-centred cubic lattice, 4 per cell. Each point carries one Cl⁻ and one Na⁺ shifted by a/2.`
             : `<b>Lattice points</b> (gold) sit only on the corners: 1 per cell. The centre holds Cs⁺, not Cl⁻, so it is <b>not</b> a lattice point. Strictly CsCl is primitive cubic; "body-centred" describes the arrangement.`,
    };
    if (focus) return T[focus];
    if (style === "cut" && ext === 1) return `Each ion is cut where the cell ends: you see exactly the share inside this cell.`;
    return "";
  }
  function setToast(h) { toast.hidden = !h; toast.innerHTML = h || ""; }

  function fit() {
    const R = ext * S * Math.sqrt(3) / 2 + (style === "bench" ? 0.5 : 1.6);
    const vf = camera.fov * Math.PI / 180, hf = 2 * Math.atan(Math.tan(vf / 2) * camera.aspect);
    camera.position.set(0, 0, R / Math.sin(Math.min(vf, hf) / 2) * 1.02);
  }
  function resetView() { root.quaternion.setFromEuler(new THREE.Euler(0.42, -0.62, 0, "XYZ")); }

  // ------------------------------------------------------------ chips and controls
  function chipList() {
    const n = st.key === "nacl", L = [];
    L.push(["shares", "Shares", "Label every ion with the share inside one cell"]);
    if (n) L.push(["corner", "Corners"], ["edge", "Edges"], ["face", "Faces"], ["body", "Centre"]);
    else L.push(["corner", "Corners"], ["body", "Centre"]);
    L.push(["cat", `Around ${st.cat.sym}`], ["an", `Around ${st.an.sym}`]);
    if (n) L.push(["tet", "Tetrahedral holes"]);
    L.push(["lat", "Lattice points"]);
    return L;
  }
  function renderChips() {
    chipsEl.innerHTML = "";
    for (const [k, t] of chipList()) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = t;
      b.setAttribute("aria-pressed", (k === "shares" ? shares : focus === k) ? "true" : "false");
      b.addEventListener("click", () => setFocus(k)); chipsEl.appendChild(b);
    }
    if (focus || shares) { const c = document.createElement("button"); c.type = "button"; c.textContent = "Clear"; c.addEventListener("click", () => { focus = null; shares = false; build(); }); chipsEl.appendChild(c); }
  }
  function setFocus(k) {
    if (k === "shares") { shares = !shares; if (shares) { focus = null; ext = 1; } build(); return; }
    focus = focus === k ? null : k; shares = false;
    if (["corner", "edge", "face", "body", "cat", "tet"].includes(focus)) ext = 1;
    if (focus === "an") ext = 2;
    build();
  }
  function syncControls() {
    document.querySelectorAll("#lStruct button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === st.key ? "true" : "false"));
    document.querySelectorAll("#lStyle button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === style ? "true" : "false"));
    document.querySelectorAll("#lExt button").forEach(b => b.setAttribute("aria-pressed", +b.dataset.v === ext ? "true" : "false"));
  }
  document.querySelectorAll("#lStruct button").forEach(b => b.addEventListener("click", () => { st = ST[b.dataset.v]; focus = null; shares = false; build(); }));
  document.querySelectorAll("#lStyle button").forEach(b => b.addEventListener("click", () => { style = b.dataset.v; build(); }));
  document.querySelectorAll("#lExt button").forEach(b => b.addEventListener("click", () => {
    ext = +b.dataset.v; if (focus && focus !== "lat" && !(focus === "an" && ext === 2)) focus = null; if (ext === 2) shares = false; build(); }));
  $("lReset").addEventListener("click", () => { resetView(); fit(); });

  // ------------------------------------------------------------ radius-ratio explainer (2D)
  let rho = 0.56;
  function rrSVG() {
    const ink = "var(--ink)", mut = "var(--muted)", good = "var(--good)", bad = "var(--bad)";
    const anc = st.an.c, cac = st.cat.c, R = 1, r = rho;
    // octahedral hole, equatorial slice: 4 anions at (±d,0),(0,±d)
    const d6 = Math.max(R + r, R * Math.SQRT2), touch6 = R + r >= R * Math.SQRT2 - 1e-9;
    // cubic hole, diagonal slice: corners at (±e/√2, ±e/2); cation–anion = e√3/2
    const e8 = Math.max(2 * R, 2 * (R + r) / Math.sqrt(3)), touch8 = R + r >= R * Math.sqrt(3) - 1e-9;
    const sc = 26, W2 = 150, H = 168;
    const panel = (ox, title, pts, touch, gapTxt) => {
      let g = `<g transform="translate(${ox + W2 / 2},${H / 2 + 6})">`;
      for (const [x, y] of pts) g += `<circle cx="${x * sc}" cy="${y * sc}" r="${R * sc}" fill="${anc}" fill-opacity=".85" stroke="${ink}" stroke-opacity=".35"/>`;
      g += `<circle cx="0" cy="0" r="${r * sc}" fill="${cac}" stroke="${touch ? good : bad}" stroke-width="2.5" ${touch ? "" : 'stroke-dasharray="4 3"'}/>`;
      g += `</g><text x="${ox + W2 / 2}" y="14" text-anchor="middle" font-size="12" font-weight="700" fill="${ink}">${title}</text>`;
      g += `<text x="${ox + W2 / 2}" y="${H + 2}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${touch ? good : bad}">${gapTxt}</text>`;
      return g;
    };
    const p6 = [[d6, 0], [-d6, 0], [0, d6], [0, -d6]];
    const p8 = [[e8 / Math.SQRT2, e8 / 2], [-e8 / Math.SQRT2, e8 / 2], [e8 / Math.SQRT2, -e8 / 2], [-e8 / Math.SQRT2, -e8 / 2]];
    return `<svg viewBox="0 0 310 ${H + 10}" role="img" aria-label="Cation in an octahedral hole and in a cubic hole at radius ratio ${rho.toFixed(2)}">` +
      panel(0, "6 neighbours (octahedral)", p6, touch6, touch6 ? "touches all 6" : "rattles: gap") +
      panel(160, "8 neighbours (cubic)", p8, touch8, touch8 ? "touches all 8" : "rattles: gap") +
      `<line x1="155" y1="22" x2="155" y2="${H - 8}" stroke="${mut}" stroke-opacity=".4"/></svg>`;
  }
  function verdict() {
    if (rho < 0.414) return `<b>r₊/r₋ = ${rho.toFixed(2)} &lt; 0.414:</b> too small even for 6 neighbours. Expect 4 (tetrahedral), as in ZnS.`;
    if (rho < 0.732) return `<b>r₊/r₋ = ${rho.toFixed(2)}:</b> touches 6 anions but would rattle among 8. Expect <b>CN 6, rock salt (NaCl)</b>.`;
    return `<b>r₊/r₋ = ${rho.toFixed(2)} ≥ 0.732:</b> big enough to touch 8 anions. More contacts, more attraction: <b>CN 8, CsCl</b>.`;
  }
  function renderRR() {
    const box = $("rrBox"); if (!box) return;
    box.querySelector(".pic").innerHTML = rrSVG();
    box.querySelector(".val").textContent = rho.toFixed(2);
    box.querySelector(".verdict").innerHTML = verdict();
    const s = $("rrSlide"); if (s && +s.value !== Math.round(rho * 100)) s.value = Math.round(rho * 100);
  }

  // ------------------------------------------------------------ info panel
  function renderInfo() {
    const n = st.key === "nacl", an = st.an, cat = st.cat;
    const dot = (c) => `<span class="dot" style="background:${c}"></span>`;
    const row = (k, site, ion, c, num, share, tot) =>
      `<tr data-focus="${k}" class="${focus === k ? "on" : ""}"><td>${site}</td><td>${dot(c)}${ion}</td><td class="n">${num} × ${share}</td><td class="n ans">= ${tot}</td></tr>`;
    let h = `<div class="ttl"><div><div class="part">Part 3 · Build and describe</div><h3>${st.name}, ${st.f}</h3></div>` +
            `<div class="badge ans"><b>${st.perCell}</b><span>${st.f} per cell</span></div></div>`;
    h += `<div class="sheet"><div class="k">Count the ions in one cell · tap a row</div><table class="t"><thead><tr><th>Site</th><th>Ion</th><th class="n">Number × share</th><th class="n ans">Total</th></tr></thead><tbody>`;
    if (n) {
      h += row("corner", "Corners", an.sym, an.c, 8, "⅛", 1) + row("face", "Face centres", an.sym, an.c, 6, "½", 3);
      h += row("edge", "Edge centres", cat.sym, cat.c, 12, "¼", 3) + row("body", "Body centre", cat.sym, cat.c, 1, "1", 1);
      h += `<tr class="tot ans"><td colspan="2">Cl⁻ 4, Na⁺ 4</td><td class="n" colspan="2">4 NaCl per cell</td></tr>`;
    } else {
      h += row("corner", "Corners", an.sym, an.c, 8, "⅛", 1) + row("body", "Body centre", cat.sym, cat.c, 1, "1", 1);
      h += `<tr class="tot ans"><td colspan="2">Cl⁻ 1, Cs⁺ 1</td><td class="n" colspan="2">1 CsCl per cell</td></tr>`;
    }
    h += `</tbody></table><div class="note">Shares: corner ⅛ (8 cells meet), edge ¼ (4 cells), face ½ (2 cells), inside 1.${n ? " Drawn with Cl⁻ on the corners, as in the manual; Na⁺ on the corners also gives 4 + 4." : ""}</div></div>`;

    h += `<div class="sheet"><div class="k">Which hole does each ion sit in?</div><div class="hole">`;
    if (n) {
      h += `<div>${dot(cat.c)}<b>Na⁺</b> <span class="ans">· octahedral, 6 Cl⁻</span></div><button type="button" data-f="cat" aria-pressed="${focus === "cat"}">Show</button>`;
      h += `<div>${dot(an.c)}<b>Cl⁻</b> <span class="ans">· octahedral, 6 Na⁺</span> <span class="note">(needs neighbouring cells)</span></div><button type="button" data-f="an" aria-pressed="${focus === "an"}">Show</button>`;
      h += `<div><b>Tetrahedral holes</b> <span class="ans">· 8 per cell, all empty</span></div><button type="button" data-f="tet" aria-pressed="${focus === "tet"}">Show</button>`;
    } else {
      h += `<div>${dot(cat.c)}<b>Cs⁺</b> <span class="ans">· cubic, 8 Cl⁻</span></div><button type="button" data-f="cat" aria-pressed="${focus === "cat"}">Show</button>`;
      h += `<div>${dot(an.c)}<b>Cl⁻</b> <span class="ans">· cubic, 8 Cs⁺</span> <span class="note">(needs 8 cells)</span></div><button type="button" data-f="an" aria-pressed="${focus === "an"}">Show</button>`;
    }
    h += `</div>`;
    if (!n) h += `<div class="call"><b class="h">Trap:</b> the sheet asks "octahedral or tetrahedral". In CsCl it is <b>neither</b>: both ions are 8-coordinate, in cubic holes. Accept "cubic" or "8-coordinate".</div>`;
    else h += `<div class="note ans">For Cl⁻ without 8 models: hold another group's cell against a face. The face-centre Cl⁻ touches 4 edge Na⁺ in its face, the body-centre Na⁺, and the body-centre Na⁺ of the next cell.</div>`;
    h += `</div>`;

    h += `<div class="sheet rr" id="rrBox"><div class="k">Why Na⁺ takes 6 neighbours and Cs⁺ takes 8</div>` +
         `<div class="pic"></div>` +
         `<div class="ctl"><label for="rrSlide" class="note">r₊/r₋</label><input id="rrSlide" type="range" min="20" max="100" value="${Math.round(rho * 100)}" aria-label="Radius ratio">` +
         `<span class="val"></span></div>` +
         `<div class="ctl"><button type="button" data-rho="0.56">Na⁺/Cl⁻ 0.56</button><button type="button" data-rho="0.96">Cs⁺/Cl⁻ 0.96</button></div>` +
         `<div class="verdict"></div>` +
         `<div class="note">Anions stay at least touching distance apart. A cation smaller than the hole rattles: no extra attraction, but the anions still repel. Lower limits: √2 − 1 = 0.414 for 6, √3 − 1 = 0.732 for 8. Radii (Shannon): Na⁺ 1.02, Cs⁺ 1.74, Cl⁻ 1.81 Å. A rule of thumb: KCl (0.76) and RbCl (0.84) still take the rock-salt structure.</div></div>`;

    h += `<div class="sheet"><div class="k">Lattice type</div>`;
    h += n ? `<div>Face-centred cubic (fcc) lattice: each ion type alone forms an fcc array, and the two arrays interpenetrate.</div>`
           : `<div class="call"><b class="h">Wording:</b> the sheet says CsCl is "body centred cubic". The ions are arranged that way, but the corner (Cl⁻) and centre (Cs⁺) differ, so the <b>lattice</b> is simple cubic with two ions per point. A student who says this is right.</div>`;
    h += `<button type="button" data-f="lat" aria-pressed="${focus === "lat"}">Show lattice points</button></div>`;

    h += `<div class="sheet"><div class="k">Bench kit</div><div class="note" style="color:var(--ink)">` +
         (n ? `27 balls: 14 Cl⁻ + 13 Na⁺. 54 equal sticks, each half the cell edge; every stick is a real Na⁺–Cl⁻ contact. One kit has 24 balls and 24 sticks, so pool three kits per bench.`
            : `9 balls: 8 Cl⁻ + 1 Cs⁺. 12 long sticks outline the cube, but Cl⁻ ions do not touch each other. The real contacts are 8 shorter sticks (0.87 × edge) from Cs⁺ to the corners.`) +
         `</div></div>`;
    info.innerHTML = h;
    info.querySelectorAll("tr[data-focus]").forEach(tr => tr.addEventListener("click", () => setFocus(tr.dataset.focus)));
    info.querySelectorAll("button[data-f]").forEach(b => b.addEventListener("click", () => setFocus(b.dataset.f)));
    info.querySelectorAll("button[data-rho]").forEach(b => b.addEventListener("click", () => { rho = +b.dataset.rho; renderRR(); }));
    $("rrSlide").addEventListener("input", (e) => { rho = +e.target.value / 100; renderRR(); });
    renderRR();
  }

  // ------------------------------------------------------------ pointer: rotate / pinch
  const ptrs = new Map(); let pinch0 = 0, camZ0 = 20;
  stage.addEventListener("pointerdown", (e) => {
    if (e.target.closest("button, input, .toast")) return;
    stage.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = Math.hypot(a.x - b.x, a.y - b.y); camZ0 = camera.position.z; }
  });
  stage.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return; const prev = ptrs.get(e.pointerId); const dx = e.clientX - prev.x, dy = e.clientY - prev.y;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 1) root.quaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(UP, dx * 0.008)).premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), dy * 0.008));
    else if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y); if (pinch0 > 0) camera.position.z = Math.min(150, Math.max(5, camZ0 * pinch0 / d)); }
  });
  const endPtr = (e) => { ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = 0; };
  stage.addEventListener("pointerup", endPtr); stage.addEventListener("pointercancel", endPtr);
  stage.addEventListener("wheel", (e) => { e.preventDefault(); camera.position.z = Math.min(150, Math.max(5, camera.position.z * (1 + e.deltaY * 0.001))); }, { passive: false });

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); fit();
  }
  new ResizeObserver(resize).observe(stage);
  const tmp = new THREE.Vector3();
  function placeLabels() {
    const w = stage.clientWidth, h = stage.clientHeight;
    const proj = (v) => { tmp.copy(v).applyQuaternion(root.quaternion).project(camera); return [(tmp.x + 1) / 2 * w, (1 - tmp.y) / 2 * h]; };
    for (const o of spans) { if (o.sp.hidden) continue; const [x, y] = proj(W(o.s.f)); o.sp.style.left = x + "px"; o.sp.style.top = y + "px"; }
    for (const mk of markers) if (mk.sp) { const p = W(mk.f); p.y += 0.42; const [x, y] = proj(p); mk.sp.style.left = x + "px"; mk.sp.style.top = y + "px"; }
  }
  function loop() { if (active) { renderer.render(scene, camera); placeLabels(); } requestAnimationFrame(loop); }
  resetView(); build(); resize(); requestAnimationFrame(loop);
  window.P3 = { setActive(v) { active = v; if (v) { applyTheme(); resize(); } }, refresh() { build(); } };
})();
