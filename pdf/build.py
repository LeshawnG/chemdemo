"""Assemble the CHEM 1170 Lab 4 Wednesday companion as HTML (then printed to PDF by print.js)."""
import os
import figs as F

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = {k: f() for k, f in F.FIGS.items()}

# ---------- small text macros ----------
def s(x):
    return f"<sub>{x}</sub>"

A1 = "a" + s("1")
NH3 = "NH" + s("3")
H3 = "H" + s("3")
C3V = "C" + s("3v")
C3 = "C" + s("3")
SV = "σ" + s("v")
PZ = "2p" + s("z")
PX = "2p" + s("x")
PY = "2p" + s("y")
H2O = "H" + s("2") + "O"
H2S = "H" + s("2") + "S"
H2Se = "H" + s("2") + "Se"
H2Te = "H" + s("2") + "Te"
CH4 = "CH" + s("4")
SiH4 = "SiH" + s("4")
GeH4 = "GeH" + s("4")
SnH4 = "SnH" + s("4")
NA = "N" + s("A")
PHI = lambda n: "φ" + s(n)
cm3 = "cm<sup>3</sup>"
gcm3 = "g cm<sup>−3</sup>"
E = lambda n: f"10<sup>{n}</sup>"

TABS = ["At a glance", "Part 1", "Part 2", "Part 3", "Answer key"]
TOTAL = 11

CSS = open(os.path.join(HERE, "fonts.css")).read() + r"""
@page { size: 7.5in 10.6667in; margin: 0; }
* { box-sizing: border-box; }
:root {
  --ink:#1b2330; --muted:#5b6472; --rule:#dde1e7; --soft:#eef0f4; --blue:#1d4ed8;
  --pos:#2f67d8; --neg:#e0782f; --green:#0f766e; --greenbg:#effaf6; --greenbd:#a7e3cf;
  --amberbg:#fffbea; --amberbd:#ecd27a; --amber:#9a6700; --violetbg:#f6f3ff; --violetbd:#d9cdf6; --violet:#6d28d9;
  --notebg:#f6f7f9; --notebd:#dfe3e8;
}
html, body { margin:0; padding:0; background:#fff; }
body { font-family:'IBM Plex Sans', 'Inter', sans-serif; color:var(--ink); font-size:11.2px; line-height:1.45;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page { width:720px; height:1024px; padding:20px 34px 0; position:relative; overflow:hidden; page-break-after:always; break-after:page; }
.page:last-child { page-break-after:auto; break-after:auto; }
nav { display:flex; gap:6px; padding-bottom:12px; border-bottom:1px solid var(--rule); margin-bottom:12px; }
nav span { flex:1; text-align:center; background:var(--soft); color:#4a5361; font-weight:600; font-size:10.5px; padding:5px 0; border-radius:6px; }
nav span.on { background:var(--blue); color:#fff; }
.eyebrow { font-size:9.5px; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color:var(--muted); margin:0 0 2px; }
h1 { font-size:21px; line-height:1.2; margin:0 0 10px; font-weight:700; letter-spacing:-.01em; }
h2 { font-size:13px; margin:12px 0 6px; font-weight:700; }
p { margin:0 0 6px; }
.lead { color:#3a4351; margin-bottom:8px; }
.row { display:flex; gap:10px; }
.row > * { flex:1; min-width:0; }
.box { border-radius:8px; padding:8px 11px 7px; margin:0 0 9px; }
.box .lab { font-size:9px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin-bottom:3px; }
.key { border:1px solid #9aa3b2; }
.key .lab { color:#3a4351; }
.coach { background:var(--greenbg); border:1px solid var(--greenbd); }
.coach .lab { color:var(--green); }
.coach dl { display:grid; grid-template-columns:118px 1fr; gap:3px 10px; margin:0; }
.coach dt { color:var(--green); font-weight:700; }
.coach dd { margin:0; }
.trap { background:var(--amberbg); border:1px solid var(--amberbd); }
.trap .lab { color:var(--amber); }
.work { background:var(--violetbg); border:1px solid var(--violetbd); }
.work .lab { color:var(--violet); }
.ans { background:#f0f6ff; border:1px solid #bcd0f5; }
.ans .lab { color:var(--blue); }
.note { background:var(--notebg); border:1px solid var(--notebd); }
.note .lab { color:var(--muted); }
ul { margin:2px 0 4px; padding-left:16px; }
li { margin:1px 0; }
table { width:100%; border-collapse:collapse; margin:0 0 9px; }
th.nt { text-transform:none; letter-spacing:0; font-size:10px; }
th { font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); text-align:left; padding:4px 6px; border-bottom:1px solid #c9ced6; }
td { padding:4px 6px; border-bottom:1px solid var(--rule); vertical-align:top; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
tr.hl td { background:#f0f6ff; font-weight:600; }
.chip { display:inline-block; font-size:8.6px; font-weight:700; letter-spacing:.04em; padding:1px 6px; border-radius:4px; white-space:nowrap; }
.c-amber { background:#fdeec2; color:#7a5200; }
.c-blue { background:#dde7fb; color:#1e3f9a; }
.c-red { background:#fde0d6; color:#9a3412; }
.c-grey { background:#e9ecf0; color:#465060; }
.fig { display:block; margin:0 auto 6px; max-width:100%; height:auto; }
.figwrap { text-align:center; }
.cap { font-size:9.5px; color:var(--muted); text-align:center; margin:-2px 0 8px; }
.mono { font-family:'IBM Plex Mono', monospace; font-size:10.5px; }
.eq { font-family:'IBM Plex Sans'; background:#fff; border:1px solid var(--violetbd); border-radius:6px; padding:6px 9px; margin:4px 0; line-height:1.7; }
.marks { display:grid; grid-template-columns:auto 1fr; gap:2px 10px; }
.marks b { white-space:nowrap; }
footer { position:absolute; left:34px; right:34px; bottom:14px; border-top:1px solid var(--rule); padding-top:6px; display:flex; justify-content:space-between; font-size:9px; color:var(--muted); }
/* cover */
.cover { background:linear-gradient(180deg,#eef2fb 0%, #ffffff 46%); padding-top:120px; }
.cover .eyebrow { margin-bottom:10px; }
.cover h1 { font-size:38px; margin-bottom:12px; }
.cover .lead { font-size:13px; max-width:560px; margin-bottom:22px; }
.toc { display:flex; flex-direction:column; gap:6px; margin-bottom:16px; }
.toc div { display:grid; grid-template-columns:170px 1fr; border:1px solid #cfd5de; border-radius:7px; padding:7px 11px; background:#fff; }
.toc b { font-weight:600; }
.toc span { color:var(--muted); }
.legend { display:flex; gap:6px; margin-bottom:12px; }
.legend span { font-size:9px; font-weight:700; letter-spacing:.06em; padding:3px 8px; border-radius:5px; border:1px solid; }
.small { font-size:9.8px; color:var(--muted); }
.tight td { padding:3px 6px; }
.k-table td:first-child { font-weight:700; white-space:nowrap; }
"""


