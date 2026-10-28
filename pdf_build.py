"""Lab 3 Companion PDF (iPad portrait). HTML pages → Chromium PDF."""
import json, math, pathlib, re
B = pathlib.Path(__file__).parent
F = json.load(open(B / 'figs.json'))
FONT = B / 'npmtmp/node_modules/@fontsource'

def fontfaces():
    css = ''
    for fam, d, files in (('IBM Plex Sans', 'ibm-plex-sans', ['400', '500', '600', '700', '400-italic', '600-italic']), ('IBM Plex Mono', 'ibm-plex-mono', ['400', '600'])):
        for f in files:
            t = (FONT / d / f'{f}.css').read_text()
            css += t.replace('url(./files/', f'url(file://{FONT / d}/files/')
    return css

# ---------------------------------------------------------------- Part 2 pattern figures (same patterns as the app)
S3 = math.sqrt(3); INK = '#1f2937'
PAT = {
  'checker': dict(name='Checkerboard', type='Square (turned 45°)', a=(1, 1), b=(1, -1), motif=f'<rect x="0" y="0" width="1" height="1" fill="{INK}"/>',
     prim=((1, 1), (1, -1)), conv=((2, 0), (0, 2)), wrong=((1, 0), (0, 1)), per='1 dark + 1 light square',
     note='Primitive: the square turned 45°. The 2 × 2 square works but holds 2 lattice points. One square fails: its neighbour is the other colour.'),
  'brick': dict(name='Brick wall', type='Centred rectangular', a=(2, 0), b=(1, .7), motif='<rect x="0" y="0" width="2" height="0.7" fill="#b85c38" stroke="#e9e4da" stroke-width="0.08"/>',
     prim=((2, 0), (1, .7)), conv=((2, 0), (0, 1.4)), wrong=((2, 0), (0, .7)), per='1 brick',
     note='Primitive: a leaning parallelogram holding 1 brick. Conventional: 1 brick × 2 courses, holding 2 bricks. One brick alone fails because the rows are offset.'),
  'hex': dict(name='Chicken wire', type='Hexagonal', a=(S3, 0), b=(S3/2, 1.5),
     motif=''.join(f'<line x1="0" y1="0" x2="{x}" y2="{y}" stroke="{INK}" stroke-width="0.09" stroke-linecap="round"/>' for x, y in ((0, 1), (S3/2, -.5), (-S3/2, -.5))) + f'<circle cx="0" cy="0" r="0.1" fill="{INK}"/><circle cx="0" cy="1" r="0.1" fill="{INK}"/>',
     prim=((S3, 0), (S3/2, 1.5)), conv=None, wrong=((0, 1), (S3, 0)), per='2 corners',
     note='Primitive: a 60°/120° rhombus holding 2 corners (a Y and an upside-down Y). Corner to next corner along an edge is not a repeat.'),
  'leaf': dict(name='Leaf grid', type='Rectangular', a=(1.6, 0), b=(0, 1.15),
     motif='<g transform="translate(0.8,0.6)"><path d="M0,-0.42 Q0.34,-0.05 0,0.38 Q-0.34,-0.05 0,-0.42Z" fill="#2f7d4f"/><line x1="0" y1="-0.34" x2="0" y2="0.5" stroke="#d9f2e2" stroke-width="0.035"/></g>',
     prim=((1.6, 0), (0, 1.15)), conv=None, wrong=None, per='1 leaf', note='Primitive and rectangular: 1 leaf per cell. The corners can sit on the leaves or between them.'),
  'flag': dict(name='Flags', type='Oblique', a=(1.5, 0), b=(0.4, 1.2),
     motif=f'<g transform="translate(0.35,0.85)"><line x1="0" y1="0" x2="0" y2="-0.62" stroke="{INK}" stroke-width="0.05"/><polygon points="0,-0.62 0.46,-0.48 0,-0.32" fill="#c2410c"/></g>',
     prim=((1.5, 0), (0.4, 1.2)), conv=((1.5, 0), (-1.1, 1.2)), wrong=((1.5, 0), (0, 1.2)), per='1 flag',
     note='Two different parallelograms, same area, both primitive and both right. Forcing a rectangle fails because each row is shifted along.'),
  'arrows': dict(name='Arrows', type='Rectangular, 2 motifs', a=(2, 0), b=(0, 1),
     motif=''.join(f'<g transform="translate({x},0.5) scale({d},1)"><polygon points="-0.32,-0.08 0.08,-0.08 0.08,-0.2 0.34,0 0.08,0.2 0.08,0.08 -0.32,0.08" fill="#1e3a8a"/></g>' for x, d in ((0.5, 1), (1.5, -1))),
     prim=((2, 0), (0, 1)), conv=None, wrong=((1, 0), (0, 1)), per='2 arrows',
     note='The cell must hold one → and one ←. Boxing a single arrow fails: sliding by one arrow turns → into ←.'),
}
def pattern_svg(k, w=300, h=164, sc=33):
    p = PAT[k]; a, b = p['a'], p['b']; cx, cy = w/2, h/2
    D = a[0]*b[1] - a[1]*b[0]; out = []
    X0, X1, Y0, Y1 = -cx/sc - 2, cx/sc + 2, -cy/sc - 2, cy/sc + 2
    corners = [(X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)]
    cf = [((x*b[1] - y*b[0])/D, (a[0]*y - a[1]*x)/D) for x, y in corners]
    i0, i1 = math.floor(min(c[0] for c in cf)) - 1, math.ceil(max(c[0] for c in cf)) + 1
    j0, j1 = math.floor(min(c[1] for c in cf)) - 1, math.ceil(max(c[1] for c in cf)) + 1
    g = ''.join(f'<g transform="translate({i*a[0]+j*b[0]:.4f},{i*a[1]+j*b[1]:.4f})">{p["motif"]}</g>' for i in range(i0, i1+1) for j in range(j0, j1+1))
    def cell(v, colr, dash, sw, fill='none'):
        u, w2 = v; O = (0, 0)
        if k in ('leaf', 'flag'): O = (0, 0)
        pts = [O, (O[0]+u[0], O[1]+u[1]), (O[0]+u[0]+w2[0], O[1]+u[1]+w2[1]), (O[0]+w2[0], O[1]+w2[1])]
        d = ' '.join(f'{cx + x*sc:.1f},{cy + y*sc:.1f}' for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<polygon points="{d}" fill="{fill}" stroke="{colr}" stroke-width="{sw}"{da} stroke-linejoin="round"/>'
    cells = ''
    if p['wrong']: cells += cell(p['wrong'], '#b42318', '5 4', 2.2)
    if p['conv']: cells += cell(p['conv'], '#b45309', '7 5', 2.4)
    cells += cell(p['prim'], '#15803d', None, 3, 'rgba(21,128,61,.14)')
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="cp{k}"><rect width="{w}" height="{h}" rx="8"/></clipPath></defs>'
            f'<g clip-path="url(#cp{k})"><rect width="{w}" height="{h}" fill="#fbfaf6"/><g transform="translate({cx},{cy}) scale({sc})">{g}</g>{cells}</g>'
            f'<rect width="{w}" height="{h}" rx="8" fill="none" stroke="#d9dfe8"/></svg>')

