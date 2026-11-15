"""Redraw the Pareto figure (revision success vs LLM calls/turn) from
results/metrics.json. Replaces the repo's auto-generated results/pareto.png,
whose per-point annotations collide in the top-left cluster.

Usage: python redraw_pareto.py <metrics.json> <out.png>
Palette: Okabe-Ito (CVD-safe literature standard) + distinct marker shapes as
secondary encoding; the bundled JS validator could not run (no node on this
machine), noted as a limitation.
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS = sys.argv[1] if len(sys.argv) > 1 else "metrics.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "figures/pareto.png"

# key -> (legend label, color, marker, filled)
FAMILY = {
    "always_global":     ("Always-Global (sampled)",       "#D55E00", "o", False),
    "always_global_det": ("Always-Global (deterministic)", "#D55E00", "o", True),
    "static_rules":      ("Static rules",                  "#888888", "s", False),
    "static_cost_aware": ("Static rules (cost-aware)",     "#888888", "s", True),
    "bc":                ("BC",                            "#0072B2", "o", False),
    "bc_aug":            ("BC + aug",                      "#0072B2", "^", True),
    "bc_dagger3":        ("BC + DAgger (3)",               "#0072B2", "v", True),
    "bc_aug_dagger3":    ("BC + aug + DAgger (3)",         "#0072B2", "D", True),
    "oracle":            ("Scripted expert",               "#000000", "*", True),
}

data = json.load(open(METRICS, encoding="utf-8"))["systems"]
rows = {}
for key, (label, color, marker, filled) in FAMILY.items():
    s = data[key]["summary"]
    rows[key] = (
        s["llm_calls_per_turn"]["mean"],
        s["revision_success_rate"]["mean"] * 100.0,
        s["unaffected_preserved"]["mean"] * 100.0,
        label, color, marker, filled,
    )

plt.rcParams.update({
    "font.size": 8, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "figure.dpi": 300,
})

fig, (ax1, ax2) = plt.subplots(
    1, 2, sharey=True, figsize=(3.4, 2.75),
    gridspec_kw={"width_ratios": [3.2, 1.0], "wspace": 0.06},
)

for ax in (ax1, ax2):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5, pad=1.5)

for key, (x, y, pres, label, color, marker, filled) in rows.items():
    # Legend handles come from ax1; the two always-global points coincide in
    # the right panel and are redrawn there as concentric markers below.
    if filled:
        ax1.scatter(x, y, s=46, c=color, marker=marker,
                    edgecolors="white", linewidths=0.5, zorder=3,
                    label=f"{label} ({pres:.0f}%)")
    else:
        ax1.scatter(x, y, s=52, facecolors="none", edgecolors=color,
                    marker=marker, linewidths=1.1, zorder=3,
                    label=f"{label} ({pres:.0f}%)")
    if key not in ("always_global", "always_global_det"):
        if filled:
            ax2.scatter(x, y, s=46, c=color, marker=marker,
                        edgecolors="white", linewidths=0.5, zorder=3)
        else:
            ax2.scatter(x, y, s=52, facecolors="none", edgecolors=color,
                        marker=marker, linewidths=1.1, zorder=3)

# Coincident always-global points (both 4.19 calls, 100% success): draw as
# concentric markers so both the sampled (open, outer) and deterministic
# (filled, inner) systems stay visible at the same position.
ag_x = rows["always_global"][0]
ax2.scatter([ag_x], [100.0], s=95, facecolors="none",
            edgecolors=FAMILY["always_global"][1], linewidths=1.2, zorder=3)
ax2.scatter([ag_x], [100.0], s=30, c=FAMILY["always_global_det"][1],
            marker="o", edgecolors="white", linewidths=0.4, zorder=4)

# Left panel: the cluster 0.68-1.10; right panel: always-global at 4.19.
ax1.set_xlim(0.68, 1.10)
ax1.set_xticks([0.7, 0.8, 0.9, 1.0])
ax2.set_xlim(4.12, 4.26)
ax2.set_xticks([4.2])
ax1.set_ylim(99.3, 100.15)
ax1.set_yticks([99.4, 99.6, 99.8, 100.0])

# Broken-axis diagonal marks on both spines.
d = 0.012
kwargs = dict(transform=ax1.transAxes, color="black", clip_on=False, linewidth=0.8)
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
kwargs.update(transform=ax2.transAxes)
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)

ax1.set_xlabel("LLM calls per turn (simulated)", labelpad=1.5)
ax1.set_ylabel("Revision success (%)", labelpad=1.5)

# Selective direct labels (3 of 9 points): the outlier pair and the expert.
ax2.annotate("always-global\n(2 systems, 4.19 calls)", (4.187, 100.0),
             xytext=(4.187, 99.45), ha="center", fontsize=6.5,
             arrowprops=dict(arrowstyle="-", color="#555555", lw=0.6,
                             shrinkA=3, shrinkB=7))
ax1.annotate("expert", (0.713, 100.0), xytext=(0.695, 100.07),
             fontsize=6.5, color="black")

handles, labels = ax1.get_legend_handles_labels()
order = [list(FAMILY).index(k) for k in
         ["oracle", "bc_aug_dagger3", "bc_dagger3", "bc_aug", "bc",
          "static_cost_aware", "static_rules", "always_global_det",
          "always_global"]]
fig.legend([handles[i] for i in order], [labels[i] for i in order],
           loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=2,
           frameon=False, fontsize=6.3, handletextpad=0.3, columnspacing=1.0,
           labelspacing=0.32, borderaxespad=0.0, markerscale=0.8,
           title="system (% of unaffected slots preserved)",
           title_fontsize=6.3, alignment="left")

fig.subplots_adjust(left=0.115, right=0.985, top=0.97, bottom=0.34)
fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0.02)
print("wrote", OUT)
for x, y, pres, label, *_ in rows.values():
    print(f"  {label:30s} x={x:.3f} y={y:.2f} pres={pres:.1f}")