def page(n, tab, body, cover=False):
    navhtml = "" if cover else "<nav>" + "".join(
        f'<span class="{"on" if t == tab else ""}">{t}</span>' for t in TABS) + "</nav>"
    foot = "" if cover else (f"<footer><span>Lab 4 Companion · CHEM 1170 Week 11 · Wednesday</span>"
                             f"<span>{n} / {TOTAL}</span></footer>")
    cls = "page cover" if cover else "page"
    return f'<section class="{cls}">{navhtml}{body}{foot}</section>'


def box(kind, label, inner, style=""):
    st = f' style="{style}"' if style else ""
    return f'<div class="box {kind}"{st}><div class="lab">{label}</div>{inner}</div>'


def coach(show, say, watch):
    return box("coach", "Coaching", f"<dl><dt>Show it</dt><dd>{show}</dd><dt>Say</dt><dd>{say}</dd>"
                                    f"<dt>Watch for</dt><dd>{watch}</dd></dl>")


pages = []

# ---------------------------------------------------------------- 1 cover
pages.append(page(1, None, f"""
<div class="eyebrow">CHEM 1170 · Laboratory 4 · Week 11 · Wednesday stream</div>
<h1>Lab 4 Companion</h1>
<p class="lead">Molecular orbital theory and bonding. The Wednesday answer script worked in full: the {NH3} MO diagram
built from an {H3} fragment, copper and tungsten unit cells, and the Group 14 and 16 hydrides. Your understanding and
your bench coaching on the same page.</p>
<div class="toc">
 <div><b>At a glance</b><span>Running order, marks, hand-in, and where the sheet and the scheme don't line up</span></div>
 <div><b>Part 1 · Shape</b><span>Point group, symmetry labels, and why the H atoms go in as a fragment</span></div>
 <div><b>Part 1 · {H3} fragment</b><span>The three combinations and the fragment diagram (1.1, 1.2)</span></div>
 <div><b>Part 1 · Matching</b><span>Which N orbital meets which combination, and why (1.3)</span></div>
 <div><b>Part 1 · Full diagram</b><span>The {NH3} MO diagram and its configuration (1.4, 1.5)</span></div>
 <div><b>Part 2 · Geometry</b><span>Where the atoms touch in BCC and FCC, and the volume expressions (2.1, 2.2)</span></div>
 <div><b>Part 2 · Cu and W</b><span>Volumes, densities and which lattice each metal takes (2.3, 2.4)</span></div>
 <div><b>Part 3 · Hydrides</b><span>Table, plots and the explanation (3.1, 3.2)</span></div>
 <div><b>Answer key</b><span>One page for marking</span></div>
</div>
<div class="legend">
 <span style="border-color:#9aa3b2;color:#3a4351">KEY IDEA</span>
 <span style="border-color:#d9cdf6;color:#6d28d9;background:#f6f3ff">WORKING</span>
 <span style="border-color:#bcd0f5;color:#1d4ed8;background:#f0f6ff">ANSWER</span>
 <span style="border-color:#ecd27a;color:#9a6700;background:#fffbea">TRAP</span>
 <span style="border-color:#a7e3cf;color:#0f766e;background:#effaf6">COACHING</span>
 <span style="border-color:#dfe3e8;color:#5b6472;background:#f6f7f9">NOTE</span>
</div>
<p class="small">The supervisor mark scheme sets the mark allocations for every stream, but its worked values are for
the Monday set (Cr, Ag, Group 15 hydrides). Every Wednesday value in this guide is our own working, recomputed in code.
It is not the official scheme: mark to the scheme's allocations. Orbital colours: <b style="color:#2f67d8">blue +</b>,
<b style="color:#e0782f">orange −</b>.</p>
<div class="box note" style="margin-top:14px"><div class="lab">Built from</div>
<p>CHEM 1170 Laboratory 4 Week 11 manual (Dr. Michael M. Forde, version 2026.1) · Week 11 answer script, Wednesday · Week 11 lab supervisor mark scheme. All three are in the Lab 4 folder.</p>
<p style="margin:0">Checked: every volume, density, Kelvin value and RMM recomputed in code; the boiling points on the sheet compared with literature values.</p></div>
""", cover=True))

