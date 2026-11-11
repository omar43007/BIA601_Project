"""Create the figures used in the report with Pillow (no extra dependencies)."""

import math
import os

from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "GA": (46, 117, 182),
    "PSO": (237, 125, 49),
    "ACO": (84, 130, 53),
}
LIGHT = {
    "GA": (214, 228, 244),
    "PSO": (252, 228, 214),
    "ACO": (221, 235, 210),
}

FONT_DIR = "C:/Windows/Fonts"


def _font(size, bold=False):
    path = os.path.join(FONT_DIR, "arialbd.ttf" if bold else "arial.ttf")
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _canvas(w, h):
    img = Image.new("RGB", (w, h), (255, 255, 255))
    return img, ImageDraw.Draw(img)


def _title(draw, text, width, y=24, size=32):
    f = _font(size, True)
    tw = draw.textlength(text, font=f)
    draw.text(((width - tw) / 2, y), text, font=f, fill=(30, 30, 30))


def _legend_row(draw, width, y, items):
    f = _font(22)
    total = 0
    gaps = []
    for label, _ in items:
        w = 46 + 10 + draw.textlength(label, font=f)
        gaps.append(w)
        total += w + 40
    x = (width - total + 40) / 2
    for (label, color), w in zip(items, gaps):
        draw.line([x, y + 11, x + 40, y + 11], fill=color, width=6)
        draw.text((x + 50, y), label, font=f, fill=(40, 40, 40))
        x += w + 40


def _ylabel(img, text, x, cy):
    f = _font(24)
    tmp = Image.new("RGB", (500, 40), (255, 255, 255))
    d = ImageDraw.Draw(tmp)
    d.text((0, 0), text, font=f, fill=(30, 30, 30))
    w = int(d.textlength(text, font=f)) + 6
    tmp = tmp.crop((0, 0, w, 40)).rotate(90, expand=True)
    img.paste(tmp, (x, int(cy - tmp.height / 2)))


def _frame(draw, left, top, right, bottom, title=None):
    draw.rectangle([left, top, right, bottom], outline=(40, 40, 40), width=2)
    if title:
        f = _font(24, True)
        tw = draw.textlength(title, font=f)
        draw.text(((left + right - tw) / 2, top - 38), title, font=f,
                  fill=(40, 40, 40))


def _y_grid(draw, left, top, right, bottom, ymin, ymax, fmt="%.0f"):
    f = _font(19)
    for i in range(6):
        val = ymin + (ymax - ymin) * i / 5
        y = bottom - (bottom - top) * i / 5
        draw.line([left, y, right, y], fill=(228, 228, 228), width=1)
        txt = fmt % val
        tw = draw.textlength(txt, font=f)
        draw.text((left - tw - 10, y - 11), txt, font=f, fill=(60, 60, 60))


def _x_grid(draw, left, top, right, bottom, xmax):
    f = _font(19)
    for i in range(6):
        val = xmax * i / 5
        x = left + (right - left) * i / 5
        draw.line([x, top, x, bottom], fill=(240, 240, 240), width=1)
        txt = "%.0f" % val
        tw = draw.textlength(txt, font=f)
        draw.text((x - tw / 2, bottom + 10), txt, font=f, fill=(60, 60, 60))