# ---------------------------------------------------------------- helpers
def box(kind, body, label=None):
    L = {'q': 'Question', 't': 'Thinking', 'w': 'Working', 'a': 'Answer', 'trap': 'Trap', 'c': 'Coaching', 'n': 'Note', 'k': 'Key idea'}[kind]
    return f'<div class="box {kind}"><div class="bl">{label or L}</div>{body}</div>'
def coach(show, say, watch):
    return box('c', f'<div class="ssw"><b>Show it with the model</b><p>{show}</p><b>Say</b><p>{say}</p><b>Watch for</b><p>{watch}</p></div>')
def sub(s): return re.sub(r'([A-Za-zσ])(\d+)', r'\1<sub>\2</sub>', s)
pages = []
NAV = [('glance', 'At a glance'), ('p1', 'Part 1'), ('p2', 'Part 2'), ('p3', 'Part 3'), ('key', 'Answer key'), ('app', 'App')]
def page(pid, sec, title, body, kicker=''):
    nav = ''.join(f'<a href="#{k}" class="{"on" if k == sec else ""}">{t}</a>' for k, t in NAV)
    pages.append(f'<section class="page" id="{pid}"><nav>{nav}</nav><div class="head"><div class="kick">{kicker}</div><h1>{title}</h1></div><div class="body">{body}</div><footer><span>Lab 3 Companion · CHEM 1170 Week 9 · Wednesday</span><span class="pn"></span></footer></section>')
def fig(k, cap=None, cls=''):
    return f'<figure class="{cls}">{F[k] if k in F else k}{f"<figcaption>{cap}</figcaption>" if cap else ""}</figure>'

# ================================================================ COVER
cover = f'''<section class="page cover" id="cover">
<div class="cv">
 <div class="kick">CHEM 1170 · Laboratory 3 · Week 9 · Wednesday stream</div>
 <h1 class="big">Lab 3 Companion</h1>
 <p class="lede">Molecular geometry and symmetry, and crystals. Your understanding and your bench coaching on the same page, with worked answers for Parts 1 and 3 and the method for Part 2.</p>
 <div class="toc">
  <a href="#glance"><b>At a glance</b><span>Running order, marks, kit, and what is not on the sheet</span></a>
  <a href="#p1"><b>Part 1 · Symmetry</b><span>[Cr(CO)<sub>6</sub>] and naphthalene: every element, every operation, before and after</span></a>
  <a href="#p2"><b>Part 2 · Unit cells from tiles</b><span>The rules, the five 2D lattices, six worked patterns</span></a>
  <a href="#p3"><b>Part 3 · NaCl and CsCl</b><span>Counting, holes, and why Na<sup>+</sup> and Cs<sup>+</sup> pack differently</span></a>
  <a href="#key"><b>Answer key</b><span>One page for marking</span></a>
  <a href="#app"><b>Lab 3 Bench app</b><span>What each tab does at the bench</span></a>
 </div>
 <div class="legend">
  {''.join(f'<span class="lg {k}">{t}</span>' for k, t in (('q', 'Question'), ('t', 'Thinking'), ('w', 'Working'), ('a', 'Answer'), ('trap', 'Trap'), ('c', 'Coaching'), ('n', 'Note')))}
 </div>
 <p class="small">Part 2's tile sheets are handed out in the lab and are not in the manual. Send photos of them and an add-on with the cells drawn on the real sheets follows. Every symmetry count here was checked by computer (all 48 and 8 operations generated and tested), and the chemistry was checked a second time independently.</p>
</div></section>'''
pages.append(cover)

# ================================================================ AT A GLANCE
body = f'''
<table class="t">
<thead><tr><th>Part</th><th>Time</th><th>Marks</th><th>Students do</th><th>You look for</th></tr></thead><tbody>
<tr><td><b>1</b> Symmetry</td><td>45 min</td><td>20</td><td>In groups, find the symmetry elements and operations of [Cr(CO)<sub>6</sub>] and naphthalene. Before-and-after drawings with labelled atoms. No point group needed.</td><td>Atoms numbered so moves can be seen. Each element drawn and named. A count of operations, not just elements.</td></tr>
<tr><td><b>2</b> Unit cells</td><td>70 min</td><td>10</td><td>Find possible unit cells on the tile sheets handed out.</td><td>Parallelograms only. Corners on identical points. Copies slide, never turn.</td></tr>
<tr><td><b>3</b> NaCl, CsCl</td><td>60 min</td><td>20</td><td>Build both cells, count ions per cell, name the holes, explain fcc vs "bcc".</td><td>Share fractions used. Hole geometry argued from the model. Radius ratio in the explanation.</td></tr>
</tbody></table>
<div class="cols2">
{box('n', '<p><b>Hand-in:</b> Parts 1 to 3 by <b>5 pm the same day</b>, drop box for Chemistry Laboratory A. Diagrams <b>in ink</b>. ID number, name and lab day on every sheet; <b>demonstrator\'s name</b> on the front page. Total 50 marks.</p>', 'Hand-in rules')}
{box('n', '<p><b>Per student:</b> 24 foam balls in 4 colours, 12 toothpicks of each of 2 sizes. That kit fits Part 1: 4 colours for Cr, C, O and H, and [Cr(CO)<sub>6</sub>] uses exactly 6 long Cr–C plus 6 short C–O sticks. Naphthalene needs 18 balls and 19 sticks. <b>NaCl needs 27 balls and 54 sticks</b>, so a bench pools about three kits; CsCl needs 9 balls.</p>', 'The kit')}
</div>
<h2>What is not on the sheet</h2>
<p class="intro">Like the A to D unknowns in Lab 1, some of what students work with arrives at the bench. Parts 1 and 3 are fixed: there is no day-by-day split, so every stream does the same molecules and lattices.</p>
<table class="t">
<thead><tr><th>Item</th><th>Status</th><th>What it means for you</th></tr></thead><tbody>
<tr><td>Part 2 tile/wallpaper sheets</td><td><span class="pill amber">Handed out in lab</span></td><td>The only part without a worked answer here. Pages 8 and 9 give the method; photos of the sheets give an add-on with every cell drawn. The app can also check cells on a photo you take at the bench.</td></tr>
<tr><td>Required reading and 3 videos</td><td><span class="pill amber">On the course page</span></td><td>Sets how deep students are expected to go (for example, whether S<sub>4</sub> and S<sub>6</sub> are expected). This guide covers the full answer.</td></tr>
<tr><td>Response sheet</td><td><span class="pill gray">None this lab</span></td><td>Students hand in their own drawings and lists. Layout will vary.</td></tr>
<tr><td>Mark scheme</td><td><span class="pill gray">Not yet</span></td><td>Page 13 gives a complete key. Mark to the scheme when it arrives.</td></tr>
<tr><td>Atom labels and axes</td><td><span class="pill blue">Students choose</span></td><td>Every student may number differently. Follow each student's own labels when marking.</td></tr>
<tr><td>"Number of operations"</td><td><span class="pill blue">Ambiguous wording</span></td><td>Could mean per element or in total. Totals: <b>48</b> for [Cr(CO)<sub>6</sub>], <b>8</b> for naphthalene. Page 4 has both.</td></tr>
</tbody></table>
{box('trap', '<p>Three places where the sheet\'s wording and the full answer differ. In each, a careful student who argues the full answer is right:</p><ul><li><b>Part 3, holes:</b> the sheet offers octahedral or tetrahedral. In CsCl both ions sit in <b>cubic</b> (8-coordinate) holes: neither.</li><li><b>Part 3, "body centred cubic":</b> the CsCl <i>arrangement</i> is body-centred, but the corner (Cl<sup>−</sup>) and centre (Cs<sup>+</sup>) differ, so the <i>lattice</i> is simple cubic with two ions per point.</li><li><b>Part 1, counting:</b> the sheet asks for elements and operations; S<sub>4</sub> and S<sub>6</sub> are easy to miss but are real elements of [Cr(CO)<sub>6</sub>].</li></ul>', 'Three traps')}
'''
page('glance', 'glance', 'At a glance', body, 'Before the session')