# ---------------------------------------------------------------- 2 at a glance
pages.append(page(2, "At a glance", f"""
<div class="eyebrow">Before the session</div>
<h1>At a glance</h1>
<table>
<tr><th style="width:74px">Part</th><th style="width:50px">Time</th><th style="width:42px">Marks</th><th>Students do</th><th>You look for</th></tr>
<tr><td><b>1</b> {NH3} MO</td><td>45 min</td><td>26</td><td>Shape and point group. The three {H3} combinations and their diagram. Match N orbitals to them. Full diagram. Configuration.</td>
<td>Three combinations from three H 1s. The e pair has nodes. N 2s below 2p. Matches by label only. Filled order 2{A1} &lt; 1e &lt; 3{A1}; 8 valence electrons.</td></tr>
<tr><td><b>2</b> Unit cells</td><td>60 min</td><td>31</td><td>Draw BCC and FCC with <i>a</i> and <i>r</i>. Volume expressions. Volume and density of Cu and W both ways. Pick the lattice.</td>
<td>Touching along the body diagonal (BCC) or face diagonal (FCC). pm to cm before cubing. <i>n</i> = 2 and 4. Units on every answer.</td></tr>
<tr><td><b>3</b> Hydrides</td><td>45 min</td><td>24</td><td>Table in K with RMM. Two plots. Explain the trends.</td>
<td>Kelvin conversion. Labelled axes. {H2O} called out for hydrogen bonding. Size and dispersion for the rest.</td></tr>
</table>
<div class="row">
{box("key", "Hand-in rules", "<p>On the answer sheet provided, by <b>5 pm the same day</b>, drop box for Chemistry Laboratory A. Diagrams <b>in ink</b>, not pencil. ID number, name and lab day on every sheet; <b>demonstrator's name</b> on the front page. Plots on graph paper, attached.</p>")}
{box("key", "What students need", "<p>Calculator, notebook, ruler, pencil and eraser for rough work, graph paper. No apparatus. They need a <b>periodic table</b>: the sheet gives no atomic masses and no Avogadro constant.</p>")}
</div>
<h2>Where the sheet and the scheme don't line up</h2>
<table class="tight">
<tr><th style="width:120px">Item</th><th style="width:96px">Status</th><th>What it means for you</th></tr>
<tr><td>Supervisor mark scheme</td><td><span class="chip c-blue">Monday values</span></td><td>Its allocations apply to every stream. Its worked values (Cr, Ag, Group 15) don't. Wednesday values: pages 8 and 9.</td></tr>
<tr><td>Mark totals</td><td><span class="chip c-red">60 vs 81</span></td><td>The summary table says 60. The parts add to 81 (26 + 31 + 24). Settle which denominator goes on the marks sheet before you start.</td></tr>
<tr><td>2.3 allocation</td><td><span class="chip c-amber">Ambiguous</span></td><td>"3 + 5 marks each" only reaches 16 if "each" means each metal. The density line lists four criteria for five marks. Page 8 has a reading.</td></tr>
<tr><td>"See spreadsheet"</td><td><span class="chip c-grey">Not supplied</span></td><td>The scheme sends you to a spreadsheet for values. It isn't in the folder. Page 8 has the full set.</td></tr>
<tr><td>N orbital energies</td><td><span class="chip c-amber">2s = 2p on sheet</span></td><td>Both given as −51.74 eV. In N, 2s lies about 12 eV below 2p (−25.6 and −13.2 eV). Page 6.</td></tr>
<tr><td>{GeH4} boiling point</td><td><span class="chip c-amber">−9 °C on sheet</span></td><td>Literature is −88 °C. With −9 °C the Group 14 plot rises, then falls. Page 9.</td></tr>
</table>
{box("trap", "Three traps", f'''<ul>
<li><b>Part 2, touching:</b> atoms touch along a diagonal, never along the edge. <i>a</i> = 2<i>r</i> is simple cubic and gives the wrong volume for both lattices.</li>
<li><b>Part 2, units:</b> 1 pm = {E("−10")} cm, and it gets cubed: {E("−30")}. Skipping the conversion, or not cubing it, throws ρ off by {E("20")} or more.</li>
<li><b>Part 1, matching:</b> an N orbital only combines with an {H3} combination of the same label. {PX} against {A1} gives zero net overlap.</li></ul>''')}
"""))