def convergence_plot(path, name, cur, n_customers):
    w, h = 1600, 1000
    img, draw = _canvas(w, h)
    left, top, right, bottom = 150, 150, w - 70, h - 140
    all_means = [v for algo in cur for v in cur[algo]["mean"]]
    ymin = min(all_means) * 0.95
    ymax = max(all_means) * 1.03
    xmax = max(len(cur[a]["mean"]) for a in cur) - 1

    _title(draw, "Convergence on the %s instance (%d customers)" %
           (name, n_customers), w)
    _legend_row(draw, w, 82, [("GA", COLORS["GA"]), ("PSO", COLORS["PSO"]),
                              ("ACO", COLORS["ACO"])])
    _frame(draw, left, top, right, bottom)
    _y_grid(draw, left, top, right, bottom, ymin, ymax)
    _x_grid(draw, left, top, right, bottom, xmax)
    f = _font(22)
    draw.text(((left + right) / 2 - 40, bottom + 45), "Iteration", font=f,
              fill=(30, 30, 30))
    _ylabel(img, "Best tour length", 18, (top + bottom) / 2)

    def px(i):
        return left + (right - left) * i / xmax

    def py(v):
        return bottom - (bottom - top) * (v - ymin) / (ymax - ymin)

    for algo in ("GA", "PSO", "ACO"):
        means = cur[algo]["mean"]
        stds = cur[algo]["std"]
        upper = [py(means[i] + stds[i]) for i in range(len(means))]
        lower = [py(max(0.0, means[i] - stds[i])) for i in range(len(means))]
        poly = [(px(i), upper[i]) for i in range(len(means))]
        poly += [(px(i), lower[i]) for i in range(len(means) - 1, -1, -1)]
        draw.polygon(poly, fill=LIGHT[algo])

    for algo in ("GA", "PSO", "ACO"):
        pts = [(px(i), py(v)) for i, v in enumerate(cur[algo]["mean"])]
        draw.line(pts, fill=COLORS[algo], width=5, joint="curve")

    img.save(path, dpi=(150, 150))


def _percentile(sorted_vals, p):
    k = (len(sorted_vals) - 1) * p
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def box_plot(path, rows, instances):
    w, h = 1600, 1000
    img, draw = _canvas(w, h)
    names = list(instances)
    algos = ["GA", "PSO", "ACO"]
    _title(draw, "Final solution quality over 10 independent runs", w)
    _legend_row(draw, w, 82, [("GA", COLORS["GA"]), ("PSO", COLORS["PSO"]),
                              ("ACO", COLORS["ACO"])])

    left, right = 95, w - 40
    top, bottom = 160, 850
    gap = 55
    panel_w = (right - left - 2 * gap) / 3

    for gi, name in enumerate(names):
        x0 = left + gi * (panel_w + gap)
        x1 = x0 + panel_w
        vals_all = [r["best_cost"] for r in rows if r["instance"] == name]
        ymin = min(vals_all) * 0.97
        ymax = max(vals_all) * 1.03
        _frame(draw, x0, top, x1, bottom, name)
        _y_grid(draw, x0, top, x1, bottom, ymin, ymax)

        def py(v):
            return bottom - (bottom - top) * (v - ymin) / (ymax - ymin)

        box_w = panel_w / 5.5
        for bi, algo in enumerate(algos):
            vals = sorted(r["best_cost"] for r in rows
                          if r["instance"] == name and r["algorithm"] == algo)
            cx = x0 + panel_w * (bi + 0.5) / 3
            q1 = _percentile(vals, 0.25)
            q3 = _percentile(vals, 0.75)
            med = _percentile(vals, 0.5)
            lo, hi = vals[0], vals[-1]
            col = COLORS[algo]

            draw.line([cx, py(lo), cx, py(hi)], fill=(70, 70, 70), width=2)
            draw.line([cx - box_w / 3, py(lo), cx + box_w / 3, py(lo)],
                      fill=(70, 70, 70), width=2)
            draw.line([cx - box_w / 3, py(hi), cx + box_w / 3, py(hi)],
                      fill=(70, 70, 70), width=2)
            draw.rectangle([cx - box_w / 2, py(q3), cx + box_w / 2, py(q1)],
                           fill=LIGHT[algo], outline=col, width=3)
            draw.line([cx - box_w / 2, py(med), cx + box_w / 2, py(med)],
                      fill=col, width=4)
            mean = sum(vals) / len(vals)
            r = 5
            draw.ellipse([cx - r, py(mean) - r, cx + r, py(mean) + r],
                         fill=(30, 30, 30))
            f = _font(20, True)
            tw = draw.textlength(algo, font=f)
            draw.text((cx - tw / 2, bottom + 14), algo, font=f, fill=(40, 40, 40))

    _ylabel(img, "Final tour length", 18, (top + bottom) / 2)
    img.save(path, dpi=(150, 150))