# ================================================================ PART 1 · concept kit
body = f'''
<div class="cols2">
{box('k', '<p>An <b>element</b> is the thing: a line, a plane, a point. An <b>operation</b> is the move you do with it. One element can give several operations: a C<sub>4</sub> axis gives turns of 90°, 180° and 270°.</p><p>A move is a symmetry operation when every atom lands on an identical atom. Before and after look the same; only the labels show that anything moved.</p>')}
{box('k', '<p><b>Before and after.</b> Number every atom (or ligand) first. Draw the element on the molecule. Draw it again after the move with the numbers in their new places. An atom that stays put sits <i>on</i> the element.</p><p>Labels travel with the atoms. That is the whole point of the drawing.</p>', 'Key idea')}
</div>
<table class="t">
<thead><tr><th>Element</th><th>Symbol</th><th>The move</th><th>New operations it adds</th></tr></thead><tbody>
<tr><td>Identity</td><td>E</td><td>Do nothing</td><td>1 (every molecule has it)</td></tr>
<tr><td>Proper axis</td><td>C<sub>n</sub></td><td>Turn by 360°/n</td><td>n − 1 (C<sub>n</sub>, C<sub>n</sub><sup>2</sup> … C<sub>n</sub><sup>n−1</sup>); C<sub>n</sub><sup>n</sup> = E</td></tr>
<tr><td>Mirror plane</td><td>σ</td><td>Reflect through the plane</td><td>1 (σ<sup>2</sup> = E). σ<sub>h</sub> ⟂ main axis; σ<sub>v</sub>, σ<sub>d</sub> contain it</td></tr>
<tr><td>Inversion centre</td><td><i>i</i></td><td>Each atom through the centre to the opposite side</td><td>1 (<i>i</i><sup>2</sup> = E)</td></tr>
<tr><td>Improper axis</td><td>S<sub>n</sub></td><td>Turn 360°/n, then reflect in the plane ⟂ to the axis</td><td>Only the powers not already counted (see below)</td></tr>
</tbody></table>
{box('t', '<p><b>Counting without double counting.</b> Take each axis and list its powers, then cross out any power that is a different operation you already have:</p><ul><li>C<sub>4</sub>: C<sub>4</sub>, C<sub>4</sub><sup>2</sup>, C<sub>4</sub><sup>3</sup>. But C<sub>4</sub><sup>2</sup> <b>is</b> the C<sub>2</sub> on that line, so it is usually listed as C<sub>2</sub>.</li><li>S<sub>4</sub>: S<sub>4</sub>, S<sub>4</sub><sup>2</sup> = C<sub>2</sub> (already counted), S<sub>4</sub><sup>3</sup>, S<sub>4</sub><sup>4</sup> = E. So each S<sub>4</sub> axis adds <b>2</b>.</li><li>S<sub>6</sub>: S<sub>6</sub>, S<sub>6</sub><sup>2</sup> = C<sub>3</sub>, S<sub>6</sub><sup>3</sup> = <i>i</i>, S<sub>6</sub><sup>4</sup> = C<sub>3</sub><sup>2</sup>, S<sub>6</sub><sup>5</sup>, S<sub>6</sub><sup>6</sup> = E. So each S<sub>6</sub> axis adds <b>2</b>.</li></ul><p>The total number of operations is the <b>order</b> of the point group. Students do not need the point group, but the total is a good check: 48 and 8.</p>', 'How to count operations')}
{coach('Hold a model with one bond pointing at the student. Turn it a quarter turn. Ask: does it look the same? Now ask which ball is which. That is the difference between "looks the same" and "a move happened".',
       '"The element is the line. The operation is the turn. Number the balls so you can prove the turn happened."',
       'Lists of elements with no count of operations. Unlabelled drawings: without numbers a before/after pair shows nothing. Students who count C<sub>2</sub> twice: once as its own axis and once as C<sub>4</sub><sup>2</sup>.')}
'''
page('p1', 'p1', 'Elements, operations and how to count them', body, 'Part 1 · Symmetry · 45 min · 20 marks')

