"""Generuje SVG obrázky pre kapitolu neuronove-siete.md.

Spustenie: python img/gen_ffn_svg.py  (obrázky zapíše vedľa skriptu, alebo do priečinka z argumentu)
"""
import math
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
FONT = 'font-family="Helvetica, Arial, sans-serif" font-size="13"'
ORANGE, BLUE, GREEN, GRAY = "#e07a1f", "#2563eb", "#16a34a", "#555"


def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>\n'
            '  <defs>\n'
            '    <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">\n'
            f'      <path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/>\n    </marker>\n'
            '    <marker id="ao" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">\n'
            f'      <path d="M0,0 L10,5 L0,10 z" fill="{ORANGE}"/>\n    </marker>\n'
            '    <marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">\n'
            f'      <path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/>\n    </marker>\n'
            '  </defs>\n'
            f'  <rect width="{w}" height="{h}" fill="#ffffff"/>\n')


# ---------------------------------------------------------------- 1. sieť s váhami
def network():
    W, H = 820, 520
    s = [head(W, H)]
    s.append('  <text x="20" y="26" font-weight="bold" font-size="14">Feed-forward sieť 3 → 4 → 2: každá čiara je jedna váha (jedno naučené číslo)</text>\n')
    layers = [3, 4, 2]
    xs = [90, 270, 450]
    top, bottom = 70, 330
    pos = []
    for n, x in zip(layers, xs):
        gap = (bottom - top) / (n + 1)
        pos.append([(x, top + gap * (i + 1)) for i in range(n)])
    # váhy (pevne zvolené, aby obrázok bol stabilný)
    w1 = [[0.8, -0.4, 0.2, 1.1],
          [-0.5, 0.9, -1.2, 0.3],
          [0.3, 0.6, 0.7, -0.9]]
    w2 = [[1.0, -0.6], [-0.8, 0.4], [0.5, 1.2], [-0.3, -1.0]]
    for (la, lb, mat) in [(0, 1, w1), (1, 2, w2)]:
        for i, (x1, y1) in enumerate(pos[la]):
            for j, (x2, y2) in enumerate(pos[lb]):
                w = mat[i][j]
                col = ORANGE if w > 0 else BLUE
                sw = 0.6 + 3.2 * abs(w)
                op = 0.35 + 0.5 * min(abs(w), 1.2) / 1.2
                hl = la == 0 and j == 0
                s.append(f'  <line x1="{x1 + 22}" y1="{y1:.1f}" x2="{x2 - 22}" y2="{y2:.1f}" stroke="{col}" '
                         f'stroke-width="{sw:.1f}" stroke-opacity="{1 if hl else op:.2f}"/>\n')
    # popisy váh na zvýraznenom neuróne h1
    hx, hy = pos[1][0]
    for i, (x1, y1) in enumerate(pos[0]):
        w = w1[i][0]
        t = 0.55
        lx = x1 + 22 + (hx - 22 - x1 - 22) * t
        ly = y1 + (hy - y1) * t
        s.append(f'  <rect x="{lx - 20:.1f}" y="{ly - 11:.1f}" width="40" height="18" rx="9" fill="#fff" stroke="{ORANGE if w > 0 else BLUE}"/>\n')
        s.append(f'  <text x="{lx:.1f}" y="{ly + 3:.1f}" text-anchor="middle" font-size="11" fill="{ORANGE if w > 0 else BLUE}">{f"{w:+.1f}".replace(".", ",").replace("-", "−")}</text>\n')
    names = [["x_{1}", "x_{2}", "x_{3}"], ["h_{1}", "h_{2}", "h_{3}", "h_{4}"], ["y_{1}", "y_{2}"]]
    fills = ["#dbeafe", "#f3f4f6", "#dcfce7"]
    strokes = [BLUE, "#999", GREEN]
    vals = [["0,9", "0,2", "0,6"], None, None]
    for li, layer in enumerate(pos):
        for ni, (x, y) in enumerate(layer):
            sw = 2.5 if (li == 1 and ni == 0) else 1.2
            st = ORANGE if (li == 1 and ni == 0) else strokes[li]
            s.append(f'  <circle cx="{x}" cy="{y:.1f}" r="22" fill="{fills[li]}" stroke="{st}" stroke-width="{sw}"/>\n')
            s.append(f'  <text x="{x}" y="{y + 5:.1f}" text-anchor="middle" font-weight="bold">{names[li][ni]}</text>\n')
            if vals[li]:
                s.append(f'  <text x="{x - 32}" y="{y + 5:.1f}" text-anchor="end" fill="{BLUE}">{vals[li][ni]}</text>\n')
    for x, lab, sub in [(90, "vstupná vrstva", "dáta (napr. pixely)"),
                        (270, "skrytá vrstva", "+ aktivácia (ReLU)"),
                        (450, "výstupná vrstva", "+ softmax")]:
        s.append(f'  <text x="{x}" y="362" text-anchor="middle" font-weight="bold">{lab}</text>\n')
        s.append(f'  <text x="{x}" y="378" text-anchor="middle" font-size="11" fill="{GRAY}">{sub}</text>\n')
    # matice
    s.append(f'  <text x="98" y="58" font-size="12" fill="#c2410c">W_{{1}}: 3 × 4 = 12 váh + 4 biasy</text>\n')
    s.append(f'  <text x="288" y="58" font-size="12" fill="#c2410c">W_{{2}}: 4 × 2 = 8 váh + 2 biasy</text>\n')

    # detail neurónu
    bx, by = 525, 70
    s.append(f'  <rect x="{bx}" y="{by}" width="280" height="290" rx="8" fill="#fffaf5" stroke="{ORANGE}" stroke-width="1.5"/>\n')
    s.append(f'  <text x="{bx + 14}" y="{by + 24}" font-weight="bold">Čo počíta jeden neurón (h_{{1}})</text>\n')
    lines = [
        ("1. vážený súčet vstupov:", "bold", "#222"),
        ("z = x_{1}·w_{1} + x_{2}·w_{2} + x_{3}·w_{3} + b", None, "#222"),
        ("   = 0,9·0,8 + 0,2·(−0,5) + 0,6·0,3 + 0,1", None, GRAY),
        ("   = 0,72 − 0,10 + 0,18 + 0,1 = 0,90", None, GRAY),
        ("", None, "#222"),
        ("2. aktivácia (nelinearita):", "bold", "#222"),
        ("h_{1} = ReLU(z) = max(0; 0,90) = 0,90", None, "#222"),
        ("", None, "#222"),
        ("Váhy w a bias b sa učia.", None, "#c2410c"),
        ("Kladná váha = vstup neurón „budí“,", None, ORANGE),
        ("záporná váha = „tlmí“.", None, BLUE),
        ("Hrúbka čiary = veľkosť váhy.", None, GRAY),
    ]
    y = by + 52
    for txt, fw, col in lines:
        if txt:
            fwa = ' font-weight="bold"' if fw else ''
            s.append(f'  <text x="{bx + 14}" y="{y}" font-size="12" fill="{col}"{fwa}>{txt}</text>\n')
        y += 19

    # maticový zápis
    s.append('  <line x1="20" y1="402" x2="800" y2="402" stroke="#ddd"/>\n')
    s.append('  <text x="20" y="428" font-weight="bold">Celá vrstva naraz = jedno násobenie maticou</text>\n')
    eq_y = 470
    s.append(f'  <rect x="30" y="{eq_y - 22}" width="110" height="32" rx="4" fill="#dbeafe" stroke="{BLUE}"/>\n')
    s.append(f'  <text x="85" y="{eq_y - 1}" text-anchor="middle">x  (1 × 3)</text>\n')
    s.append(f'  <text x="155" y="{eq_y}" text-anchor="middle" font-size="18">·</text>\n')
    s.append(f'  <rect x="170" y="{eq_y - 30}" width="110" height="48" rx="4" fill="#fde7d4" stroke="{ORANGE}" stroke-width="1.5"/>\n')
    s.append(f'  <text x="189" y="{eq_y - 1}">W_{{1}}  (3 × 4)</text>\n')
    s.append(f'  <text x="297" y="{eq_y}" text-anchor="middle" font-size="18">+</text>\n')
    s.append(f'  <rect x="314" y="{eq_y - 22}" width="80" height="32" rx="4" fill="#fde7d4" stroke="{ORANGE}" stroke-width="1.5"/>\n')
    s.append(f'  <text x="330" y="{eq_y - 1}">b_{{1}}  (4)</text>\n')
    s.append(f'  <text x="412" y="{eq_y}" text-anchor="middle" font-size="18">→</text>\n')
    s.append(f'  <text x="470" y="{eq_y - 1}" text-anchor="middle">ReLU</text>\n')
    s.append(f'  <text x="525" y="{eq_y}" text-anchor="middle" font-size="18">→</text>\n')
    s.append(f'  <rect x="545" y="{eq_y - 22}" width="110" height="32" rx="4" fill="#f3f4f6" stroke="#999"/>\n')
    s.append(f'  <text x="600" y="{eq_y - 1}" text-anchor="middle">h  (1 × 4)</text>\n')
    s.append(f'  <text x="30" y="505" font-size="12" fill="{GRAY}">Pre dávku 64 príkladov je x matica 64 × 3 a výpočet je stále jedno násobenie, presne to, v čom je GPU rýchle.</text>\n')
    s.append('</svg>\n')
    return "".join(s)