def runtime_plot(path, summary, instances):
    w, h = 1600, 950
    img, draw = _canvas(w, h)
    names = list(instances)
    algos = ["GA", "PSO", "ACO"]
    times = {a: [next(s["mean_time"] for s in summary[n] if s["algorithm"] == a)
                 for n in names] for a in algos}
    allv = [v for a in algos for v in times[a]]
    ymin = min(allv) * 0.6
    ymax = max(allv) * 1.45

    _title(draw, "Average running time per run (log scale)", w)
    _legend_row(draw, w, 82, [("GA", COLORS["GA"]), ("PSO", COLORS["PSO"]),
                              ("ACO", COLORS["ACO"])])
    left, top, right, bottom = 160, 150, w - 70, 820
    _frame(draw, left, top, right, bottom)

    # logarithmic grid with readable second values
    f = _font(19)
    ticks = [t for t in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
             if ymin <= t <= ymax]
    lo, hi = math.log10(ymin), math.log10(ymax)
    for t in ticks:
        y = bottom - (bottom - top) * (math.log10(t) - lo) / (hi - lo)
        draw.line([left, y, right, y], fill=(228, 228, 228), width=1)
        txt = "%.2f" % t if t < 1 else "%.1f" % t
        tw = draw.textlength(txt, font=f)
        draw.text((left - tw - 10, y - 11), txt, font=f, fill=(60, 60, 60))

    group_w = (right - left) / len(names)
    bar_w = group_w / 5.2
    for gi, name in enumerate(names):
        center = left + group_w * (gi + 0.5)
        for bi, algo in enumerate(algos):
            x = center + (bi - 1) * (bar_w + 6)
            t = times[algo][gi]
            y = bottom - (bottom - top) * (math.log10(t) - lo) / (hi - lo)
            draw.rectangle([x - bar_w / 2, y, x + bar_w / 2, bottom],
                           fill=COLORS[algo], outline=(255, 255, 255))
            txt = "%.2f" % t
            fs = _font(18, True)
            tw = draw.textlength(txt, font=fs)
            draw.text((x - tw / 2, y - 24), txt, font=fs, fill=(40, 40, 40))
        f2 = _font(22, True)
        tw = draw.textlength(name, font=f2)
        draw.text((center - tw / 2, bottom + 18), name, font=f2, fill=(40, 40, 40))

    _ylabel(img, "Time (seconds)", 18, (top + bottom) / 2)
    img.save(path, dpi=(150, 150))


def route_plot(path, inst, tour, algo):
    size = 900
    img, draw = _canvas(size, size + 60)
    margin = 70
    _title(draw, "Best route found by %s on the %s instance" % (algo, inst.name),
           size, y=18, size=30)

    def pxy(i):
        x, y = inst.coords[i]
        return (margin + (size - 2 * margin) * x / 100.0,
                size - 20 - margin - (size - 2 * margin) * y / 100.0)

    pts = [pxy(i) for i in [0] + tour + [0]]
    draw.line(pts, fill=(46, 117, 182), width=5, joint="curve")

    f_id = _font(18, True)
    for i in range(1, inst.n):
        x, y = pxy(i)
        draw.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(46, 117, 182),
                     outline=(255, 255, 255), width=2)
        draw.text((x + 12, y - 10), str(i), font=f_id, fill=(40, 40, 40))
    x, y = pxy(0)
    draw.rectangle([x - 13, y - 13, x + 13, y + 13], fill=(192, 0, 0),
                   outline=(255, 255, 255), width=2)
    draw.text((x + 18, y - 12), "Depot", font=_font(20, True), fill=(192, 0, 0))

    draw.text((margin, size + 18), "Total length: %.2f" % inst.tour_length(tour),
              font=_font(22), fill=(40, 40, 40))
    img.save(path, dpi=(150, 150))


def make_all(root, rows, summary, exact, convergence, instances):
    fig_dir = os.path.join(root, "results", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    for name, inst in instances.items():
        convergence_plot(os.path.join(fig_dir, "convergence_%s.png" % name),
                         name, convergence[name], inst.n - 1)
    box_plot(os.path.join(fig_dir, "boxplot.png"), rows, instances)
    runtime_plot(os.path.join(fig_dir, "runtime.png"), summary, instances)

    small_rows = [r for r in rows if r["instance"] == "small" and r["algorithm"] == "ACO"]
    best_row = min(small_rows, key=lambda r: r["best_cost"])
    tour = [int(x) for x in best_row["best_tour"].split("-")]
    route_plot(os.path.join(fig_dir, "route_small.png"), instances["small"], tour, "ACO")