# ---------------------------------------------------------------- 3 Part 1 shape
pages.append(page(3, "Part 1", f"""
<div class="eyebrow">Part 1 · {NH3} MO diagram · 45 min · 26 marks</div>
<h1>Shape, symmetry, and why the H atoms go in as a fragment</h1>
<div class="row" style="align-items:flex-start">
 <div style="flex:0 0 430px">{FIG["FIG_NH3"]}</div>
 {box("key", "Key idea · <span style='text-transform:none'>" + C3V + "</span>", f"<p>A trigonal pyramid. Elements: E, one {C3} axis through N, three {SV} planes, each holding the axis and one N–H.</p><p><b>Six operations</b>: E, {C3}, {C3}<sup>2</sup>, {SV}, {SV}′, {SV}″.</p><p>No {chr(963)}<sub>h</sub> and no <i>i</i>: N sits off the {H3} plane. Flat {NH3} would be D<sub>3h</sub>.</p>")}
</div>
<div class="row">
{box("key", "Labels come from the operations", f"<p><b>{A1}</b>: unchanged by every operation ({C3} and each {SV}).</p><p><b>e</b>: a pair that turn into mixtures of each other under {C3}. Same energy, always drawn as two lines.</p><p>N 2s and {PZ} are {A1}. {PX} and {PY} together are e.</p>")}
{box("key", "Why a fragment", f"<p>The three H 1s orbitals are swapped into each other by {C3}, so none of them can meet N on its own terms.</p><p>Combine them first into three group orbitals that carry the {C3V} labels. Then N meets each combination as a single partner, matched by label.</p>")}
</div>
{box("work", "Where a1 + e comes from (only if a strong student asks)", f'''
<div class="row" style="align-items:center"><div style="flex:0 0 300px">
<table class="tight" style="margin:0"><tr><th></th><th class="num nt">E</th><th class="num nt">2{C3}</th><th class="num nt">3{SV}</th></tr>
<tr><td>A<sub>1</sub></td><td class="num">1</td><td class="num">1</td><td class="num">1</td></tr>
<tr><td>A<sub>2</sub></td><td class="num">1</td><td class="num">1</td><td class="num">−1</td></tr>
<tr><td>E</td><td class="num">2</td><td class="num">−1</td><td class="num">0</td></tr>
<tr class="hl"><td>3 × H 1s</td><td class="num">3</td><td class="num">0</td><td class="num">1</td></tr></table></div>
<div><p>Count the H 1s orbitals that stay put under each operation: 3, 0, 1. That set reduces to <b>A<sub>1</sub> + E</b>: A<sub>1</sub> = (3 + 0 + 3)/6 = 1, A<sub>2</sub> = (3 + 0 − 3)/6 = 0, E = (6 + 0 + 0)/6 = 1.</p>
<p>Students don't need the table. "One all-in-phase combination, plus a pair with a node" is the whole result.</p></div></div>''')}
<table class="tight">
<tr><th style="width:56px">Step</th><th>On the sheet</th><th class="num" style="width:80px">Marks</th><th style="width:60px">Page</th></tr>
<tr><td>—</td><td>Shape, point group, symmetry elements and operations</td><td class="num">not marked</td><td>this page</td></tr>
<tr><td>1.1</td><td>Sketch the orbital combinations of the {H3} fragment</td><td class="num">5</td><td>4</td></tr>
<tr><td>1.2</td><td>MO diagram for the {H3} fragment</td><td class="num">4</td><td>4</td></tr>
<tr><td>1.3</td><td>Sketch N orbitals overlapping the {H3} combinations</td><td class="num">6</td><td>5</td></tr>
<tr><td>1.4, 1.5</td><td>Full labelled MO diagram; electron configuration</td><td class="num">8 + 3</td><td>6</td></tr>
</table>
{coach("Hold a pen upright through N as the " + C3 + " axis. Turn a third of a turn: every H moves into the next one's place. Then a mirror: one H stays, two swap.",
       "\"Three H orbitals in, three combinations out. Build those first, then let N pick its partners by label.\"",
       "Students drawing N meeting each H separately. D<sub>3h</sub> instead of " + C3V + ". A linear H–H–H fragment: the manual says the H atoms stay where they sit in " + NH3 + ".")}
"""))

# ---------------------------------------------------------------- 4 H3 fragment
pages.append(page(4, "Part 1", f"""
<div class="eyebrow">Part 1 · 1.1 and 1.2 · 5 + 4 marks</div>
<h1>The {H3} fragment: three combinations, one diagram</h1>
<p class="lead">Looking down the {C3} axis from above N. H1 points along +x. Lobe size shows each H's weight in the combination.</p>
<div class="figwrap">{FIG["FIG_SALC"]}</div>
<div class="row" style="align-items:flex-start">
 <div style="flex:0 0 330px">{FIG["FIG_H3"]}</div>
 <div>
 {box("work", "Working", f"<p><b>{A1}</b> = ({PHI(1)} + {PHI(2)} + {PHI(3)})/√3. All in phase, no node.</p><p><b>e(x)</b> = (2{PHI(1)} − {PHI(2)} − {PHI(3)})/√6. H1 carries twice the weight.</p><p><b>e(y)</b> = ({PHI(2)} − {PHI(3)})/√2. H1 sits on the node.</p><p>One node each, so the two e combinations share an energy.</p>")}
 {box("key", "How far they split", f"<p>Simple Hückel picture: {A1} drops by <span style='white-space:nowrap'>2|β|</span>, each e rises by <span style='white-space:nowrap'>|β|</span>, so the average stays at the H 1s level. H···H in {NH3} is 1.62 Å (H<sub>2</sub> is 0.74 Å), so β is small and the splitting is modest.</p>")}
 </div>
</div>
<div class="row">
{box("note", "1.1 · 5 marks · scheme", "<div class='marks'><b>Shape 1</b><span>triangle seen down the axis</span><b>Phase 1</b><span>shading or +/− shown</span><b>Labels 1</b><span>a<sub>1</sub>, e (or clear names)</span><b>Overlap 2</b><span>in-phase lobes overlapping; a node between opposite phases</span></div><p class='small' style='margin-top:4px'>Right column: our reading of the scheme's words.</p>")}
{box("note", "1.2 · 4 marks · scheme", f"<div class='marks'><b>Energy scale 1</b><span>an E axis; H 1s at −13.6 eV</span><b>AOs 1</b><span>three H 1s, labelled</span><b>MOs 1</b><span>{A1} and e labelled</span><b>Order 1</b><span>{A1} below H 1s, e pair above, e drawn as two lines</span></div>")}
</div>
{coach("Draw the triangle, shade all three the same: one combination. Now make H1 opposite to the other two: a node appears. That's the e pair's job.",
       "\"Every sign change costs energy. No node is lowest; one node is higher. Two different one-node patterns, same energy.\"",
       f"Three combinations like {PHI(1)} − {PHI(2)}, {PHI(2)} − {PHI(3)}, {PHI(3)} − {PHI(1)}: they add to zero, so they aren't independent, and the all-in-phase one is missing. Equal lobe sizes in e(x) are a fair simplification at this level.")}
"""))