# ---------------------------------------------------------------- 2. cyklus učenia + gradient
def learning():
    W, H = 820, 450
    s = [head(W, H)]
    s.append('  <text x="20" y="26" font-weight="bold" font-size="14">Jeden krok učenia: dopredu → chyba → späť → úprava váh, a znova</text>\n')
    boxes = [
        (40, 60, "1. dopredný priechod", "x → vrstvy → predikcia", "#dbeafe", BLUE),
        (40, 160, "2. chyba (loss)", "ako ďaleko je predikcia od cieľa", "#f3f4f6", "#999"),
        (40, 260, "3. spätné šírenie", "gradient pre každú váhu", "#fde7d4", ORANGE),
        (40, 360, "4. krok optimalizátora", "w ← w − η · gradient  (Adam)", "#dcfce7", GREEN),
    ]
    for x, y, t, sub, f, st in boxes:
        s.append(f'  <rect x="{x}" y="{y}" width="270" height="52" rx="6" fill="{f}" stroke="{st}" stroke-width="1.5"/>\n')
        s.append(f'  <text x="{x + 135}" y="{y + 22}" text-anchor="middle" font-weight="bold">{t}</text>\n')
        s.append(f'  <text x="{x + 135}" y="{y + 40}" text-anchor="middle" font-size="12" fill="#444">{sub}</text>\n')
    for y in (112, 212, 312):
        s.append(f'  <line x1="175" y1="{y}" x2="175" y2="{y + 46}" stroke="{GRAY}" stroke-width="1.5" marker-end="url(#a)"/>\n')
    s.append(f'  <path d="M310,386 L345,386 L345,86 L314,86" fill="none" stroke="{GREEN}" stroke-width="1.8" marker-end="url(#a)"/>\n')
    s.append(f'  <text x="352" y="230" font-size="12" fill="{GREEN}">ďalšia</text>\n')
    s.append(f'  <text x="352" y="245" font-size="12" fill="{GREEN}">dávka</text>\n')

    # graf lossu podľa jednej váhy
    gx, gy, gw, gh = 430, 60, 360, 300

    def L(w):
        return 0.25 * (w - 1.0) ** 2 + 0.15 * math.sin(2.2 * w) + 0.45

    wmin, wmax = -2.2, 3.6
    vals = [L(wmin + (wmax - wmin) * i / 200) for i in range(201)]
    lmin, lmax = 0.0, max(vals) * 1.05

    def px(w):
        return gx + (w - wmin) / (wmax - wmin) * gw

    def py(l):
        return gy + gh - (l - lmin) / (lmax - lmin) * gh

    s.append(f'  <line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy + gh}" stroke="#999" marker-end="url(#a)"/>\n')
    s.append(f'  <line x1="{gx}" y1="{gy + gh}" x2="{gx}" y2="{gy - 5}" stroke="#999" marker-end="url(#a)"/>\n')
    s.append(f'  <text x="{gx + gw}" y="{gy + gh + 18}" text-anchor="end" font-size="12" fill="{GRAY}">hodnota jednej váhy w</text>\n')
    s.append(f'  <text x="{gx + 6}" y="{gy + 6}" font-size="12" fill="{GRAY}">loss</text>\n')
    pts = " ".join(f"{px(wmin + (wmax - wmin) * i / 200):.1f},{py(v):.1f}" for i, v in enumerate(vals))
    s.append(f'  <polyline points="{pts}" fill="none" stroke="#333" stroke-width="2"/>\n')

    # kroky gradientného zostupu
    def dL(w):
        return 0.5 * (w - 1.0) + 0.33 * math.cos(2.2 * w)

    w = 3.2
    lr = 1.1
    path = [w]
    for _ in range(4):
        w = w - lr * dL(w)
        path.append(w)
    for a, b in zip(path, path[1:]):
        s.append(f'  <line x1="{px(a):.1f}" y1="{py(L(a)):.1f}" x2="{px(b):.1f}" y2="{py(L(b)):.1f}" stroke="{ORANGE}" '
                 f'stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#ao)"/>\n')
    for i, w in enumerate(path):
        s.append(f'  <circle cx="{px(w):.1f}" cy="{py(L(w)):.1f}" r="{5 if i == 0 else 3.5}" fill="{ORANGE}"/>\n')
    # dotyčnica v štarte
    w0 = path[0]
    k = dL(w0)
    d = 0.35
    x1, x2 = w0 - d, w0 + d
    s.append(f'  <line x1="{px(x1):.1f}" y1="{py(L(w0) - k * d):.1f}" x2="{px(x2):.1f}" y2="{py(L(w0) + k * d):.1f}" stroke="{BLUE}" stroke-width="2"/>\n')
    s.append(f'  <text x="{px(w0) - 14:.1f}" y="{py(L(w0)) - 40:.1f}" text-anchor="end" font-size="12" fill="{BLUE}">sklon = gradient</text>\n')
    s.append(f'  <text x="{px(w0) - 14:.1f}" y="{py(L(w0)) - 25:.1f}" text-anchor="end" font-size="12" fill="{BLUE}">(kladný → choď doľava)</text>\n')
    s.append(f'  <text x="{px(path[0]):.1f}" y="{py(L(path[0])) + 22:.1f}" text-anchor="middle" font-size="11" fill="{ORANGE}">štart</text>\n')
    wb = path[-1]
    s.append(f'  <text x="{px(wb):.1f}" y="{py(L(wb)) + 22:.1f}" text-anchor="middle" font-size="11" fill="{GREEN}">minimum</text>\n')
    s.append(f'  <text x="{gx}" y="{gy + gh + 40}" font-size="12" fill="#444">Gradient ukazuje, ktorým smerom loss rastie.</text>\n')
    s.append(f'  <text x="{gx}" y="{gy + gh + 56}" font-size="12" fill="#444">Váha sa posunie opačným smerom o kúsok úmerný</text>\n')
    s.append(f'  <text x="{gx}" y="{gy + gh + 72}" font-size="12" fill="#444">learning rate η. V sieti sa to deje naraz pre všetky váhy.</text>\n')
    s.append('</svg>\n')
    return "".join(s)