# ================================================================ Cr(CO)6 page 1
el_rows = [
 ('E', '1', '–', '1'),
 ('C<sub>4</sub>', '3', 'Along each OC–Cr–CO line (through 2 trans ligands)', '6 (C<sub>4</sub>, C<sub>4</sub><sup>3</sup> on each)'),
 ('C<sub>2</sub> = C<sub>4</sub><sup>2</sup>', 'same 3', 'Same lines as the C<sub>4</sub>', '3'),
 ('C<sub>3</sub>', '4', 'Through the centres of opposite triangular faces of the ligand octahedron', '8 (C<sub>3</sub>, C<sub>3</sub><sup>2</sup> on each)'),
 ('C<sub>2</sub>′', '6', 'Bisecting two neighbouring ligands, and the opposite pair', '6'),
 ('<i>i</i>', '1', 'At Cr', '1'),
 ('S<sub>4</sub>', '3', 'On the C<sub>4</sub> lines', '6 (S<sub>4</sub>, S<sub>4</sub><sup>3</sup> on each)'),
 ('S<sub>6</sub>', '4', 'On the C<sub>3</sub> lines', '8 (S<sub>6</sub>, S<sub>6</sub><sup>5</sup> on each)'),
 ('σ<sub>h</sub>', '3', 'Each contains 4 ligands and Cr (⟂ to a C<sub>4</sub>)', '3'),
 ('σ<sub>d</sub>', '6', 'Each contains 1 trans pair and bisects the other four', '6'),
]
body = f'''
{box('q', '<p><b>From the manual:</b> explore the symmetry elements and operations of [Cr(CO)<sub>6</sub>]. Practise illustrating the elements and operations (the before and after snapshot, labelling the atoms properly). Submit labelled illustrations and the list of elements and number of operations you deduced. You do not need to assign the point group.</p>')}
<div class="cols2">
{box('t', '<p><b>Shape first.</b> Six CO ligands around Cr, nothing else: six electron domains, octahedral. Each Cr–C≡O unit is straight (180°), so every ligand lies on a line through Cr.</p><p><b>So</b> the molecule has exactly the symmetry of the paper octahedron from Lab 2. The O atoms behave like its six vertices. Number the ligands 1 to 6: 1 up, 6 down, and 2, 3, 4, 5 around the middle.</p>')}
{box('t', '<p><b>Find the high axes.</b> Each of the 3 ligand-to-ligand lines is a C<sub>4</sub>. Look at one face of three ligands (1, 2, 3): a C<sub>3</sub> runs through it and out through the opposite face (4, 5, 6). 8 faces give 4 such lines.</p><p><b>Then the rest:</b> C<sub>2</sub>′ lines between neighbouring ligands, the centre at Cr, the planes, and the S axes riding on the C<sub>4</sub> and C<sub>3</sub> lines.</p>')}
</div>
{box('a', '<table class="t"><thead><tr><th>Element</th><th>How many</th><th>Where</th><th class="n">Operations</th></tr></thead><tbody>' +
     ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td class="n">{d}</td></tr>' for a, b, c, d in el_rows) +
     '<tr class="tot"><td colspan="3">Total operations (the order)</td><td class="n">48</td></tr></tbody></table>'
     '<p class="small">Compact list for a student\'s answer: <b>E, 3C<sub>4</sub>, 3C<sub>2</sub> (= C<sub>4</sub><sup>2</sup>), 4C<sub>3</sub>, 6C<sub>2</sub>′, <i>i</i>, 3S<sub>4</sub>, 4S<sub>6</sub>, 3σ<sub>h</sub>, 6σ<sub>d</sub>: 48 operations.</b></p>', 'Answer · [Cr(CO)₆]')}
{box('trap', '<ul><li><b>24 instead of 48:</b> students who find only the turns (rotations) get 24. The other 24 come from <i>i</i>, S<sub>4</sub>, S<sub>6</sub> and the 9 mirror planes.</li><li><b>A C<sub>6</sub> on the C<sub>3</sub> line:</b> looking down a C<sub>3</sub> you see six ligands in a zig-zag. A plain 60° turn fails; 60° then a reflection works. That is the S<sub>6</sub>.</li><li><b>Counting 9 C<sub>2</sub> axes as 9 elements</b> is fine if they say 3 lie on the C<sub>4</sub> lines; listing 3C<sub>4</sub> and 9C<sub>2</sub> and counting C<sub>4</sub><sup>2</sup> again double counts.</li></ul>', 'Traps')}
'''
page('p1-cr', 'p1', '[Cr(CO)<sub>6</sub>]: the full answer', body, 'Part 1 · Molecule 1 of 2')

# ================================================================ Cr(CO)6 figures
caps = {'C4': 'C<sub>4</sub> · 90°', 'C2': 'C<sub>2</sub> = C<sub>4</sub><sup>2</sup> · 180°', 'C3': 'C<sub>3</sub> · 120°', 'C2p': 'C<sub>2</sub>′ · 180°', 'i': '<i>i</i> · through Cr',
        'S4': 'S<sub>4</sub> · 90° + reflect', 'S6': 'S<sub>6</sub> · 60° + reflect', 'sh': 'σ<sub>h</sub> · contains 2, 3, 4, 5', 'sd': 'σ<sub>d</sub> · contains 1, 6'}
cells = fig('cr_C4_b', '<b>Before</b> (every panel starts here). Ligand numbers sit on the O atoms.')
for k in ('C4', 'C2', 'C3', 'C2p', 'i', 'S4', 'S6', 'sh', 'sd'):
    cells += fig(f'cr_{k}_a', f'<b>{caps[k]}</b><br>{F["cr_" + k + "_t"]}')
cells += fig('cr_C6fake', '<b>Not an element:</b> 60° alone about a C<sub>3</sub> line. Ligands land between old places.', 'bad')
body = f'''
<p class="intro">One element of each kind, shown <b>after</b> its move, from the same starting view. The element is drawn on each panel; numbers moved with their ligands. A student's drawing needs a before and after for each element, like this pair.</p>
<div class="grid4">{cells}</div>
{coach('Turn the model by hand about the vertical line, one quarter turn, then press ▶ C<sub>4</sub> in the app to show the same move with the numbers travelling.',
       '"Ligand 2 went to where 3 was, 3 to 4, 4 to 5, 5 to 2. Ligands 1 and 6 are on the axis, so they stay."',
       'S<sub>4</sub> drawings that show only the turn. The reflection step must appear: 1 and 6 swap.')}
'''
page('p1-cr-figs', 'p1', '[Cr(CO)<sub>6</sub>]: before and after', body, 'Part 1 · Molecule 1 of 2 · drawings')

# ================================================================ Naphthalene
na_rows = [
 ('E', '–', '–'),
 ('C<sub>2</sub>(z)', '⟂ to the ring plane, through the centre', 'none'),
 ('C<sub>2</sub>(y)', 'In the plane, the short axis, along the C4a–C8a bond', 'C4a, C8a'),
 ('C<sub>2</sub>(x)', 'In the plane, the long axis', 'none (it cuts the 2–3, 4a–8a, 6–7 bonds)'),
 ('<i>i</i>', 'Midpoint of the C4a–C8a bond', 'none'),
 ('σ(xy)', 'The ring plane itself', 'all 18 atoms'),
 ('σ(xz)', '⟂ to the ring, containing the long axis', 'none'),
 ('σ(yz)', '⟂ to the ring, containing the short axis', 'C4a, C8a'),
]
body = f'''
{box('q', '<p><b>From the manual:</b> the same task for naphthalene, C<sub>10</sub>H<sub>8</sub>: labelled before and after illustrations, the elements, and the number of operations.</p>')}
<div class="cols2a">
{fig('na_ref', 'Standard numbering (IUPAC): C1 to C8 around the outside, C4a and C8a at the ring fusion. Some texts call these C9 and C10.')}
{box('t', '<p><b>Flat and rectangular.</b> All 18 atoms lie in one plane, and the molecule is symmetric end to end and side to side. Three lines at right angles: the long axis (x), the short axis (y) and the line ⟂ to the plane (z). Each is a C<sub>2</sub>.</p><p><b>Three mirror planes</b> each contain two of those lines. Where all three meet is <i>i</i>.</p>')}
</div>
{box('a', '<table class="t"><thead><tr><th>Element</th><th>Where</th><th>Atoms on it</th></tr></thead><tbody>' +
     ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in na_rows) +
     '<tr class="tot"><td colspan="2">Total operations (the order); each element gives one</td><td class="n">8</td></tr></tbody></table>', 'Answer · naphthalene')}
<div class="cols2">
{box('trap', '<p><b>Look-alike pairs.</b> On a flat molecule some moves send every atom to the same place:</p><ul><li>C<sub>2</sub>(z) and <i>i</i></li><li>C<sub>2</sub>(x) and σ(xz)</li><li>C<sub>2</sub>(y) and σ(yz)</li><li>E and σ(xy)</li></ul><p>They are still different operations: they differ above and below the plane. Put a mark on the top face (a red dot above C1 in these drawings) to tell them apart.</p>', 'Trap · same numbers, different moves')}
{box('trap', '<ul><li><b>Benzene thinking:</b> each ring looks hexagonal, but there is no C<sub>6</sub> or C<sub>3</sub>. The second ring breaks it.</li><li><b>"σ(xy) does nothing":</b> every atom stays, but it is still an operation and counts.</li><li><b>Double bonds:</b> the manual\'s picture is the Kekulé form that keeps full symmetry, so it gives the same answer.</li></ul>' +
     '<div class="kek">' + F['kek_d2h'] + F['kek_c2v'] + '</div>', 'Traps')}
</div>
'''
page('p1-na', 'p1', 'Naphthalene: the full answer', body, 'Part 1 · Molecule 2 of 2')