# ---------------------------------------------------------------- 5 matching
pages.append(page(5, "Part 1", f"""
<div class="eyebrow">Part 1 · 1.3 · 6 marks</div>
<h1>Which N orbital meets which combination</h1>
<div class="figwrap">{FIG["FIG_OVERLAP"]}</div>
<p class="cap">In-phase (bonding) overlap shown; flip the H signs for each antibonding partner. Dashed box: {PX} against {A1}. H1 meets the + lobe, H2 and H3 the − lobe, and the overlaps cancel, so symmetry forbids the pair.</p>
<table class="tight">
<tr><th>N orbital</th><th>Label</th><th>Partner on {H3}</th><th>What it gives</th></tr>
<tr><td>2s</td><td>{A1}</td><td>{A1}</td><td>2{A1} (bonding); antibonding share in 4{A1}*</td></tr>
<tr><td>{PZ}</td><td>{A1}</td><td>{A1}</td><td>3{A1}, the lone pair; antibonding share in 4{A1}*</td></tr>
<tr><td>{PX}, {PY}</td><td>e</td><td>e(x), e(y)</td><td>1e (bonding pair) and 2e* (antibonding pair)</td></tr>
<tr><td>1s</td><td>{A1}</td><td>none: far too deep</td><td>1{A1}, core, unchanged</td></tr>
</table>
<div class="row">
{box("key", "Count check", f"<p>4 N valence orbitals + 3 {H3} combinations = <b>7 valence MOs</b>: three {A1} (2{A1}, 3{A1}, 4{A1}*) and two e pairs (1e, 2e*). N 1s adds 1{A1}: 8 in all.</p><p>Three {A1} functions mix, so 3{A1} isn't pure {PZ}: some 2s mixes in and points it away from the H atoms. Symmetry decides which pairs are allowed; the energy gap decides how strongly they mix.</p>")}
{box("note", "1.3 · 6 marks · scheme", f"<div class='marks'><b>Shape 1</b><span>N orbital with the H positions around it</span><b>Phase 1</b><span>matching signs where lobes meet</span><b>Labels 2</b><span>N orbital and {H3} combination both named</span><b>Overlap 2</b><span>each N orbital with its correct partner: 2s and {PZ} with {A1}; {PX}, {PY} with e</span></div>")}
</div>
{coach("Put the N orbital in the middle of the triangle and ask which " + H3 + " pattern has the same signs in the same places.",
       "\"Find the H combination that looks like the N orbital. That's its partner. If the signs cancel, there's no bond.\"",
       f"2s paired with e. {PZ} paired with e. p orbitals drawn without signs, so overlap can't be judged. {PX} and {PY} each paired with the same e combination.")}
"""))

# ---------------------------------------------------------------- 6 full diagram
pages.append(page(6, "Part 1", f"""
<div class="eyebrow">Part 1 · 1.4 and 1.5 · 8 + 3 marks</div>
<h1>The {NH3} MO diagram</h1>
<div class="figwrap">{FIG["FIG_MO"]}</div>
<p class="cap">Qualitative. AO levels are valence orbital ionisation energies; MOs are placed in the order photoelectron spectroscopy gives, not calculated. Faint lines: minor contributions.</p>
<div class="row">
{box("ans", "1.5 · Configuration", f"<p>10 electrons (N 7, H 3): <b>(1{A1})<sup>2</sup> (2{A1})<sup>2</sup> (1e)<sup>4</sup> (3{A1})<sup>2</sup></b>.</p><p>Many texts drop the core and renumber: (1{A1})<sup>2</sup> (1e)<sup>4</sup> (2{A1})<sup>2</sup>. Either is right if it matches the student's own diagram.</p><p>Six electrons in bonding MOs (2{A1}, 1e): three N–H bonds. 3{A1} is the lone pair, pointing along {C3} away from the H atoms: why {NH3} is a base and a ligand. The first ionisation (about 10 to 11 eV) removes a 3{A1} electron.</p>")}
{box("note", "1.4 · 8 marks and 1.5 · 3 marks · scheme", f"<div class='marks'><b>Energy scale 1</b><span>an E axis</span><b>AOs 1</b><span>N 2s below 2p; {H3} {A1} and e</span><b>MOs labelled 2</b><span>symmetry labels on every MO</span><b>MOs correct 3</b><span>seven valence MOs from the right partners</span><b>Order 1</b><span>2{A1} &lt; 1e &lt; 3{A1} &lt; antibonding</span><b>1.5 order 1</b><span>MOs listed in energy order</span><b>1.5 electrons 2</b><span>2, 4, 2 in the filled MOs; 8 valence</span></div>")}
</div>
{box("trap", "The sheet's orbital energies", f"<p>The sheet gives N 2s and N 2p the same energy (−51.74 eV). The accepted valence values are N 2s −25.6 eV, N 2p −13.2 eV, H 1s −13.6 eV, and this diagram uses them. A student who draws 2s and 2p level because the sheet said so has followed the data given. Worth deciding before marking whether that costs the \"AOs correct\" mark. The empty antibonding levels are drawn in the order an extended Hückel calculation gives (2e* below 4{A1}*); some textbooks swap them, and the scheme doesn't address it.</p>")}
"""))