# ---------------------------------------------------------------- 3. SGD vs Adam
def optimizers():
    W, H = 820, 400
    s = [head(W, H)]
    s.append('  <text x="20" y="26" font-weight="bold" font-size="14">Rovnaký štart, rovnaký počet krokov: obyčajný gradient descent vs. Adam</text>\n')
    a, b = 0.05, 2.0          # f = a·x² + b·y²   (úzke, pretiahnuté údolie)

    def grad(x, y):
        return 2 * a * x, 2 * b * y

    start = (-9.0, 1.6)
    steps = 20
    # SGD
    sgd = [start]
    x, y = start
    for _ in range(steps):
        gx_, gy_ = grad(x, y)
        x, y = x - 0.46 * gx_, y - 0.46 * gy_
        sgd.append((x, y))
    # Adam
    adam = [start]
    x, y = start
    m = [0, 0]; v = [0, 0]
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.5
    for t in range(1, steps + 1):
        g = grad(x, y)
        for i in range(2):
            m[i] = b1 * m[i] + (1 - b1) * g[i]
            v[i] = b2 * v[i] + (1 - b2) * g[i] ** 2
        mh = [mi / (1 - b1 ** t) for mi in m]
        vh = [vi / (1 - b2 ** t) for vi in v]
        x -= lr * mh[0] / (math.sqrt(vh[0]) + eps)
        y -= lr * mh[1] / (math.sqrt(vh[1]) + eps)
        adam.append((x, y))

    panels = [(20, "Gradient descent (SGD): w ← w − η·g", sgd, BLUE, "#ab"),
              (420, "Adam: w ← w − η · m / (√v + ε)", adam, ORANGE, "#ao")]
    xr, yr = (-10.5, 2.5), (-2.0, 2.0)
    pw, ph = 380, 250
    for ox, title, path, col, mk in panels:
        oy = 70

        def px(xx):
            return ox + (xx - xr[0]) / (xr[1] - xr[0]) * pw

        def py(yy):
            return oy + ph - (yy - yr[0]) / (yr[1] - yr[0]) * ph

        s.append(f'  <text x="{ox}" y="{oy - 14}" font-weight="bold" fill="{col}">{title}</text>\n')
        s.append(f'  <clipPath id="c{ox}"><rect x="{ox}" y="{oy}" width="{pw}" height="{ph}"/></clipPath>\n')
        s.append(f'  <rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="#fafafa" stroke="#ddd"/>\n')
        s.append(f'  <g clip-path="url(#c{ox})">\n')
        for c in [0.05, 0.25, 0.7, 1.5, 2.8, 4.5, 6.8, 9.5]:
            rx = math.sqrt(c / a) / (xr[1] - xr[0]) * pw
            ry = math.sqrt(c / b) / (yr[1] - yr[0]) * ph
            s.append(f'    <ellipse cx="{px(0):.1f}" cy="{py(0):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#c7c7c7"/>\n')
        pts = " ".join(f"{px(p[0]):.1f},{py(p[1]):.1f}" for p in path)
        s.append(f'    <polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.8"/>\n')
        for p in path:
            s.append(f'    <circle cx="{px(p[0]):.1f}" cy="{py(p[1]):.1f}" r="2.4" fill="{col}"/>\n')
        s.append('  </g>\n')
        s.append(f'  <circle cx="{px(0):.1f}" cy="{py(0):.1f}" r="5" fill="none" stroke="{GREEN}" stroke-width="2"/>\n')
        s.append(f'  <text x="{px(0) + 8:.1f}" y="{py(0) - 8:.1f}" font-size="11" fill="{GREEN}">minimum</text>\n')
        s.append(f'  <circle cx="{px(start[0]):.1f}" cy="{py(start[1]):.1f}" r="5" fill="{col}"/>\n')
        s.append(f'  <text x="{px(start[0]) + 8:.1f}" y="{py(start[1]) - 6:.1f}" font-size="11" fill="{col}">štart</text>\n')
        end = path[-1]
        s.append(f'  <text x="{ox + pw}" y="{oy + ph + 16}" text-anchor="end" font-size="11" fill="{GRAY}">po {steps} krokoch: vzdialenosť od minima {f"{math.hypot(*end):.2f}".replace(".", ",")}</text>\n')
    s.append(f'  <text x="20" y="362" font-size="12" fill="#444">Loss je úzke údolie: v smere y strmé, v smere x takmer ploché. SGD v strmom smere skáče zo steny na stenu</text>\n')
    s.append(f'  <text x="20" y="378" font-size="12" fill="#444">a v plochom sa ledva hýbe. Adam delí krok veľkosťou gradientu (√v), takže obe váhy idú podobným tempom,</text>\n')
    s.append(f'  <text x="20" y="394" font-size="12" fill="#444">a momentum (m) vyhladí kmitanie.</text>\n')
    s.append('</svg>\n')
    return "".join(s), sgd[-1], adam[-1]