capn = {'C2z': 'C<sub>2</sub>(z)', 'C2y': 'C<sub>2</sub>(y)', 'C2x': 'C<sub>2</sub>(x)', 'i': '<i>i</i>', 'sxy': 'σ(xy)', 'sxz': 'σ(xz)', 'syz': 'σ(yz)'}
def pair(k1, k2, head):
    def one(k):
        if k == 'E': return fig('na_C2z_b', '<b>Before / E</b>: nothing moves. Red dot = top face, above C1.')
        return fig(f'na_{k}_a', f'<b>{capn[k]}</b> · {F["na_" + k + "_t"]}')
    return f'<div class="pair"><div class="ph">{head}</div><div class="pp">{one(k1)}{one(k2)}</div></div>'
cells = (pair('E', 'sxy', 'E and σ(xy): no atom moves') + pair('C2z', 'i', 'C<sub>2</sub>(z) and <i>i</i>: same swaps') +
         pair('C2y', 'syz', 'C<sub>2</sub>(y) and σ(yz): same swaps') + pair('C2x', 'sxz', 'C<sub>2</sub>(x) and σ(xz): same swaps'))
body = f'''
<p class="intro">Each pair moves the atoms to exactly the same places. Only the red dot tells them apart: solid = above the plane, dashed = below. Students drawing before/after need a marker like this, or the pairs look identical.</p>
<div class="pairs">{cells}</div>
{coach('Lay the model flat. Stick a small paper flag on C1 pointing up. Turn it 180° about the vertical axis: flag still up. Now invert through the centre: flag points down. Same numbers, different moves.',
       '"Both moves swap 1 with 5, 2 with 6 and so on. Only the flag tells you which one you did."',
       'Students listing 4 elements (just the obvious ones). The two in-plane C<sub>2</sub> axes and <i>i</i> are the usual misses.')}
'''
page('p1-na-figs', 'p1', 'Naphthalene: after each move', body, 'Part 1 · Molecule 2 of 2 · drawings')

# ================================================================ PART 2
body = f'''
{box('q', '<p><b>From the manual:</b> in groups, using the tile/wallpaper patterns provided, deduce possible unit cells. You are looking for the simplest repeating unit that builds the whole pattern by <b>translation only</b>. Submit the pattern sheets with possible unit cells marked. (10 marks)</p>')}
<div class="cols2">
{box('k', '<ul class="tight"><li>A 2D unit cell is a <b>parallelogram</b> set by two edges, <b>a</b> and <b>b</b>.</li><li>Copies of it, <b>slid only</b> (never turned or flipped), rebuild the whole pattern with no gaps or overlaps.</li><li>All four corners sit on <b>identical points</b>: same motif, same orientation.</li><li>The origin can go anywhere. Moving the whole cell does not change it.</li><li>Many cells work. The <b>primitive</b> cell holds 1 lattice point (4 corners × ¼). A bigger cell is still valid.</li></ul>', 'The rules')}
{box('t', '<p><b>A test that always works.</b> Trace the pattern, or imagine a transparent copy. Slide it along your proposed edge <b>a</b>. If the copy lands exactly on the pattern everywhere, a is a true repeat. Do the same for b. If both pass and the cell is a parallelogram, it is a unit cell.</p><p>The app\'s <b>shift test</b> does exactly this on a photo of the real sheet.</p>', 'The slide test')}
</div>
<h2>The five 2D lattices</h2>
<table class="t">
<thead><tr><th>Lattice</th><th>Cell edges</th><th>Angle</th><th>Example on page 10</th></tr></thead><tbody>
<tr><td><b>Oblique</b></td><td>a ≠ b</td><td>any (not 90°)</td><td>Flags</td></tr>
<tr><td><b>Rectangular</b></td><td>a ≠ b</td><td>90°</td><td>Leaf grid; Arrows (2 motifs per cell)</td></tr>
<tr><td><b>Centred rectangular</b></td><td>rectangle with an extra point in the middle; primitive cell is a rhombus</td><td>90° (conventional)</td><td>Brick wall</td></tr>
<tr><td><b>Square</b></td><td>a = b</td><td>90°</td><td>Checkerboard (square turned 45°)</td></tr>
<tr><td><b>Hexagonal</b></td><td>a = b</td><td>120° (or 60°)</td><td>Chicken wire</td></tr>
</tbody></table>
<div class="cols2">
{box('trap', '<ul><li><b>Boxing one motif</b> when its neighbours are turned or mirrored copies. The true cell holds both.</li><li><b>A hexagon or triangle</b> as the cell. Cells are parallelograms.</li><li><b>Corners on look-alike points</b> that differ in orientation.</li><li><b>Naming the lattice from the cell shape.</b> A brick wall\'s primitive cell is a leaning parallelogram, but the pattern is centred rectangular, not oblique. The type comes from the pattern\'s symmetry.</li></ul>', 'Typical errors')}
{box('n', '<p><b>Counting what is inside.</b> A primitive cell holds exactly one repeat of the pattern: one motif, or one set of motifs (two arrows, two corners). Students can check a cell by counting pieces of motif inside it.</p><p><b>For marking:</b> "possible unit cells" means more than one answer can score. Any parallelogram whose edges pass the slide test is valid; the primitive one is the simplest.</p>')}
</div>
'''
page('p2', 'p2', 'Finding a unit cell in a pattern', body, 'Part 2 · Unit cells · 70 min · 10 marks')

cells = ''.join(f'<figure class="pat">{pattern_svg(k)}<figcaption><b>{PAT[k]["name"]}</b> · {PAT[k]["type"]}<br>{PAT[k]["note"]}</figcaption></figure>' for k in PAT)
body = f'''
<p class="intro"><span class="sw g"></span> primitive cell · <span class="sw o"></span> another valid cell · <span class="sw r"></span> the common mistake. Practice patterns made for this guide; the lab's own sheets go in the add-on.</p>
<div class="grid2">{cells}</div>
{coach('Put a sheet of tracing paper over the pattern (or use the app\'s shift test on a photo). Mark one motif and slide the tracing along the student\'s edge.',
       '"If the traced copy sits on the pattern everywhere, your edge is a real repeat. If anything is out of place, it is not."',
       'Cells drawn around a single motif in patterns where motifs alternate. Cells with curved or hexagonal outlines.')}
'''
page('p2-ex', 'p2', 'Six worked patterns', body, 'Part 2 · worked examples')