# ---------------------------------------------------------------- 7 Part 2 geometry
pages.append(page(7, "Part 2", f"""
<div class="eyebrow">Part 2 · Unit cells · 60 min · 31 marks · 2.1 and 2.2</div>
<h1>BCC and FCC: find where the atoms touch</h1>
<div class="figwrap">{FIG["FIG_CELLS"]}</div>
<div class="figwrap">{FIG["FIG_SECTIONS"]}</div>
<p class="cap">Top: reduced spheres, so the cell is visible. Bottom: hard spheres in the plane where they touch. Green dots mark r and 3r along the diagonal.</p>
{box("work", "2.2 · Working", f'''<div class="row"><div>
<p><b>BCC</b>: atoms touch along the body diagonal.</p>
<div class="eq">√3 <i>a</i> = 4<i>r</i> &nbsp;⇒&nbsp; <i>a</i> = 4<i>r</i>/√3<br><i>V</i> = <i>a</i><sup>3</sup> = (4<i>r</i>/√3)<sup>3</sup> = 64<i>r</i><sup>3</sup>/(3√3) ≈ <b>12.32 <i>r</i><sup>3</sup></b></div></div>
<div><p><b>FCC</b>: atoms touch along a face diagonal.</p>
<div class="eq">√2 <i>a</i> = 4<i>r</i> &nbsp;⇒&nbsp; <i>a</i> = 2√2 <i>r</i><br><i>V</i> = <i>a</i><sup>3</sup> = (2√2 <i>r</i>)<sup>3</sup> = 16√2 <i>r</i><sup>3</sup> ≈ <b>22.63 <i>r</i><sup>3</sup></b></div></div></div>
<p style="margin-top:4px">The scheme writes these as BCC <i>V</i> = (4R/√3)<sup>3</sup> and FCC <i>V</i> = 16R<sup>3</sup>√2, with R the atomic radius. Same expressions.</p>''')}
<div class="row">
{box("note", "2.1 · 4 marks · 2.2 · 6 marks", "<div class='marks'><b>2.1 sketches 2</b><span>one BCC, one FCC</span><b>2.1 labels 2</b><span><i>a</i> on an edge, <i>r</i> on an atom, the touching diagonal</span><b>2.2</b><span>3 marks for each correct expression</span></div>")}
{box("trap", "The manual's hint", "<p>It calls the cube side R, then asks for \"the radius of the unit cell (half the length of the cube)\". Followed literally, students write <i>a</i>/2 = <i>r</i>, which is simple cubic. At the bench: <i>a</i> for the edge, <i>r</i> for the atom.</p>")}
</div>
{coach("Draw the diagonal through the touching atoms and count radii along it: r + 2r + r.",
       "\"Where do the spheres actually touch? That line is 4r. Now get its length in terms of a with Pythagoras.\"",
       "<i>a</i> = 2<i>r</i> for either lattice. BCC solved on the face diagonal. FCC solved on the body diagonal. R used for both edge and radius.")}
"""))

# ---------------------------------------------------------------- 8 Part 2 Cu, W
pages.append(page(8, "Part 2", f"""
<div class="eyebrow">Part 2 · 2.3 and 2.4 · 16 + 5 marks</div>
<h1>Copper and tungsten: volume, density, lattice</h1>
<p class="lead">Sheet: Cu <i>r</i> = 128 pm, measured 8.93 {gcm3}. W <i>r</i> = 137.1 pm, measured 19.25 {gcm3}.
Students supply <i>A</i> (Cu 63.55, W 183.84 g mol<sup>−1</sup>) and {NA} = 6.022 × {E("23")} mol<sup>−1</sup>.</p>
{box("work", "Worked through once · Cu as FCC", f'''<div class="eq">
<i>r</i> = 128 pm = 128 × {E("−10")} cm = 1.28 × {E("−8")} cm<br>
<i>V</i> = 16√2 <i>r</i><sup>3</sup> = 22.627 × (1.28 × {E("−8")} cm)<sup>3</sup> = 22.627 × 2.097 × {E("−24")} {cm3} = <b>4.745 × {E("−23")} {cm3}</b><br>
ρ = <i>nA</i> / (<i>V</i> {NA}) = (4 × 63.55 g mol<sup>−1</sup>) / (4.745 × {E("−23")} {cm3} × 6.022 × {E("23")} mol<sup>−1</sup>) = 254.2 g / 28.57 {cm3} = <b>8.90 {gcm3}</b></div>''')}
<table>
<tr><th></th><th class="num">Cu as BCC</th><th class="num">Cu as FCC</th><th class="num">W as BCC</th><th class="num">W as FCC</th></tr>
<tr><td>Edge <i>a</i> / pm</td><td class="num">295.6</td><td class="num">362.0</td><td class="num">316.6</td><td class="num">387.8</td></tr>
<tr><td><i>V</i> / {cm3}</td><td class="num">2.583 × {E("−23")}</td><td class="num">4.745 × {E("−23")}</td><td class="num">3.174 × {E("−23")}</td><td class="num">5.831 × {E("−23")}</td></tr>
<tr><td>Atoms per cell <i>n</i></td><td class="num">2</td><td class="num">4</td><td class="num">2</td><td class="num">4</td></tr>
<tr><td>ρ / {gcm3}</td><td class="num">8.17</td><td class="num"><b>8.90</b></td><td class="num"><b>19.24</b></td><td class="num">20.94</td></tr>
<tr><td>vs measured</td><td class="num">−8.5 %</td><td class="num"><b>−0.4 %</b></td><td class="num"><b>−0.1 %</b></td><td class="num">+8.8 %</td></tr>
</table>
<div class="row">
{box("ans", "2.4 · Which lattice", f"<p><b>Cu is FCC</b>: 8.90 against 8.93 measured. BCC would give 8.17, 8.5 % low.</p><p><b>W is BCC</b>: 19.24 against 19.25. FCC would give 20.94, 8.8 % high.</p><p>Both agree with the known structures: copper is cubic close packed, tungsten body-centred cubic.</p>")}
{box("key", "Why the answer is never close", "<p>For the same <i>r</i>, FCC is always 8.9 % denser than BCC (ratio 1.089). The packing fractions are 74 % and 68 %. So any metal's two candidates sit about 9 % apart, and a match within 1 % settles it.</p>")}
</div>
<div class="row">
{box("note", "2.3 · 16 marks · 2.4 · 5 marks · scheme", "<div class='marks'><b>Volume 3 each</b><span>equation 1 · values used 1 · answer with units 1</span><b>Density 5 each</b><span>equation 1 · values used 1 · conversions 1 · answer with units 1</span><b>2.4</b><span>rationale 3 · correct choice 2</span></div>")}
{box("note", "Our reading of 2.3 (an inference)", f"<p>(3 + 5) × 2 = 16 works if \"each\" means each metal. The fifth density mark isn't named; choosing <i>n</i> (2 or 4) is the obvious unlisted step. Rounding <i>A</i> (63.5 vs 63.55, 184 vs 183.84) or N<sub>A</sub> moves ρ by a few hundredths at most: treat ±0.05 {gcm3} as the same answer.</p>")}
</div>
{coach("Write the units into every line of the calculation and cancel them. If they don't end as g cm<sup>−3</sup>, something is missing.",
       "\"Convert r to cm first, then cube. The 10<sup>−10</sup> gets cubed too.\"",
       "r left in pm. 10<sup>−10</sup> not cubed. <i>n</i> = 1. <i>A</i> in kg mol<sup>−1</sup>. Densities with no units.")}
"""))

