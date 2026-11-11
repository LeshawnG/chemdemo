// ============================================================ PART 1 · NH3 molecular orbitals
(function () {
  const $ = (id) => document.getElementById(id);
  const stage = $("mStage"), labelsEl = $("mLabelsEl"), info = $("mInfo"), toast = $("mToast"), chipsEl = $("mChips"), chips2 = $("mChips2");
  const MO = window.LAB4_MO;
  let active = false, student = false;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  stage.insertBefore(renderer.domElement, labelsEl);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 400);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8892a6, 0.85));
  const dl = new THREE.DirectionalLight(0xffffff, 0.7); dl.position.set(4, 7, 9); scene.add(dl);
  const root = new THREE.Group(); scene.add(root);
  const sphereGeo = new THREE.SphereGeometry(1, 40, 28), cylGeo = new THREE.CylinderGeometry(1, 1, 1, 14);
  const UP = new THREE.Vector3(0, 1, 0);
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function applyTheme() { renderer.setClearColor(new THREE.Color(cssVar("--stage") || "#e9edf3")); if (built) build(); }
  let built = false;
  try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme); } catch (e) {}
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  // ------------------------------------------------------------ geometry (molecule frame: Å, z along C3, N on top)
  const SC = 2.3, Rc = MO._geom.Rc, hN = MO._geom.hN;
  const TH = [0, 2 * Math.PI / 3, 4 * Math.PI / 3];
  const HOME = TH.map(t => [Rc * Math.cos(t), Rc * Math.sin(t), 0]);
  const NHOME = [0, 0, hN];
  const W = (p) => new THREE.Vector3(p[0] * SC, (p[2] - hN / 2) * SC, -p[1] * SC);
  const D = (v) => new THREE.Vector3(v[0], v[2], -v[1]).normalize();   // molecule-frame direction -> scene direction
  let hNow = HOME.map(p => p.slice()), nNow = NHOME.slice();

  // ------------------------------------------------------------ state
  let step = "shape", showLabels = true;
  let showAxis = true, showPlanes = false, opKey = null, opT = 0, anim = null; const found = new Set(); let stayed = null;
  let salc = "a1", showNode = true, showN = true;
  let nOrb = "s", mSalc = "a1", bonding = true;
  let moKey = "3a1", nVal = 8, valenceNum = false;

  // ------------------------------------------------------------ data
  const SUB = (s) => s.replace(/_([0-9a-z]+)/g, "<sub>$1</sub>");
  const SALC = {
    a1: { c: [1, 1, 1].map(x => x / Math.sqrt(3)), lab: "a<sub>1</sub>", f: "φ<sub>1</sub> + φ<sub>2</sub> + φ<sub>3</sub>", node: "none", sym: "a1" },
    ex: { c: [2, -1, -1].map(x => x / Math.sqrt(6)), lab: "e(x)", f: "2φ<sub>1</sub> − φ<sub>2</sub> − φ<sub>3</sub>", node: "one: the plane through N between H1 and H2/H3", sym: "e" },
    ey: { c: [0, 1, -1].map(x => x / Math.sqrt(2)), lab: "e(y)", f: "φ<sub>2</sub> − φ<sub>3</sub>", node: "one: the plane through N and H1", sym: "e" },
  };
  const NORB = {
    s: { lab: "N 2s", sym: "a1", cs: 1, cp: [0, 0, 0] },
    pz: { lab: "N 2p<sub>z</sub>", sym: "a1", cs: 0, cp: [0, 0, 1] },
    px: { lab: "N 2p<sub>x</sub>", sym: "e", cs: 0, cp: [1, 0, 0] },
    py: { lab: "N 2p<sub>y</sub>", sym: "e", cs: 0, cp: [0, 1, 0] },
  };
  // Slater-orbital overlaps at the NH3 geometry (N zeta 1.95, H zeta 1.30); px/py/pz values follow from symmetry
  const Sv = MO._S, a = Sv.pxH1;
  const SNH = { s: [Sv.sH, Sv.sH, Sv.sH], px: [a, -a / 2, -a / 2], py: [0, a * Math.sqrt(3) / 2, -a * Math.sqrt(3) / 2], pz: [Sv.pzH, Sv.pzH, Sv.pzH] };
  function salcNorm(c) { let t = 0; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) t += c[i] * c[j] * (i === j ? 1 : Sv.HH); return 1 / Math.sqrt(t); }
  function groupOverlap(n, s) { const c = SALC[s].c, k = salcNorm(c); const parts = c.map((ci, i) => ci * SNH[n][i]); const sum = parts.reduce((x, y) => x + y, 0); return { parts, sum, G: k * sum }; }

  // MO levels (diagram positions are qualitative; filled order as photoelectron spectroscopy gives, empty order from extended Hückel)
  const LV = [
    { k: "2a1", lab: "2a_1", v: "1a_1", E: -27, deg: 1, kind: "bonding", desc: "Mostly N 2s with all three H 1s in phase (H<sub>3</sub> a<sub>1</sub>). Strongly bonding; the lowest valence MO.", mos: ["2a1"] },
    { k: "1e", lab: "1e", v: "1e", E: -16.2, deg: 2, kind: "bonding", desc: "N 2p<sub>x</sub> with e(x), and N 2p<sub>y</sub> with e(y), in phase. A degenerate bonding pair: together with 2a<sub>1</sub>, these hold the three N–H bonds.", mos: ["1ex", "1ey"] },
    { k: "3a1", lab: "3a_1", v: "2a_1", E: -11.6, deg: 1, kind: "HOMO · lone pair", desc: "Mostly N 2p<sub>z</sub> with some 2s. The big lobe points up the C<sub>3</sub> axis, away from the H atoms: the lone pair. Close to nonbonding. This is the electron pair NH<sub>3</sub> donates as a base or ligand.", mos: ["3a1"] },
    { k: "2e", lab: "2e*", v: "2e*", E: -4.5, deg: 2, kind: "antibonding", desc: "N 2p<sub>x</sub>/2p<sub>y</sub> with the e pair out of phase. Empty in NH<sub>3</sub>.", mos: ["2ex", "2ey"] },
    { k: "4a1", lab: "4a_1*", v: "3a_1*", E: -1.2, deg: 1, kind: "antibonding", desc: "N 2s/2p<sub>z</sub> with H<sub>3</sub> a<sub>1</sub> out of phase. Empty. Which empty level sits higher depends on the method; not marked.", mos: ["4a1"] },
  ];
  const MOLAB = { "2a1": "2a<sub>1</sub>", "1ex": "1e (x)", "1ey": "1e (y)", "3a1": "3a<sub>1</sub>", "2ex": "2e* (x)", "2ey": "2e* (y)", "4a1": "4a<sub>1</sub>*" };
  const MOVAL = { "2a1": "1a<sub>1</sub>", "1ex": "1e (x)", "1ey": "1e (y)", "3a1": "2a<sub>1</sub>", "2ex": "2e* (x)", "2ey": "2e* (y)", "4a1": "3a<sub>1</sub>*" };
  const lvOf = (mk) => LV.find(l => l.mos.includes(mk));

  // ------------------------------------------------------------ scene building
  const atomG = new THREE.Group(), orbG = new THREE.Group(), elemG = new THREE.Group();
  root.add(elemG, atomG, orbG);
  function clear(g) { while (g.children.length) { const c = g.children.pop(); if (c.geometry && c.geometry !== sphereGeo && c.geometry !== cylGeo) c.geometry.dispose(); } }
  let spans = [];
  function label(get, txt, cls) { const sp = document.createElement("span"); sp.innerHTML = txt; if (cls) sp.className = cls; labelsEl.appendChild(sp); spans.push({ sp, get }); return sp; }
  const col = (sign) => new THREE.Color(cssVar(sign > 0 ? "--pos" : "--neg") || (sign > 0 ? "#2f67d8" : "#e0782f"));
  function lobeMat(sign, op) { return new THREE.MeshStandardMaterial({ color: col(sign), roughness: 0.5, metalness: 0, transparent: true, opacity: op || 0.8, depthWrite: false }); }
  function sphereLobe(center, r, sign) {
    if (r < 0.04) return; const m = new THREE.Mesh(sphereGeo, lobeMat(sign)); m.position.copy(center); m.scale.setScalar(r); m.renderOrder = 2; orbG.add(m);
  }
  function pLobe(center, dir, amp, sign) {
    if (amp < 0.05) return;
    const L = 0.55 + 1.55 * amp, w = 0.32 + 0.42 * amp;
    const m = new THREE.Mesh(sphereGeo, lobeMat(sign)); m.scale.set(w, L / 2, w);
    m.quaternion.setFromUnitVectors(UP, dir); m.position.copy(center).addScaledVector(dir, L / 2 * 0.96); m.renderOrder = 2; orbG.add(m);
  }
  function drawN(cs, cp, gain) {
    gain = gain || 1; const c0 = W(nNow);
    const P = Math.hypot(cp[0], cp[1], cp[2]);
    if (P < 0.12) { if (Math.abs(cs) > 0.04) sphereLobe(c0, (0.42 + 0.75 * Math.abs(cs)) * gain, Math.sign(cs)); return; }
    const u = D([cp[0] / P, cp[1] / P, cp[2] / P]), k = 0.65;
    const ap = k * cs + P, am = k * cs - P;
    pLobe(c0, u, Math.abs(ap) * gain, Math.sign(ap) || 1);
    pLobe(c0, u.clone().negate(), Math.abs(am) * gain, Math.sign(am) || 1);
  }
  function drawH(coeffs, gain) {
    gain = gain || 1;
    coeffs.forEach((c, i) => { if (Math.abs(c) > 0.02) sphereLobe(W(hNow[i]), (0.2 + 0.95 * Math.abs(c)) * gain, Math.sign(c)); });
  }
  function stick(p, q, w, color, op) {
    const m = new THREE.Mesh(cylGeo, new THREE.MeshStandardMaterial({ color, roughness: 0.7, transparent: op < 1, opacity: op }));
    const d = new THREE.Vector3().subVectors(q, p), L = d.length();
    m.position.copy(p).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(UP, d.normalize()); m.scale.set(w, L, w); atomG.add(m); return m;
  }
  function atoms(big, ghostN) {
    const rN = big ? 0.55 : 0.3, rH = big ? 0.36 : 0.2;
    const nm = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0x3a4a8c, roughness: 0.4, transparent: !!ghostN, opacity: ghostN ? 0.25 : 1 }));
    nm.scale.setScalar(rN); nm.position.copy(W(nNow)); atomG.add(nm);
    hNow.forEach((p) => { const m = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({ color: 0xe8ecf2, roughness: 0.45 })); m.scale.setScalar(rH); m.position.copy(W(p)); atomG.add(m); });
    hNow.forEach((p) => stick(W(nNow), W(p), big ? 0.09 : 0.055, 0x8b93a5, ghostN ? 0.25 : 1));
  }
  function plane(normalMol, size, color, op) {
    const g = new THREE.PlaneGeometry(size, size);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color, transparent: true, opacity: op, side: THREE.DoubleSide, depthWrite: false }));
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), D(normalMol)); m.position.copy(W([0, 0, hN / 2])); m.renderOrder = 1; elemG.add(m);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.7 }));
    e.quaternion.copy(m.quaternion); e.position.copy(m.position); elemG.add(e);
  }
  function axis() {
    const p = W([0, 0, -0.9]), q = W([0, 0, hN + 1.2]);
    stick(p, q, 0.035, new THREE.Color(cssVar("--good") || "#15803d"), 1);
    label(() => [0, 0, hN + 1.38], "C<sub>3</sub>", "ax");
  }
  const sigNormal = (k) => [-Math.sin(TH[k]), Math.cos(TH[k]), 0];

  function build() {
    built = true;
    clear(atomG); clear(orbG); clear(elemG); labelsEl.innerHTML = ""; spans = [];
    if (step === "shape") {
      atoms(true, false);
      if (showAxis) axis();
      if (showPlanes || (opKey && OPS[opKey].kind === "ref")) {
        for (let k = 0; k < 3; k++) {
          const hl = opKey && OPS[opKey].k === k;
          if (!showPlanes && !hl) continue;
          plane(sigNormal(k), 5.6, hl ? 0x7c3aed : 0x8b5cf6, hl ? 0.22 : 0.1);
        }
      }
      if (opKey === "sh") plane([0, 0, 1], 6, 0xb42318, 0.12);
    } else if (step === "frag") {
      atoms(false, true);
      if (!showN) atomG.children.forEach((m, i) => { if (i === 0) m.visible = false; });
      drawH(SALC[salc].c);
      if (showNode) {
        if (salc === "ex") plane([1, 0, 0], 5.4, 0x475569, 0.13);
        if (salc === "ey") plane([0, 1, 0], 5.4, 0x475569, 0.13);
      }
    } else if (step === "match") {
      atoms(false, false);
      const no = NORB[nOrb]; drawN(no.cs, no.cp);
      const g = groupOverlap(nOrb, mSalc), flip = (Math.abs(g.sum) < 1e-6 ? 1 : (bonding ? Math.sign(g.sum) : -Math.sign(g.sum)));
      drawH(SALC[mSalc].c.map(x => x * flip));
    } else if (step === "mo") {
      atoms(false, false);
      const c = MO[moKey];
      drawN(c[0], [c[1], c[2], c[3]], 1);
      drawH([c[4], c[5], c[6]], 1);
    }
    if (showLabels) {
      label(() => [nNow[0], nNow[1], nNow[2] + (step === "shape" ? 0.5 : 0.36)], "N", "");
      HOME.forEach((_, i) => label(() => { const p = hNow[i]; const r = Math.hypot(p[0], p[1]) || 1; const out = step === "shape" ? 0.0 : 0.42; return [p[0] + p[0] / r * out, p[1] + p[1] / r * out, p[2] - (step === "shape" ? 0 : 0.18)]; }, String(i + 1), "nb"));
      if (step === "shape" && showPlanes) for (let k = 0; k < 3; k++) label(() => [Rc * 1.55 * Math.cos(TH[k]), Rc * 1.55 * Math.sin(TH[k]), 0.9], "σ<sub>v</sub>", "pl");
    }
    syncControls(); renderChips(); renderInfo(); setToast(toastFor()); placeLabels();
  }

  // ------------------------------------------------------------ symmetry operations (step 1)
  const OPS = {
    E: { lab: "E", kind: "id", valid: true },
    C3: { lab: "C<sub>3</sub>", kind: "rot", ang: 120, valid: true },
    C32: { lab: "C<sub>3</sub><sup>2</sup>", kind: "rot", ang: 240, valid: true },
    s0: { lab: "σ<sub>v</sub> (1)", kind: "ref", k: 0, valid: true },
    s1: { lab: "σ<sub>v</sub> (2)", kind: "ref", k: 1, valid: true },
    s2: { lab: "σ<sub>v</sub> (3)", kind: "ref", k: 2, valid: true },
    C2: { lab: "C<sub>2</sub>?", kind: "rot", ang: 180, valid: false, fake: true },
    sh: { lab: "σ<sub>h</sub>?", kind: "refh", valid: false, fake: true },
  };
  function posAt(key, t) {
    const op = OPS[key];
    const H = HOME.map(p => p.slice()); let Np = NHOME.slice();
    if (op.kind === "rot") { const th = op.ang * Math.PI / 180 * t, c = Math.cos(th), s = Math.sin(th); for (const p of H) { const x = p[0], y = p[1]; p[0] = x * c - y * s; p[1] = x * s + y * c; } }
    if (op.kind === "ref") { const n = sigNormal(op.k); for (const p of H) { const d = p[0] * n[0] + p[1] * n[1]; p[0] -= 2 * t * d * n[0]; p[1] -= 2 * t * d * n[1]; } }
    if (op.kind === "refh") Np = [0, 0, hN - 2 * t * hN];
    return { H, Np };
  }
  function whoStays(key) {
    const { H } = posAt(key, 1); const st = [];
    H.forEach((p, i) => { if (Math.hypot(p[0] - HOME[i][0], p[1] - HOME[i][1]) < 1e-6) st.push(i + 1); });
    return st;
  }
  function play(key) {
    if (anim) cancelAnimationFrame(anim.raf);
    opKey = key; opT = 0; hNow = HOME.map(p => p.slice()); nNow = NHOME.slice(); stayed = null; build();
    const dur = OPS[key].kind === "id" ? 500 : 1500, t0 = performance.now();
    const tick = (now) => {
      const u = Math.min(1, (now - t0) / dur), e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
      opT = e; const p = posAt(key, e); hNow = p.H; nNow = p.Np; refreshAtoms();
      if (u < 1) anim.raf = requestAnimationFrame(tick);
      else { anim = null; if (OPS[key].valid) found.add(key); stayed = OPS[key].valid ? whoStays(key) : null; renderInfo(); setToast(toastFor()); renderChips(); }
    };
    anim = { raf: requestAnimationFrame(tick) };
  }
  function putBack() { if (anim) { cancelAnimationFrame(anim.raf); anim = null; } opKey = null; opT = 0; hNow = HOME.map(p => p.slice()); nNow = NHOME.slice(); stayed = null; build(); }
  function refreshAtoms() {
    // move existing atom meshes without rebuilding labels
    const kids = atomG.children; kids[0].position.copy(W(nNow));
    for (let i = 0; i < 3; i++) kids[1 + i].position.copy(W(hNow[i]));
    for (let i = 0; i < 3; i++) { const m = kids[4 + i], p = W(nNow), q = W(hNow[i]); const d = new THREE.Vector3().subVectors(q, p), L = d.length(); m.position.copy(p).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(UP, d.normalize()); m.scale.y = L; }
  }

  // ------------------------------------------------------------ toasts
  function toastFor() {
    if (step === "shape") {
      if (!opKey) return `Trigonal pyramid, point group <b>C<sub>3v</sub></b>. Play each move. A move is a symmetry operation when every atom lands where an identical atom was.`;
      if (anim) return "";
      const st = whoStays(opKey);
      const T = {
        E: `<b>E</b>: do nothing. Every H stays put (3 of 3).`,
        C3: `<b>C<sub>3</sub></b>: turn 120° about the axis. H1 → H2's place, H2 → H3's, H3 → H1's. <b>No H stays put.</b>`,
        C32: `<b>C<sub>3</sub><sup>2</sup></b>: turn 240° (two C<sub>3</sub> turns). A different operation from C<sub>3</sub>, from the same axis. <b>No H stays put.</b>`,
        s0: `<b>σ<sub>v</sub> (1)</b>: reflect through the plane holding the axis and H1. <b>H1 stays</b>; H2 and H3 swap.`,
        s1: `<b>σ<sub>v</sub> (2)</b>: the plane through H2. <b>H2 stays</b>; H1 and H3 swap.`,
        s2: `<b>σ<sub>v</sub> (3)</b>: the plane through H3. <b>H3 stays</b>; H1 and H2 swap.`,
        C2: `<span class="no">Not an operation.</span> A half turn puts the H atoms where there were none. No C<sub>2</sub> in NH<sub>3</sub>.`,
        sh: `<span class="no">Not an operation.</span> Reflecting through the H<sub>3</sub> plane sends N below it. No σ<sub>h</sub>, so not D<sub>3h</sub>: that needs a flat molecule.`,
      };
      return T[opKey] + (OPS[opKey].valid ? ` <span class="ok">✓</span>` : "");
    }
    if (step === "frag") {
      const s = SALC[salc];
      return `<b>${s.lab}</b> = ${s.f}. ${salc === "a1" ? "All three in phase: no node, lowest energy." : "One sign change, so one nodal plane (grey). Same energy as the other e."} Lobe size = each H's weight.`;
    }
    if (step === "match") {
      const g = groupOverlap(nOrb, mSalc), z = Math.abs(g.sum) < 1e-6;
      if (z) return NORB[nOrb].sym === SALC[mSalc].sym
        ? `<span class="no">No net overlap.</span> Both are e, but they are different members of the pair (x and y): the + and − overlaps cancel. Each p orbital has its own partner.`
        : `<span class="no">No net overlap.</span> ${NORB[nOrb].lab} is ${SUB(NORB[nOrb].sym === "a1" ? "a_1" : "e")} and H<sub>3</sub> ${SALC[mSalc].lab} is ${SALC[mSalc].sym === "a1" ? "a<sub>1</sub>" : "e"}: the + and − overlaps cancel. They cannot combine, whatever the phases.`;
      return `<span class="ok">Allowed.</span> ${NORB[nOrb].lab} and H<sub>3</sub> ${SALC[mSalc].lab} share a label. ${bonding ? "In phase: <b>bonding</b>." : "Out of phase: <b>antibonding</b>."} Group overlap ${fmt(bonding ? Math.abs(g.G) : -Math.abs(g.G))}.`;
    }
    if (step === "mo") {
      const l = lvOf(moKey);
      return `<b>${(valenceNum ? MOVAL : MOLAB)[moKey]}</b> · ${l.kind}. Lobe sizes from an extended Hückel calculation.`;
    }
    return "";
  }
  function setToast(h) { toast.hidden = !h; toast.innerHTML = h || ""; }
  const fmt = (x) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(2);

  // ------------------------------------------------------------ chips
  function chip(el, html, pressed, onClick, cls) {
    const b = document.createElement("button"); b.type = "button"; b.innerHTML = html; if (cls) b.className = cls;
    if (pressed !== null) b.setAttribute("aria-pressed", pressed ? "true" : "false");
    b.addEventListener("click", onClick); el.appendChild(b); return b;
  }
  function renderChips() {
    chipsEl.innerHTML = ""; chips2.innerHTML = "";
    if (step === "shape") {
      for (const k of Object.keys(OPS)) chip(chipsEl, (OPS[k].valid && found.has(k) ? "✓ " : "") + OPS[k].lab, opKey === k, () => play(k), OPS[k].fake ? "fake" : "");
      chip(chips2, "C<sub>3</sub> axis", showAxis, () => { showAxis = !showAxis; build(); });
      chip(chips2, "σ<sub>v</sub> planes", showPlanes, () => { showPlanes = !showPlanes; build(); });
      chip(chips2, "Put back", null, putBack);
      const c = document.createElement("span"); c.className = "cnt"; c.style.cssText = "align-self:center;font-size:13px;padding:0 4px;white-space:nowrap";
      const n = [...found].length; c.innerHTML = `Operations found: <b style="color:var(${n === 6 ? "--good" : "--accent"})">${n}</b> of 6`; chips2.appendChild(c);
    } else if (step === "frag") {
      for (const k of ["a1", "ex", "ey"]) chip(chipsEl, SALC[k].lab, salc === k, () => { salc = k; build(); });
      chip(chips2, "Nodal plane", showNode, () => { showNode = !showNode; build(); });
      chip(chips2, "Show N", showN, () => { showN = !showN; build(); });
    } else if (step === "match") {
      for (const k of ["s", "pz", "px", "py"]) chip(chipsEl, NORB[k].lab, nOrb === k, () => { nOrb = k; build(); });
      for (const k of ["a1", "ex", "ey"]) chip(chips2, "H<sub>3</sub> " + SALC[k].lab, mSalc === k, () => { mSalc = k; build(); });
      chip(chips2, "Bonding", bonding, () => { bonding = true; build(); });
      chip(chips2, "Antibonding", !bonding, () => { bonding = false; build(); });
    } else if (step === "mo") {
      for (const k of ["2a1", "1ex", "1ey", "3a1", "2ex", "2ey", "4a1"]) chip(chipsEl, (valenceNum ? MOVAL : MOLAB)[k], moKey === k, () => { moKey = k; build(); });
    }
  }

  // ------------------------------------------------------------ info panel
  function ttl(part, h3, badge) {
    return `<div class="ttl"><div><div class="part">${part}</div><h3>${h3}</h3></div>${badge ? `<div class="badge ans">${badge}</div>` : ""}</div>`;
  }
  function infoShape() {
    let h = ttl("Part 1 · Shape and symmetry", "NH<sub>3</sub> is C<sub>3v</sub>", `<b>6</b><span>operations</span>`);
    h += `<div class="sheet"><div class="k">Elements and the operations they give · tap to play</div><table class="t"><thead><tr><th>Element</th><th>Operations</th><th class="n">H left in place</th></tr></thead><tbody>`;
    const row = (key, el, ops, stay) => `<tr data-op="${key}" class="${opKey === key ? "on" : ""}"><td>${el}</td><td>${ops}</td><td class="n ans">${stay}</td></tr>`;
    h += row("E", "Identity", "E", 3) + row("C3", "C<sub>3</sub> axis through N", "C<sub>3</sub>, C<sub>3</sub><sup>2</sup>", 0) + row("s0", "3 σ<sub>v</sub> planes, each holds one N–H", "σ<sub>v</sub>, σ<sub>v</sub>′, σ<sub>v</sub>″", 1);
    h += `<tr class="tot ans"><td colspan="2">Total</td><td class="n">6 operations</td></tr></tbody></table>`;
    h += `<div class="note">Not present: σ<sub>h</sub>, <i>i</i>, C<sub>2</sub>. Try the dashed chips. Flat NH<sub>3</sub> would be D<sub>3h</sub>.</div></div>`;
    h += `<div class="sheet"><div class="k">Where a<sub>1</sub> + e comes from</div>`;
    h += `<div class="note" style="color:var(--ink)">Count the H 1s orbitals each operation leaves in place: E <b>3</b>, C<sub>3</sub> <b>0</b>, σ<sub>v</sub> <b>1</b>. That set (3, 0, 1) reduces to <b>a<sub>1</sub> + e</b> in C<sub>3v</sub>: one all-in-phase combination and a degenerate pair.</div>`;
    if (stayed) h += `<div class="read">Last move left <b>${stayed.length}</b> H in place${stayed.length ? ` (H${stayed.join(", H")})` : ""}.</div>`;
    h += `</div>`;
    h += `<div class="sheet"><div class="k">Labels</div><div class="note" style="color:var(--ink)"><b>a<sub>1</sub></b>: unchanged by every operation. <b>e</b>: a pair that turn into mixtures of each other under C<sub>3</sub>; always the same energy.<br>N 2s and 2p<sub>z</sub> are a<sub>1</sub>; 2p<sub>x</sub> and 2p<sub>y</sub> together are e.</div></div>`;
    h += `<div class="call"><b class="h">Watch for:</b> D<sub>3h</sub> instead of C<sub>3v</sub>, and a linear H–H–H fragment in 1.1. The manual says the H atoms stay where they sit in NH<sub>3</sub>.</div>`;
    return h;
  }
  function fragSVG() {
    const ink = "var(--ink)", mut = "var(--muted)", acc = "var(--accent)";
    const yH = 70, ya = 112, ye = 44; let s = `<svg viewBox="0 0 300 150" role="img" aria-label="H3 fragment MO diagram">`;
    s += `<line x1="14" y1="138" x2="14" y2="12" stroke="${mut}" stroke-width="1.2"/><text x="20" y="18" font-size="11" fill="${mut}">E</text>`;
    for (const x of [52, 76, 100]) s += `<line x1="${x - 9}" y1="${yH}" x2="${x + 9}" y2="${yH}" stroke="${ink}" stroke-width="2"/>`;
    s += `<text x="76" y="${yH + 18}" font-size="11" text-anchor="middle" fill="${ink}">3 × H 1s</text><text x="76" y="${yH + 31}" font-size="10" text-anchor="middle" fill="${mut}">−13.6 eV</text>`;
    const lvl = (k, x, y, w) => `<g class="lvl ${salc === k ? "on" : ""}" data-s="${k}"><rect x="${x - w / 2 - 4}" y="${y - 10}" width="${w + 8}" height="20" fill="transparent"/><line class="l" x1="${x - w / 2}" y1="${y}" x2="${x + w / 2}" y2="${y}" stroke="${salc === k ? acc : ink}" stroke-width="${salc === k ? 3.2 : 2}"/></g>`;
    s += lvl("a1", 210, ya, 36) + lvl("ex", 188, ye, 30) + lvl("ey", 232, ye, 30);
    s += `<line x1="111" y1="${yH}" x2="190" y2="${ya}" stroke="${mut}" stroke-dasharray="3 3"/><line x1="111" y1="${yH}" x2="171" y2="${ye}" stroke="${mut}" stroke-dasharray="3 3"/>`;
    s += `<text x="236" y="${ya + 4}" font-size="12" font-weight="700" fill="${ink}">a<tspan baseline-shift="sub" font-size="9">1</tspan></text>`;
    s += `<text x="255" y="${ye + 4}" font-size="12" font-weight="700" fill="${ink}">e</text>`;
    s += `<text x="188" y="${ye - 10}" font-size="9.5" text-anchor="middle" fill="${mut}">x</text><text x="232" y="${ye - 10}" font-size="9.5" text-anchor="middle" fill="${mut}">y</text>`;
    s += `<text x="285" y="${(ya + yH) / 2 + 4}" font-size="9.5" text-anchor="end" fill="${mut}">−2|β|</text><text x="285" y="${(ye + yH) / 2 + 4}" font-size="9.5" text-anchor="end" fill="${mut}">+|β|</text>`;
    return s + `</svg>`;
  }
  function infoFrag() {
    const s = SALC[salc];
    let h = ttl("Part 1 · 1.1 and 1.2 · 5 + 4 marks", `H<sub>3</sub> fragment: ${s.lab}`, `<b>3</b><span>in, 3 out</span>`);
    h += `<div class="sheet"><div class="k">This combination</div><div class="eqn">${s.lab} = ${s.f}</div><table class="t"><thead><tr><th>H</th><th class="n">Coefficient</th><th>Phase</th></tr></thead><tbody>`;
    s.c.forEach((c, i) => { h += `<tr><td>H${i + 1}</td><td class="n">${Math.abs(c) < 1e-9 ? "0" : fmt(c)}</td><td>${Math.abs(c) < 1e-9 ? '<span class="note">on the node</span>' : c > 0 ? '<span class="ph p">+</span>' : '<span class="ph n">−</span>'}</td></tr>`; });
    h += `</tbody></table><div class="note">Nodes: ${s.node}. Normalised: (1/√3), (1/√6), (1/√2).</div></div>`;
    h += `<div class="sheet mo"><div class="k">Fragment diagram · tap a level</div>${fragSVG()}<div class="note">Simple Hückel picture: a<sub>1</sub> drops 2|β|, each e rises |β|, so the average stays at −13.6 eV. H···H in NH<sub>3</sub> is 1.62 Å, so the split is small.</div></div>`;
    h += `<div class="sheet"><div class="k">Scheme · 1.1 (5) and 1.2 (4)</div><div class="note" style="color:var(--ink)">1.1: shape 1 · phase 1 · labels 1 · overlap 2.<br>1.2: energy scale 1 · AOs 1 · MOs labelled 1 · splitting and order 1.</div></div>`;
    h += `<div class="call"><b class="h">Watch for:</b> φ<sub>1</sub> − φ<sub>2</sub>, φ<sub>2</sub> − φ<sub>3</sub>, φ<sub>3</sub> − φ<sub>1</sub> as the three combinations. They add to zero (only two are independent) and the all-in-phase one is missing.</div>`;
    return h;
  }
  function bars(g) {
    const max = 0.6; const w = (v) => Math.min(50, Math.abs(v) / max * 50);
    const bar = (lab, v, cls) => `<div class="b ${cls || ""}"><span>${lab}</span><span class="trk"><span class="fill" style="${v >= 0 ? "left:50%" : "right:50%"};width:${w(v)}%;background:var(${v >= 0 ? "--good" : "--bad"})"></span></span><span class="v">${Math.abs(v) < 5e-4 ? "0.00" : fmt(v)}</span></div>`;
    const flip = Math.abs(g.sum) < 1e-6 ? 1 : (bonding ? Math.sign(g.sum) : -Math.sign(g.sum));
    let h = `<div class="bars">`;
    g.parts.forEach((p, i) => { h += bar(`H${i + 1}`, p * flip); });
    h += bar("Sum", g.sum * flip, "sum") + `</div>`;
    return h;
  }
  function infoMatch() {
    const g = groupOverlap(nOrb, mSalc), z = Math.abs(g.sum) < 1e-6;
    let h = ttl("Part 1 · 1.3 · 6 marks", `${NORB[nOrb].lab} with H<sub>3</sub> ${SALC[mSalc].lab}`, z ? `<b>0</b><span>no overlap</span>` : `<b>${Math.abs(g.G).toFixed(2)}</b><span>overlap</span>`);
    h += `<div class="sheet"><div class="k">Overlap with each H · coefficient × S(N, H)</div>${bars(g)}`;
    h += z ? `<div class="read"><span class="no">Zero.</span> The H contributions cancel exactly. Symmetry forbids this pair.</div>`
           : `<div class="read"><span class="ok">Allowed.</span> Group overlap ⟨N | H<sub>3</sub>⟩ = <b>${fmt(bonding ? Math.abs(g.G) : -Math.abs(g.G))}</b>: ${bonding ? "in phase, bonding" : "out of phase, antibonding"}.</div>`;
    h += `<div class="note">S from Slater orbitals at the real NH<sub>3</sub> geometry (N ζ 1.95, H ζ 1.30): S(2s, H) = ${Sv.sH.toFixed(2)}, S(2p<sub>x</sub>, H1) = ${a.toFixed(2)}, S(2p<sub>z</sub>, H) = ${Sv.pzH.toFixed(2)}.</div></div>`;
    h += `<div class="sheet"><div class="k">Every pair · tap to load</div><div class="grid"><div></div><div class="h">a<sub>1</sub></div><div class="h">e(x)</div><div class="h">e(y)</div>`;
    for (const n of ["s", "pz", "px", "py"]) {
      h += `<div class="h" style="text-align:left">${NORB[n].lab.replace("N ", "")}</div>`;
      for (const s of ["a1", "ex", "ey"]) {
        const gg = groupOverlap(n, s), zz = Math.abs(gg.sum) < 1e-6, on = n === nOrb && s === mSalc;
        h += `<button type="button" data-n="${n}" data-s="${s}" class="${zz ? "zero" : ""} ${on ? "on" : ""}">${student ? "?" : zz ? "0" : Math.abs(gg.G).toFixed(2)}</button>`;
      }
    }
    h += `</div><div class="note">Non-zero only where the labels match: 2s and 2p<sub>z</sub> with a<sub>1</sub>; 2p<sub>x</sub> with e(x); 2p<sub>y</sub> with e(y).</div></div>`;
    h += `<div class="sheet"><div class="k">Scheme · 1.3 (6)</div><div class="note" style="color:var(--ink)">Shape 1 · phase 1 · labels 2 · overlap 2: each N orbital drawn with its partner, signs matched where lobes meet.</div></div>`;
    return h;
  }
  function moSVG() {
    const ink = "var(--ink)", mut = "var(--muted)", acc = "var(--accent)";
    const top = 18, bot = 250, Emax = 2, Emin = -29;
    const Y = (E) => top + (Emax - E) / (Emax - Emin) * (bot - top);
    const xN = 62, xM = 170, xH = 282;
    let s = `<svg viewBox="0 0 340 300" role="img" aria-label="NH3 molecular orbital diagram">`;
    s += `<line x1="12" y1="${bot + 4}" x2="12" y2="${top - 4}" stroke="${mut}" stroke-width="1.1"/><text x="17" y="${top}" font-size="10" fill="${mut}">E</text>`;
    // fill electrons by aufbau (Hund) into valence levels
    const occ = {}; let left = nVal;
    for (const l of LV) { const cap = 2 * l.deg; const n = Math.min(cap, left); left -= n; occ[l.k] = n; }
    const arrows = (x, y, n) => {
      let t = ""; if (n >= 1) t += `<path d="M${x - (n === 2 ? 3.5 : 0)},${y + 6} v-13" stroke="${ink}" stroke-width="1.4" marker-end="url(#mah)"/>`;
      if (n === 2) t += `<path d="M${x + 3.5},${y - 6} v13" stroke="${ink}" stroke-width="1.4" marker-end="url(#mah)"/>`; return t;
    };
    s += `<defs><marker id="mah" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="${ink}"/></marker></defs>`;
    const dash = (x1, y1, x2, y2, op) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${mut}" stroke-dasharray="3 3" opacity="${op || 1}"/>`;
    // AOs
    const yS = Y(-25.6), yP = Y(-13.2), ya = Y(-14.8), ye = Y(-13.0);
    s += `<line x1="${xN - 14}" y1="${yS}" x2="${xN + 14}" y2="${yS}" stroke="${ink}" stroke-width="2"/>` + arrows(xN, yS, 2);
    for (const dx of [-26, 0, 26]) s += `<line x1="${xN + dx - 10}" y1="${yP}" x2="${xN + dx + 10}" y2="${yP}" stroke="${ink}" stroke-width="2"/>` + arrows(xN + dx, yP, 1);
    s += `<text x="${xN - 42}" y="${yP + 4}" font-size="11" font-weight="700" fill="${ink}" text-anchor="end">2p</text><text x="${xN - 20}" y="${yS + 4}" font-size="11" font-weight="700" fill="${ink}" text-anchor="end">2s</text>`;
    s += `<text x="${xN}" y="${bot + 22}" font-size="11" font-weight="700" fill="${ink}" text-anchor="middle">N</text>`;
    s += `<line x1="${xH - 14}" y1="${ya}" x2="${xH + 14}" y2="${ya}" stroke="${ink}" stroke-width="2"/>` + arrows(xH, ya, 2);
    s += `<line x1="${xH - 30}" y1="${ye}" x2="${xH - 4}" y2="${ye}" stroke="${ink}" stroke-width="2"/><line x1="${xH + 4}" y1="${ye}" x2="${xH + 30}" y2="${ye}" stroke="${ink}" stroke-width="2"/>` + arrows(xH - 17, ye, 1);
    s += `<text x="${xH + 34}" y="${ya + 4}" font-size="11" font-weight="700" fill="${ink}">a<tspan baseline-shift="sub" font-size="8">1</tspan></text><text x="${xH + 34}" y="${ye - 4}" font-size="11" font-weight="700" fill="${ink}">e</text>`;
    s += `<text x="${xH}" y="${bot + 22}" font-size="11" font-weight="700" fill="${ink}" text-anchor="middle">H<tspan baseline-shift="sub" font-size="8">3</tspan></text>`;
    // correlation lines
    const yM = (k) => Y(LV.find(l => l.k === k).E);
    s += dash(xN + 15, yS, xM - 22, yM("2a1")) + dash(xN + 15, yS, xM - 22, yM("4a1"), 0.4) + dash(xN + 37, yP, xM - 22, yM("3a1")) + dash(xN + 37, yP, xM - 44, yM("1e")) + dash(xN + 37, yP, xM - 44, yM("2e"));
    s += dash(xH - 15, ya, xM + 22, yM("2a1")) + dash(xH - 15, ya, xM + 22, yM("4a1")) + dash(xH - 15, ya, xM + 22, yM("3a1"), 0.4) + dash(xH - 31, ye, xM + 44, yM("1e")) + dash(xH - 31, ye, xM + 44, yM("2e"));
    // MO levels
    for (const l of LV) {
      const y = Y(l.E), on = lvOf(moKey) === l, c = on ? acc : ink, sw = on ? 3.2 : 2;
      const lab = (valenceNum ? l.v : l.lab).replace(/_(\d)/, '<tspan baseline-shift="sub" font-size="8">$1</tspan>');
      s += `<g class="lvl ${on ? "on" : ""}" data-l="${l.k}"><rect x="${xM - 50}" y="${y - 11}" width="100" height="22" fill="transparent"/>`;
      if (l.deg === 1) s += `<line class="l" x1="${xM - 20}" y1="${y}" x2="${xM + 20}" y2="${y}" stroke="${c}" stroke-width="${sw}"/>` + arrows(xM, y, occ[l.k]);
      else {
        const a1 = occ[l.k] >= 2 ? (occ[l.k] >= 3 ? 2 : 1) : occ[l.k], a2 = occ[l.k] >= 4 ? 2 : occ[l.k] >= 2 ? 1 : 0;
        s += `<line class="l" x1="${xM - 44}" y1="${y}" x2="${xM - 6}" y2="${y}" stroke="${c}" stroke-width="${sw}"/><line class="l" x1="${xM + 6}" y1="${y}" x2="${xM + 44}" y2="${y}" stroke="${c}" stroke-width="${sw}"/>` + arrows(xM - 25, y, a1) + arrows(xM + 25, y, a2);
      }
      s += `<text x="${xM + (l.deg === 1 ? 26 : 48)}" y="${y - 3}" font-size="11" font-weight="700" fill="${c}" stroke="var(--panel)" stroke-width="3" paint-order="stroke">${lab}</text></g>`;
    }
    // core
    const yc = bot + 6;
    s += `<text x="${xM}" y="${yc + 34}" font-size="9.5" fill="${mut}" text-anchor="middle">1a₁ (N 1s core, 2 e⁻) far below</text>`;
    return s + `</svg>`;
  }
  function config() {
    const occ = {}; let left = nVal; for (const l of LV) { const n = Math.min(2 * l.deg, left); left -= n; occ[l.k] = n; }
    const parts = []; if (!valenceNum) parts.push("(1a₁)²");
    const name = { "2a1": valenceNum ? "1a₁" : "2a₁", "1e": "1e", "3a1": valenceNum ? "2a₁" : "3a₁", "2e": "2e*", "4a1": valenceNum ? "3a₁*" : "4a₁*" };
    const sup = (n) => "⁰¹²³⁴"[n];
    for (const l of LV) if (occ[l.k]) parts.push(`(${name[l.k]})${sup(occ[l.k])}`);
    return parts.join(" ");
  }
  function infoMO() {
    const l = lvOf(moKey);
    let h = ttl("Part 1 · 1.4 and 1.5 · 8 + 3 marks", `${(valenceNum ? MOVAL : MOLAB)[moKey]} · ${l.kind}`, `<b>${nVal}</b><span>valence e⁻</span>`);
    h += `<div class="sheet ans"><div class="note" style="color:var(--ink)">${l.desc}</div></div>`;
    h += `<div class="sheet mo"><div class="k">MO diagram · tap a level</div>${moSVG()}`;
    h += `<div class="ctl2"><button type="button" id="eAdd">Add electron</button><button type="button" id="eFill">Fill 8</button><button type="button" id="eEmpty">Empty</button></div></div>`;
    h += `<div class="sheet"><div class="k">1.5 · Configuration</div><div class="cfg ans">${config()}</div>`;
    h += `<div class="ctl2"><button type="button" id="eNum" aria-pressed="${valenceNum}">Valence-only numbering</button></div>`;
    h += `<div class="note">Either numbering is right if it matches the student's own diagram. Six bonding electrons (2a<sub>1</sub>, 1e) make three N–H bonds; 3a<sub>1</sub> is the lone pair.</div></div>`;
    h += `<div class="call"><b class="h">Sheet energies:</b> the sheet lists N 2s and N 2p both at −51.74 eV. Real valence values: 2s −25.6, 2p −13.2, H 1s −13.6 eV (used here). Decide up front whether level 2s and 2p cost the "AOs correct" mark.</div>`;
    h += `<div class="note">Levels are qualitative: filled order as photoelectron spectroscopy gives (first ionisation about 10 to 11 eV, from 3a<sub>1</sub>); empty order from extended Hückel. Scheme 1.4: energy scale 1 · AOs 1 · MOs labelled 2 · MOs correct 3 · order 1. 1.5: order 1 · electrons 2.</div>`;
    return h;
  }
  function renderInfo() {
    info.innerHTML = step === "shape" ? infoShape() : step === "frag" ? infoFrag() : step === "match" ? infoMatch() : infoMO();
    info.querySelectorAll("tr[data-op]").forEach(tr => tr.addEventListener("click", () => play(tr.dataset.op)));
    info.querySelectorAll("g[data-s]").forEach(g => g.addEventListener("click", () => { salc = g.dataset.s; build(); }));
    info.querySelectorAll("button[data-n]").forEach(b => b.addEventListener("click", () => { nOrb = b.dataset.n; mSalc = b.dataset.s; build(); }));
    info.querySelectorAll("g[data-l]").forEach(g => g.addEventListener("click", () => { const l = LV.find(x => x.k === g.dataset.l); moKey = l.mos.includes(moKey) && l.mos.length > 1 ? l.mos[(l.mos.indexOf(moKey) + 1) % 2] : l.mos[0]; build(); }));
    const on = (id, f) => { const b = $(id); if (b) b.addEventListener("click", f); };
    on("eAdd", () => { nVal = nVal >= 8 ? 0 : nVal + 1; renderInfo(); });
    on("eFill", () => { nVal = 8; renderInfo(); });
    on("eEmpty", () => { nVal = 0; renderInfo(); });
    on("eNum", () => { valenceNum = !valenceNum; build(); });
  }
  function syncControls() {
    document.querySelectorAll("#mStep button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === step ? "true" : "false"));
    $("mLabels").setAttribute("aria-pressed", showLabels ? "true" : "false");
  }
  document.querySelectorAll("#mStep button").forEach(b => b.addEventListener("click", () => {
    if (anim) { cancelAnimationFrame(anim.raf); anim = null; }
    step = b.dataset.v; opKey = null; hNow = HOME.map(p => p.slice()); nNow = NHOME.slice(); stayed = null; build();
  }));
  $("mLabels").addEventListener("click", () => { showLabels = !showLabels; build(); });
  $("mReset").addEventListener("click", () => { resetView(); fit(); });
  $("mDown").addEventListener("click", () => { root.quaternion.setFromEuler(new THREE.Euler(Math.PI / 2, 0, 0, "XYZ")); fit(); });

  // ------------------------------------------------------------ view
  function fit() {
    const R = 4.6, vf = camera.fov * Math.PI / 180, hf = 2 * Math.atan(Math.tan(vf / 2) * camera.aspect);
    camera.position.set(0, 0, R / Math.sin(Math.min(vf, hf) / 2) * 1.02);
  }
  function resetView() { root.quaternion.setFromEuler(new THREE.Euler(0.55, 0.35, 0, "XYZ")); }
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
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); fit();
  }
  new ResizeObserver(resize).observe(stage);
  const tmp = new THREE.Vector3();
  function placeLabels() {
    const w = stage.clientWidth, h = stage.clientHeight; if (!w) return;
    for (const o of spans) { tmp.copy(W(o.get())).applyQuaternion(root.quaternion).project(camera); o.sp.style.left = ((tmp.x + 1) / 2 * w) + "px"; o.sp.style.top = ((1 - tmp.y) / 2 * h) + "px"; }
  }
  function loop() { if (active) { renderer.render(scene, camera); placeLabels(); } requestAnimationFrame(loop); }
  resetView(); applyTheme(); build(); resize(); requestAnimationFrame(loop);
  window.P1 = { setActive(v) { active = v; if (v) { applyTheme(); resize(); } }, setStudent(v) { student = v; renderInfo(); } };
})();