# ================================================================ PART 3 · NaCl
body = f'''
{box('q', '<p><b>From the manual:</b> build NaCl and CsCl. Write the number of each type of atom in the unit cell (faces, edges, vertices, centre). Identify if the cation and anion sit in an octahedral or tetrahedral hole; you may need other groups\' models. Explain why Na<sup>+</sup> forms a face centred cubic structure but Cs<sup>+</sup> a body centred cubic structure with Cl<sup>−</sup>. (20 marks)</p>')}
<div class="cols2a">
{fig('nacl_full')}
<div>{box('w', '<p>Count each site, times its share of the cell:</p><table class="t"><tbody><tr><td>Corners, Cl<sup>−</sup></td><td class="n">8 × ⅛ = 1</td></tr><tr><td>Face centres, Cl<sup>−</sup></td><td class="n">6 × ½ = 3</td></tr><tr><td>Edge centres, Na<sup>+</sup></td><td class="n">12 × ¼ = 3</td></tr><tr><td>Body centre, Na<sup>+</sup></td><td class="n">1 × 1 = 1</td></tr><tr class="tot"><td>Cl<sup>−</sup> 4, Na<sup>+</sup> 4</td><td class="n">4 NaCl per cell</td></tr></tbody></table><p class="small">Shares: a corner is shared by 8 cells, an edge by 4, a face by 2. Na<sup>+</sup> on the corners gives the same 4 + 4.</p>')}</div>
</div>
<div class="grid4">{fig('nacl_corner')}{fig('nacl_face')}{fig('nacl_edge')}{fig('nacl_body')}</div>
<div class="grid3">{fig('nacl_oct_cat', 'Na<sup>+</sup> at the centre touches the 6 face-centre Cl<sup>−</sup>: <b>octahedral hole</b>.')}{fig('nacl_oct_an', 'Cl<sup>−</sup> where 8 cells meet touches 6 Na<sup>+</sup>: also <b>octahedral</b>.')}{fig('nacl_tet', 'The 8 <b>tetrahedral holes</b> (white) are all <b>empty</b>.')}</div>
{coach('For the Cl<sup>−</sup> octahedron without 8 models: hold another group\'s cell against one face. The face-centre Cl<sup>−</sup> touches 4 edge Na<sup>+</sup> in its face, the body-centre Na<sup>+</sup> on one side, and the next cell\'s body-centre Na<sup>+</sup> on the other.',
       '"Each ion sits in the middle of six of the other kind. 6 : 6, octahedral both ways."',
       'Counts of 14 Cl<sup>−</sup> and 13 Na<sup>+</sup> (balls, not shares). Totals that are not equal: NaCl must come out 1 : 1.')}
'''
page('p3', 'p3', 'Sodium chloride, NaCl', body, 'Part 3 · Build and describe · 60 min · 20 marks')

# ================================================================ PART 3 · CsCl
body = f'''
<div class="grid3">{fig('cscl_full', 'Dashed: the 8 Cs<sup>+</sup>–Cl<sup>−</sup> contacts.')}{fig('cscl_corner')}{fig('cscl_body')}</div>
{box('w', '<table class="t"><tbody><tr><td>Corners, Cl<sup>−</sup></td><td class="n">8 × ⅛ = 1</td></tr><tr><td>Body centre, Cs<sup>+</sup></td><td class="n">1 × 1 = 1</td></tr><tr class="tot"><td>Cl<sup>−</sup> 1, Cs<sup>+</sup> 1</td><td class="n">1 CsCl per cell</td></tr></tbody></table>')}
<div class="cols2">{fig('cscl_cube_cat', 'Cs<sup>+</sup> touches all 8 corner Cl<sup>−</sup>: a <b>cubic hole</b>, CN 8.')}{fig('cscl_cube_an', 'Cl<sup>−</sup> where 8 cells meet touches 8 Cs<sup>+</sup>: also cubic, CN 8.')}</div>
{box('trap', '<ul><li><b>Octahedral or tetrahedral?</b> Neither. Both ions are 8-coordinate, in <b>cubic</b> holes. Accept "cubic" or "8-coordinate"; a student who forces "octahedral" has not looked at the model.</li><li><b>"Body centred cubic":</b> the arrangement is body-centred, but the corner ion (Cl<sup>−</sup>) and centre ion (Cs<sup>+</sup>) differ, so the corner and centre are not identical points. Strictly the lattice is <b>simple cubic</b>, with one Cl<sup>−</sup> and one Cs<sup>+</sup> per lattice point. Students who say this are right.</li><li><b>Edge sticks are not contacts.</b> Cl<sup>−</sup>…Cl<sup>−</sup> along an edge is 4.12 Å, more than 2 × 1.81 Å, so the anions do not touch. Only the centre-to-corner Cs<sup>+</sup>–Cl<sup>−</sup> distance (3.57 Å) is a contact.</li></ul>', 'Traps · CsCl')}
{coach('Push 8 groups\' CsCl cells together around one corner. The shared corner Cl<sup>−</sup> now has a Cs<sup>+</sup> in each of the 8 cubes around it.',
       '"Cs<sup>+</sup> is inside a cube of 8 Cl<sup>−</sup>, and each Cl<sup>−</sup> is inside a cube of 8 Cs<sup>+</sup>. 8 : 8."',
       'Students who label the CsCl cell "4 per cell" by copying NaCl. Only 1 CsCl per cell.')}
'''
page('p3-cs', 'p3', 'Caesium chloride, CsCl', body, 'Part 3 · Build and describe')

# ================================================================ PART 3 · why
body = f'''
{box('a', '<p><b>Model answer.</b> Both salts are 1 : 1, so the question is how many anions fit around each cation. A cation is stable in a hole only if it touches the anions around it; if it is too small it "rattles", gaining no extra attraction while the anions still repel each other.</p><p>The ratio r<sub>+</sub>/r<sub>−</sub> decides it. A cation touches 8 anions in a cubic hole only if r<sub>+</sub>/r<sub>−</sub> ≥ 0.732, and 6 anions in an octahedral hole if r<sub>+</sub>/r<sub>−</sub> ≥ 0.414. For NaCl, 1.02/1.81 = <b>0.56</b>: Na<sup>+</sup> is too small for 8 neighbours, so it takes 6, the rock-salt (fcc) structure. For CsCl, 1.74/1.81 = <b>0.96</b>: Cs<sup>+</sup> is large enough to touch 8 Cl<sup>−</sup>, and more nearest-neighbour attractions give a lower energy, so it takes the 8 : 8 CsCl structure.</p>', 'Answer · why fcc for Na⁺, "bcc" for Cs⁺')}
<div class="grid5">{fig('rr_oct_lim')}{fig('rr_cub_lim')}{fig('rr_na_oct')}{fig('rr_na_cub')}{fig('rr_cs_cub')}</div>
<div class="cols2">
{box('w', '<p><b>Octahedral limit.</b> Slice through the cation and 4 of its 6 anions: a square. At the limit the anions touch along the edge, so the edge is 2r<sub>−</sub>. The diagonal is 2(r<sub>+</sub> + r<sub>−</sub>) = √2 × 2r<sub>−</sub>, so r<sub>+</sub>/r<sub>−</sub> = √2 − 1 = 0.414.</p><p><b>Cubic limit.</b> Anions on the cube corners touch along the edge: edge = 2r<sub>−</sub>. Cation–anion contact runs along the body diagonal: √3 × edge = 2(r<sub>+</sub> + r<sub>−</sub>), so r<sub>+</sub>/r<sub>−</sub> = √3 − 1 = 0.732.</p>', 'Where 0.414 and 0.732 come from')}
{box('n', '<ul class="tight"><li>These are <b>lower</b> limits: CN 6 from 0.414 to 0.732, CN 8 above 0.732.</li><li>Radii here are Shannon ionic radii: Na<sup>+</sup> 1.02 Å (CN 6), Cs<sup>+</sup> 1.74 Å (CN 8), Cl<sup>−</sup> 1.81 Å. Other tables give slightly different ratios (Pauling: 0.52 and 0.93); the conclusion is the same.</li><li>Madelung constants: NaCl 1.748, CsCl 1.763 (8 neighbours give slightly more attraction).</li><li>The rule is a guide, not a law: KCl (0.76) and RbCl (0.84) are still rock salt, and CsCl itself turns into the rock-salt form above about 470 °C.</li></ul>', 'For your understanding')}
</div>
'''
page('p3-why', 'p3', 'Why Na<sup>+</sup> takes 6 neighbours and Cs<sup>+</sup> takes 8', body, 'Part 3 · the explanation')