# ---------------------------------------------------------------- 9 Part 3 table/plots
pages.append(page(9, "Part 3", f"""
<div class="eyebrow">Part 3 · Hydrides · 45 min · 24 marks · 3.1</div>
<h1>Boiling points of the Group 14 and 16 hydrides</h1>
<table>
<tr><th>Compound</th><th class="num">b.p. / °C (sheet)</th><th class="num">b.p. / K</th><th class="num">RMM</th><th style="width:14px"></th><th>Compound</th><th class="num">b.p. / °C (sheet)</th><th class="num">b.p. / K</th><th class="num">RMM</th></tr>
<tr><td>{CH4}</td><td class="num">−164</td><td class="num">109.15</td><td class="num">16.04</td><td></td><td>{H2O}</td><td class="num">100</td><td class="num">373.15</td><td class="num">18.02</td></tr>
<tr><td>{SiH4}</td><td class="num">−112</td><td class="num">161.15</td><td class="num">32.12</td><td></td><td>{H2S}</td><td class="num">−60</td><td class="num">213.15</td><td class="num">34.08</td></tr>
<tr><td>{GeH4}</td><td class="num">−9</td><td class="num">264.15</td><td class="num">76.66</td><td></td><td>{H2Se}</td><td class="num">−41</td><td class="num">232.15</td><td class="num">80.99</td></tr>
<tr><td>{SnH4}</td><td class="num">−52</td><td class="num">221.15</td><td class="num">122.74</td><td></td><td>{H2Te}</td><td class="num">−2</td><td class="num">271.15</td><td class="num">129.62</td></tr>
</table>
<p class="small" style="margin-top:-4px">K = °C + 273.15; +273 is fine. RMM from standard atomic masses (H 1.008); one decimal place is fine.</p>
<div class="figwrap">{FIG["FIG_PLOTS"]}</div>
<p class="cap">Plotted from the sheet's values. Hollow point: {GeH4}'s literature boiling point (−88 °C).</p>
<div class="row">
{box("note", "3.1 · 16 marks · scheme", "<div class='marks'><b>Table 8</b><span>b.p. in K: 2 × 2 = 4; RMM: 2 × 2 = 4</span><b>Plots 8</b><span>axes 1 · labels 1 · points 1 · trendline 1, × 2</span></div><p class='small' style='margin-top:4px'>\"× 2\" fits two plots, or two series on one set of axes with a trendline each.</p>")}
{box("key", "Trendlines here", f"<p>A straight best-fit line through all four Group 16 points hides the point of the exercise. Joined points, or a line through {H2S}, {H2Se}, {H2Te} with {H2O} standing above it, both show the trend. Worth deciding which you accept for the trendline mark before marking.</p>")}
</div>
{box("trap", "GeH4 on the sheet", f"<p>The sheet gives {GeH4} as −9 °C (264 K). The literature value is −88 °C (185 K). With the sheet's value the Group 14 plot climbs to {GeH4} and drops to {SnH4}, which no bonding argument explains. Students will ask. One line that keeps everyone on the same footing: <b>\"Plot the number on the sheet. If a point doesn't fit the trend, say so, and say what the trend predicts.\"</b> ({CH4} is given as −164 °C against −161.5 °C: too small to matter.)</p>")}
"""))

# ---------------------------------------------------------------- 10 explanation
pages.append(page(10, "Part 3", f"""
<div class="eyebrow">Part 3 · 3.2 · 8 marks</div>
<h1>Explaining the trends</h1>
<p class="lead">Two questions for every series: is the molecule polar, and how big is it? The model answer below follows the scheme's four 2-mark points.</p>
{box("ans", "Model answer", f'''
<p><b>1 · Bonds within the molecules (2).</b> Every hydride is held together by covalent E–H σ bonds. O–H is strongly polar (electronegativity O 3.44, H 2.20); S–H, Se–H and Te–H much less so; C–H and Si–H only slightly. The Group 14 hydrides are <b>tetrahedral</b>, so their bond dipoles cancel and the molecules are nonpolar. The Group 16 hydrides are <b>bent</b>, so they are polar.</p>
<p><b>2 · Forces between the molecules (2).</b> Group 14: London dispersion forces only. Group 16: dispersion plus dipole–dipole forces; water also forms hydrogen bonds.</p>
<p><b>3 · The first member (2).</b> {H2O} boils at 373 K, about 170 K above where the {H2S}–{H2Te} trend puts it (about 200 K). O is small and very electronegative, so O–H is strongly polarised; the nearly bare H of one molecule is drawn to a lone pair on the O of the next. Each {H2O} can make up to four hydrogen bonds (two through its H atoms, two through its lone pairs), so boiling has to break an extended network. {CH4} is not anomalous: C–H is barely polar and C has no lone pair, so there is no hydrogen bonding and {CH4} is simply the lightest and lowest.</p>
<p><b>4 · Down each group (2).</b> Boiling point rises with size. Heavier hydrides have more electrons in larger, more polarisable clouds, so London forces get stronger, and more energy is needed to separate the molecules.</p>''')}
<div class="row">
{box("key", "Same mass, different polarity", f"<p>{SiH4} (M 32) boils at 161 K; {H2S} (M 34) at 213 K. Nearly the same number of electrons, so nearly the same dispersion. The 52 K gap is the dipole–dipole contribution. A good one to ask a student who has finished.</p>")}
{box("note", "The scheme's wording", f"<p>It says \"the first member for Group 5, 6, 7\": one scheme covers all streams (Monday and Tuesday have Group 15, Friday Group 17). For Wednesday that point is {H2O}. Group 14 is the control series: no first-member anomaly.</p>")}
</div>
{box("key", "Boiling breaks the forces between molecules, not the bonds inside them", f"<p>E–H bonds get <i>weaker</i> down a group, yet boiling points rise. Any answer that says \"bp rises because the bonds get stronger\" has mixed up the two kinds of interaction.</p>")}
{coach(f"Line up {SiH4} and {H2S} on the plot: same x, different y. Ask what's different about the molecules.",
       "\"Inside the molecule: covalent bonds, which don't break on boiling. Between molecules: what holds them together in the liquid?\"",
       f"Hydrogen bonding claimed for {CH4} or {H2S}. Group 14 hydrides called polar because C–H is polar. \"Stronger bonds\" as the reason for higher boiling points. Kelvin and Celsius mixed on one axis.")}
"""))