# ---------------------------------------------------------------- 4. aktivačné funkcie
def activations():
    W, H = 820, 545

    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    funcs = [
        ("Sigmoid", "1 / (1 + e^{−z})", sigmoid, (-0.2, 1.2), "výstup 0…1; staršie siete, brány v LSTM"),
        ("Tanh", "(e^{z} − e^{−z}) / (e^{z} + e^{−z})", math.tanh, (-1.2, 1.2), "výstup −1…1; RNN, LSTM"),
        ("ReLU", "max(0, z)", lambda x: max(0.0, x), (-1.2, 3.2), "štandard; rýchla, jednoduchá"),
        ("Leaky ReLU", "z, pre záporné z iba α·z", lambda x: x if x > 0 else 0.05 * x, (-1.2, 3.2), "neuróny „neumrú“"),
        ("GELU", "z · Φ(z)", lambda x: 0.5 * x * (1 + math.erf(x / math.sqrt(2))), (-1.2, 3.2), "BERT, GPT-2, GPT-3"),
        ("SiLU / Swish", "z · sigmoid(z)", lambda x: x * sigmoid(x), (-1.2, 3.2), "v SwiGLU: Llama, OLMo"),
    ]
    s = [head(W, H)]
    s.append('  <text x="20" y="26" font-weight="bold" font-size="14">Aktivačné funkcie: čo neurón urobí so svojím váženým súčtom z</text>\n')
    cols, pw, ph = 3, 240, 150
    for k, (name, formula, f, yr, note) in enumerate(funcs):
        ox = 25 + (k % cols) * 265
        oy = 60 + (k // cols) * 225
        xr = (-4.0, 4.0) if yr[1] < 2 else (-3.0, 3.0)

        def px(x):
            return ox + (x - xr[0]) / (xr[1] - xr[0]) * pw

        def py(y):
            return oy + 30 + ph - (y - yr[0]) / (yr[1] - yr[0]) * ph

        col = ORANGE if k >= 2 else BLUE
        s.append(f'  <text x="{ox}" y="{oy + 2}" font-weight="bold">{name}</text>\n')
        s.append(f'  <text x="{ox}" y="{oy + 20}" font-size="12" fill="{GRAY}">{formula}</text>\n')
        s.append(f'  <rect x="{ox}" y="{oy + 30}" width="{pw}" height="{ph}" fill="#fafafa" stroke="#e5e5e5"/>\n')
        s.append(f'  <line x1="{ox}" y1="{py(0):.1f}" x2="{ox + pw}" y2="{py(0):.1f}" stroke="#bbb"/>\n')
        s.append(f'  <line x1="{px(0):.1f}" y1="{oy + 30}" x2="{px(0):.1f}" y2="{oy + 30 + ph}" stroke="#bbb"/>\n')
        for gy in ([1.0] if yr[1] < 2 else [1.0, 2.0, 3.0]) + ([-1.0] if yr[0] < -1 else []):
            s.append(f'  <line x1="{ox}" y1="{py(gy):.1f}" x2="{ox + pw}" y2="{py(gy):.1f}" stroke="#eee" stroke-dasharray="3 3"/>\n')
            s.append(f'  <text x="{px(0) - 4:.1f}" y="{py(gy) + 4:.1f}" text-anchor="end" font-size="10" fill="#999">{gy:g}</text>\n')
        n = 160
        pts = []
        for i in range(n + 1):
            x = xr[0] + (xr[1] - xr[0]) * i / n
            pts.append(f"{px(x):.1f},{py(f(x)):.1f}")
        s.append(f'  <polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.5"/>\n')
        s.append(f'  <text x="{ox + pw - 4}" y="{py(0) + 14:.1f}" text-anchor="end" font-size="10" fill="#999">z</text>\n')
        s.append(f'  <text x="{ox}" y="{oy + ph + 50}" font-size="12" fill="#444">{note}</text>\n')
    s.append(f'  <text x="20" y="532" font-size="12" fill="#444">Modré: „saturujú“ (pre veľké |z| sú ploché, gradient ≈ 0). Oranžové: pre kladné z rastú bez hranice, preto sa nimi trénujú hlboké siete.</text>\n')
    s.append('</svg>\n')
    return "".join(s)


def scripts(svg):
    def seg(m):
        out, txt = [], m.group(1)
        parts = re.split(r'([_^])\{(.*?)\}', txt)
        out.append(parts[0])
        for i in range(1, len(parts), 3):
            kind, inner, rest = parts[i], parts[i + 1], parts[i + 2]
            d = 4 if kind == "_" else -6
            out.append(f'<tspan dy="{d}" font-size="10">{inner}</tspan>')
            if rest:
                out.append(f'<tspan dy="{-d}">{rest}</tspan>')
        return ">" + "".join(out) + "<"
    return re.sub(r'>([^<>]*[_^]\{[^<>]*)<', seg, svg)


_net = network
network = lambda: scripts(_net())
_act = activations
activations = lambda: scripts(_act())

(OUT / "ffn-siet-vahy.svg").write_text(network())
(OUT / "ffn-ucenie.svg").write_text(learning())
svg, sgd_end, adam_end = optimizers()
(OUT / "adam-vs-sgd.svg").write_text(svg)
(OUT / "aktivacne-funkcie.svg").write_text(activations())