# ================================================================ KEY
body = f'''
<div class="cols2">
{box('a', '<p><b>[Cr(CO)<sub>6</sub>]</b><br>E, 3C<sub>4</sub>, 3C<sub>2</sub> (= C<sub>4</sub><sup>2</sup>), 4C<sub>3</sub>, 6C<sub>2</sub>′, <i>i</i>, 3S<sub>4</sub>, 4S<sub>6</sub>, 3σ<sub>h</sub>, 6σ<sub>d</sub>.<br><b>48 operations</b>: 1 + 6 + 3 + 8 + 6 + 1 + 6 + 8 + 3 + 6.</p><p><b>Naphthalene</b><br>E, C<sub>2</sub>(z), C<sub>2</sub>(y), C<sub>2</sub>(x), <i>i</i>, σ(xy), σ(xz), σ(yz).<br><b>8 operations</b>, one per element.</p><p class="small">Point groups (not asked): O<sub>h</sub> and D<sub>2h</sub>.</p>', 'Part 1 · 20 marks')}
{box('a', '<p>Any parallelogram cell whose two edges are true repeats of the pattern, with corners on identical points. The primitive cell holds 1 lattice point. Several cells can be right for one sheet; the primitive one is the simplest.</p><p>Per-sheet answers: see the add-on.</p>', 'Part 2 · 10 marks')}
</div>
{box('a', '<table class="t"><thead><tr><th></th><th>NaCl</th><th>CsCl</th></tr></thead><tbody>'
 '<tr><td>Anions</td><td>8 × ⅛ + 6 × ½ = 4 Cl<sup>−</sup></td><td>8 × ⅛ = 1 Cl<sup>−</sup></td></tr>'
 '<tr><td>Cations</td><td>12 × ¼ + 1 = 4 Na<sup>+</sup></td><td>1 Cs<sup>+</sup></td></tr>'
 '<tr><td>Formula units</td><td>4</td><td>1</td></tr>'
 '<tr><td>Cation hole</td><td>octahedral (CN 6)</td><td>cubic (CN 8): neither oct nor tet</td></tr>'
 '<tr><td>Anion site</td><td>octahedral (CN 6)</td><td>cubic (CN 8)</td></tr>'
 '<tr><td>Tetrahedral holes</td><td>8 per cell, empty</td><td>–</td></tr>'
 '<tr><td>Lattice</td><td>fcc</td><td>simple cubic ("bcc" arrangement)</td></tr>'
 '<tr><td>r<sub>+</sub>/r<sub>−</sub></td><td>0.56 (0.414–0.732)</td><td>0.96 (≥ 0.732)</td></tr></tbody></table>'
 '<p><b>Explanation must have:</b> the radius ratio for each salt, the idea that a cation must touch its neighbours (too small rattles), and that Cs<sup>+</sup> is large enough for 8 neighbours while Na<sup>+</sup> fits only 6.</p>', 'Part 3 · 20 marks')}
{box('n', '<p><b>Marking against students\' own labels.</b> Each student numbers atoms their own way. Check that their after-drawing is consistent with their before-drawing for the element they name, rather than matching these numbers. Accept fuller answers than the scheme (for example S<sub>4</sub>, S<sub>6</sub>, "cubic hole", "simple cubic lattice") as correct.</p>')}
'''
page('key', 'key', 'Answer key', body, 'For marking')

# ================================================================ APP
body = f'''
<p class="intro"><b>Lab 3 Bench</b> is one app with three tabs, one per part. On the iPad, open it from the Home Screen; after the first load it works without Wi-Fi.</p>
<table class="t">
<thead><tr><th>Tab</th><th>What it does</th><th>Best use at the bench</th></tr></thead><tbody>
<tr><td><b>Part 1 · Symmetry</b></td><td>[Cr(CO)<sub>6</sub>] and naphthalene in 3D. ▶ plays each element's move; numbers travel with the atoms. Dashed buttons try tempting moves that fail (C<sub>6</sub>, C<sub>8</sub>, "benzene thinking"). The counter tracks how many of the 48 or 8 operations you have found.</td><td>Show the S<sub>4</sub> and S<sub>6</sub> moves slowly (Slow). Show C<sub>2</sub>(z) next to <i>i</i> on naphthalene.</td></tr>
<tr><td><b>Part 2 · Unit cells</b></td><td>Six practice patterns with live checking of the blue cell (drag its 3 handles), Tile it, Shift test, Common mistake, Show answer. <b>Load a photo</b> of a real sheet to try cells on it.</td><td>Photograph a student's sheet, drag the cell onto it, and run the shift test together.</td></tr>
<tr><td><b>Part 3 · NaCl &amp; CsCl</b></td><td>Bench model, space-filling or cut-at-the-cell views; 1 or 8 cells. Chips highlight corners, edges, faces, centre with their shares, the coordination octahedron or cube, tetrahedral holes and lattice points. A radius-ratio slider shows the cation touching or rattling.</td><td>"Cut at the cell" makes the ⅛, ¼, ½ shares visible. Slide r<sub>+</sub>/r<sub>−</sub> from 0.56 to 0.96 while explaining.</td></tr>
</tbody></table>
<div class="cols2">
{box('n', '<p><b>Student mode</b> (top right) hides answers: point groups, totals, hole names. <b>Present</b> hides the side panel for showing on a larger screen.</p>')}
{box('n', '<p><b>Part 2 add-on.</b> When the tile sheets arrive: photograph each sheet flat-on in good light and send the photos. The cells are found by computer, checked by eye, drawn onto your photos in a short add-on PDF, and added to the app as "Lab sheets" with the answer key.</p>', 'Tomorrow')}
</div>
'''
page('app', 'app', 'Using Lab 3 Bench', body, 'The app')