# ---------------------------------------------------------------- 11 answer key
pages.append(page(11, "Answer key", f"""
<div class="eyebrow">For marking</div>
<h1>Answer key</h1>
{box("ans", "Part 1 · 26 marks", f'''<table class="tight k-table" style="margin:0">
<tr><td>Shape</td><td>Trigonal pyramid, {C3V}: E, 2{C3}, 3{SV} (six operations). Not marked separately.</td></tr>
<tr><td>1.1 (5)</td><td>{A1} = {PHI(1)} + {PHI(2)} + {PHI(3)}; e = 2{PHI(1)} − {PHI(2)} − {PHI(3)} and {PHI(2)} − {PHI(3)}. Triangle, phases, labels, node in each e.</td></tr>
<tr><td>1.2 (4)</td><td>Three H 1s at −13.6 eV; {A1} below, e pair (two lines) above; energy axis.</td></tr>
<tr><td>1.3 (6)</td><td>2s with {A1}; {PZ} with {A1}; {PX} with e(x), {PY} with e(y). Phases matched where lobes meet.</td></tr>
<tr><td>1.4 (8)</td><td>From the bottom: 1{A1} (N 1s core), 2{A1}, 1e, 3{A1} (HOMO, lone pair), then 2e* and 4{A1}* (empty). N 2s below N 2p; {H3} {A1} and e on the right.</td></tr>
<tr><td>1.5 (3)</td><td>(1{A1})<sup>2</sup> (2{A1})<sup>2</sup> (1e)<sup>4</sup> (3{A1})<sup>2</sup>; valence-only (1{A1})<sup>2</sup> (1e)<sup>4</sup> (2{A1})<sup>2</sup> also right.</td></tr></table>''')}
{box("ans", "Part 2 · 31 marks", f'''<table class="tight k-table" style="margin:0">
<tr><td>2.1 (4)</td><td>BCC: body diagonal √3<i>a</i> = 4<i>r</i>. FCC: face diagonal √2<i>a</i> = 4<i>r</i>. <i>a</i> and <i>r</i> labelled.</td></tr>
<tr><td>2.2 (6)</td><td>BCC <i>V</i> = (4<i>r</i>/√3)<sup>3</sup> ≈ 12.32<i>r</i><sup>3</sup>. FCC <i>V</i> = 16√2<i>r</i><sup>3</sup> ≈ 22.63<i>r</i><sup>3</sup>.</td></tr>
<tr><td>2.3 (16)</td><td>Cu: BCC 2.583 × {E("−23")} {cm3}, 8.17 {gcm3}; <b>FCC 4.745 × {E("−23")} {cm3}, 8.90 {gcm3}</b>.<br>W: <b>BCC 3.174 × {E("−23")} {cm3}, 19.24 {gcm3}</b>; FCC 5.831 × {E("−23")} {cm3}, 20.94 {gcm3}. Accept ±0.05 {gcm3}.</td></tr>
<tr><td>2.4 (5)</td><td><b>Cu FCC</b> (8.90 vs 8.93). <b>W BCC</b> (19.24 vs 19.25). The other lattice is about 9 % off in each case.</td></tr></table>''')}
{box("ans", "Part 3 · 24 marks", f'''<table class="tight k-table" style="margin:0">
<tr><td>3.1 (16)</td><td>K: {CH4} 109, {SiH4} 161, {GeH4} 264, {SnH4} 221; {H2O} 373, {H2S} 213, {H2Se} 232, {H2Te} 271.<br>RMM: 16.04, 32.12, 76.66, 122.74; 18.02, 34.08, 80.99, 129.62. Two plots (or series): axes, labels, points, trendline.</td></tr>
<tr><td>3.2 (8)</td><td>Covalent E–H bonds; Group 14 tetrahedral and nonpolar, Group 16 bent and polar (2). Dispersion only vs dispersion + dipole–dipole (+ H-bonding for water) (2). {H2O} high from hydrogen bonding: small, electronegative O, polarised O–H (2). B.p. rises with size and polarisability down each group (2).</td></tr></table>''')}
{box("note", "Before the first script", f"<ul><li><b>Denominator:</b> the summary says 60; the parts add to 81.</li><li><b>2.3:</b> \"each\" read as each metal gives 16; the fifth density mark is unnamed.</li><li><b>N 2s = 2p on the sheet:</b> decide whether level 2s and 2p cost the \"AOs correct\" mark in 1.4.</li><li><b>{GeH4}:</b> plotted at the sheet's 264 K, the Group 14 line won't be smooth; credit students who say so.</li></ul>")}
"""))

assert len(pages) == TOTAL, len(pages)
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Lab 4 Companion</title><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"
with open(os.path.join(HERE, "lab4.html"), "w") as fh:
    fh.write(html)
print("built", len(html))