CSS = fontfaces() + '''
@page { size: 7.5in 10.667in; margin: 0; }
:root { --ink:#121826; --muted:#5a6475; --line:#d9dfe8; --accent:#1d4ed8; --bg:#ffffff; --chip:#eef2f7; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: 'IBM Plex Sans', system-ui, sans-serif; color: var(--ink); font-size: 11.4px; line-height: 1.42; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 720px; height: 1024px; position: relative; overflow: hidden; page-break-after: always; break-after: page; padding: 0 30px; display: flex; flex-direction: column; background: #fff; }
nav { display: flex; gap: 4px; padding: 14px 0 10px; border-bottom: 1px solid var(--line); }
nav a { flex: 1; text-align: center; text-decoration: none; color: var(--muted); font-weight: 600; font-size: 10.5px; padding: 5px 0; border-radius: 7px; background: var(--chip); }
nav a.on { background: var(--accent); color: #fff; }
.head { padding: 12px 0 8px; }
.kick { font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
h1 { font-size: 22px; margin: 2px 0 0; line-height: 1.15; text-wrap: balance; }
h2 { font-size: 14px; margin: 4px 0 0; }
.body { flex: 1; display: flex; flex-direction: column; gap: 9px; min-height: 0; }
footer { display: flex; justify-content: space-between; color: var(--muted); font-size: 9.5px; padding: 8px 0 14px; border-top: 1px solid var(--line); }
p { margin: 0 0 5px; } p:last-child { margin-bottom: 0; }
ul { margin: 2px 0 4px; padding-left: 16px; } li { margin: 1px 0; }
ul.tight li { margin: 0; }
.intro { color: var(--ink); margin: 0; }
.small { font-size: 10.2px; color: var(--muted); }
sub, sup { font-size: 72%; line-height: 0; }
.box { border-radius: 10px; padding: 8px 11px 9px; border: 1px solid; position: relative; }
.box .bl { font-size: 9.5px; letter-spacing: .08em; text-transform: uppercase; font-weight: 700; margin-bottom: 3px; }
.box.q { background: #f1f5f9; border-color: #cbd5e1; } .box.q .bl { color: #475569; }
.box.t { background: #f5f3ff; border-color: #ddd6fe; } .box.t .bl { color: #6d28d9; }
.box.w { background: #eff6ff; border-color: #bfdbfe; } .box.w .bl { color: #1d4ed8; }
.box.a { background: #f0fdf4; border-color: #bbf7d0; } .box.a .bl { color: #15803d; }
.box.trap { background: #fffbeb; border-color: #fcd34d; } .box.trap .bl { color: #b45309; }
.box.c { background: #f0fdfa; border-color: #99f6e4; } .box.c .bl { color: #0f766e; }
.box.n, .box.k { background: #f8fafc; border-color: #e2e8f0; } .box.n .bl, .box.k .bl { color: #475569; }
.box.k { background: #fff; border-color: #94a3b8; }
.ssw { display: grid; grid-template-columns: 128px 1fr; gap: 3px 10px; } .ssw b { color: #0f766e; } .ssw p { margin: 0; }
.cols2 { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; align-items: start; }
.cols2a { display: grid; grid-template-columns: auto 1fr; gap: 10px; align-items: center; }
.cols2a > figure { width: 330px; }
.cols2a > figure figcaption { text-align: left; }
table.t { width: 100%; border-collapse: collapse; font-size: 10.8px; }
table.t th { text-align: left; font-size: 9.5px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); padding: 3px 5px; border-bottom: 1.5px solid var(--line); }
table.t td { padding: 3.5px 5px; border-bottom: 1px solid var(--line); vertical-align: top; }
.box table.t td { border-color: rgba(0,0,0,.08); }
table.t td.n { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
table.t tr.tot td { font-weight: 700; border-bottom: 0; }
.pill { display: inline-block; font-size: 9.5px; font-weight: 700; padding: 1px 7px; border-radius: 9px; white-space: nowrap; }
.pill.amber { background: #fef3c7; color: #92400e; } .pill.gray { background: #e2e8f0; color: #334155; } .pill.blue { background: #dbeafe; color: #1e40af; }
figure { margin: 0; display: flex; flex-direction: column; align-items: center; gap: 2px; }
figcaption { font-size: 9.8px; color: var(--ink); text-align: center; line-height: 1.3; max-width: 100%; }
figure.bad figcaption { color: #b42318; }
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px 4px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px 6px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; }
.grid2s { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.grid5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
.grid5 svg { width: 100%; height: auto; }
.grid4 svg, .grid3 svg { max-width: 100%; height: auto; }
figure.pat figcaption { text-align: left; font-size: 10px; }
.pairs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pair { border: 1px solid var(--line); border-radius: 10px; padding: 6px 6px 8px; }
.pair .ph { font-size: 10.5px; font-weight: 700; color: #be123c; text-align: center; margin-bottom: 2px; }
.pair .pp { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
.pair svg { width: 100%; height: auto; }
.kek { display: flex; gap: 4px; margin-top: 4px; } .kek svg { width: 50%; height: auto; }
.sw { display: inline-block; width: 18px; height: 0; border-top: 3px solid; vertical-align: middle; margin: 0 3px 0 6px; }
.sw.g { border-color: #15803d; } .sw.o { border-color: #b45309; border-top-style: dashed; } .sw.r { border-color: #b42318; border-top-style: dashed; }
.cover { justify-content: center; background: linear-gradient(180deg, #eef2ff 0%, #ffffff 46%); }
.cv { display: flex; flex-direction: column; gap: 16px; padding: 0 10px; }
h1.big { font-size: 44px; letter-spacing: -.01em; margin: 0; }
.lede { font-size: 15px; color: #334155; max-width: 560px; }
.toc { display: flex; flex-direction: column; gap: 6px; }
.toc a { display: grid; grid-template-columns: 200px 1fr; gap: 10px; padding: 10px 14px; border: 1px solid var(--line); border-radius: 10px; text-decoration: none; color: var(--ink); background: #fff; font-size: 12.5px; }
.toc a span { color: var(--muted); }
.legend { display: flex; flex-wrap: wrap; gap: 6px; }
.lg { font-size: 10px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; padding: 4px 9px; border-radius: 7px; border: 1px solid; }
.lg.q { background:#f1f5f9; border-color:#cbd5e1; color:#475569 } .lg.t { background:#f5f3ff; border-color:#ddd6fe; color:#6d28d9 } .lg.w { background:#eff6ff; border-color:#bfdbfe; color:#1d4ed8 }
.lg.a { background:#f0fdf4; border-color:#bbf7d0; color:#15803d } .lg.trap { background:#fffbeb; border-color:#fcd34d; color:#b45309 } .lg.c { background:#f0fdfa; border-color:#99f6e4; color:#0f766e } .lg.n { background:#f8fafc; border-color:#e2e8f0; color:#475569 }
'''
html = f'<!doctype html><html><head><meta charset="utf-8"><title>Lab 3 Companion</title><style>{CSS}</style></head><body>{"".join(pages)}<script>document.querySelectorAll(".pn").forEach((e,i)=>e.textContent=(i+2)+" / {len(pages)}")</script></body></html>'
out = B / 'out' / 'companion.html'; out.write_text(html)
print('pages', len(pages), 'html', len(html))
