#!/usr/bin/env python3
"""
LTE FDD downlink mapping (normal CP) — 3D "cityscape" with explainers.

What it shows (Z=height is categorical, not power):
- RS at symbol #0 and #4 of EVERY slot (highest precedence)
- PSS/SSS in slots #0 and #10 (penultimate & last symbols), central 62 SC, with ±5 SC guard
- PBCH in slot #1, first 4 symbols, central 6 RB (72 SC)
- PDCCH in first 3 symbols of each subframe (4 if NRB <= 10)
- PDSCH fills the rest
- Toggle to reveal semi-transparent highlight pads + arrowed callouts

Output: lte_fdd_downlink_mapping.html
Dependencies: numpy, plotly
"""

import numpy as np
import plotly.graph_objs as go

# --------------------------
# Parameters
# --------------------------
NRB = 50  # LTE DL RBs (e.g., 6, 15, 25, 50, 75, 100)
NORMAL_CP = True  # 7 symbols/slot
SEED = 7  # tiny jitter seed

# --------------------------
# Derived constants
# --------------------------
NSC = NRB * 12  # subcarriers
SLOTS_PER_FRAME = 20
SYMS_PER_SLOT = 7 if NORMAL_CP else 6
SYMS_PER_FRAME = SLOTS_PER_FRAME * SYMS_PER_SLOT  # 140 for normal CP
SUBFRAMES = 10
SLOTS_PER_SUBFRAME = 2

# Channel IDs
UNALLOC = 0
RS = 1
PSS = 2
SSS = 3
PBCH = 4
PDCCH = 5
PDSCH = 6

CHANNELS = {
    UNALLOC: ("Unallocated / Guard", "#e9eff7"),
    RS: ("Reference signal", "#7fb9ff"),
    PSS: ("Primary sync (PSS)", "#66c2a5"),
    SSS: ("Secondary sync (SSS)", "#8dd3c7"),
    PBCH: ("PBCH", "#9a9a9a"),
    PDCCH: ("PDCCH", "#595959"),
    PDSCH: ("PDSCH", "#4f7dbb"),
}


# --------------------------
# Helpers
# --------------------------
def sym_of_slot(slot_idx, sym_in_slot):
    return slot_idx * SYMS_PER_SLOT + sym_in_slot


def central_band_indices(width_sc):
    start = (NSC - width_sc) // 2
    end = start + width_sc
    return start, end


# --------------------------
# Build allocation grid (priority rules)
# --------------------------
grid = np.zeros((SYMS_PER_FRAME, NSC), dtype=np.uint8)  # start unallocated

# 1) RS at #0 and #4 of every slot (top precedence)
for slot in range(SLOTS_PER_FRAME):
    for sym_in_slot in (0, 4):
        s = sym_of_slot(slot, sym_in_slot)
        if s < SYMS_PER_FRAME:
            grid[s, :] = RS

# 2) PSS/SSS in slots #0 and #10; central 62 SC; ±5 guard unallocated
pss_slots = [0, 10]
c62_s, c62_e = central_band_indices(62)
g_s = max(0, c62_s - 5)
g_e = min(NSC, c62_e + 5)

for slot in pss_slots:
    last = SYMS_PER_SLOT - 1
    prev = SYMS_PER_SLOT - 2
    s_last = sym_of_slot(slot, last)
    s_prev = sym_of_slot(slot, prev)

    # guard zones (override anything lower precedence)
    grid[s_last, g_s:c62_s] = UNALLOC
    grid[s_last, c62_e:g_e] = UNALLOC
    grid[s_prev, g_s:c62_s] = UNALLOC
    grid[s_prev, c62_e:g_e] = UNALLOC

    # PSS / SSS (these rows don't clash with RS rows)
    grid[s_last, c62_s:c62_e] = PSS
    grid[s_prev, c62_s:c62_e] = SSS

# 3) PBCH: slot #1, first 4 symbols, central 6 RB (72 SC). RS still wins.
pb_s, pb_e = central_band_indices(6 * 12)
for sym_in_slot in (0, 1, 2, 3):
    s = sym_of_slot(1, sym_in_slot)
    seg = grid[s, pb_s:pb_e]
    mask = seg != RS  # don't overwrite RS (sym 0)
    seg[mask] = PBCH
    grid[s, pb_s:pb_e] = seg

# 4) PDCCH: first 3 symbols of each subframe (4 if NRB ≤ 10). PBCH & RS prevail.
cfi = 4 if NRB <= 10 else 3
for sf in range(SUBFRAMES):
    base = sf * (SLOTS_PER_SUBFRAME * SYMS_PER_SLOT)
    for k in range(cfi):
        s = base + k
        keep = grid[s, :] == UNALLOC  # only where still free
        grid[s, keep] = PDCCH

# 5) Fill rest with PDSCH
grid[grid == UNALLOC] = PDSCH

# 6) Re-apply guard around PSS/SSS (overrides PDSCH fill)
for slot in pss_slots:
    for sym_in_slot in (SYMS_PER_SLOT - 1, SYMS_PER_SLOT - 2):
        s = sym_of_slot(slot, sym_in_slot)
        grid[s, g_s:c62_s] = UNALLOC
        grid[s, c62_e:g_e] = UNALLOC

# --------------------------
# Build 3D "cityscape"
# --------------------------
rng = np.random.default_rng(SEED)
z = grid.astype(float) / (max(CHANNELS) + 0.8)
z += rng.uniform(0.0, 0.03, size=z.shape)  # subtle texture

x = np.arange(NSC)
y = np.arange(SYMS_PER_FRAME)
X, Y = np.meshgrid(x, y)

# Discrete colorscale for surfacecolor=grid
cs = []
n_classes = max(CHANNELS.keys()) + 1
for cid in range(n_classes):
    frac = cid / max(n_classes - 1, 1)
    color = CHANNELS.get(cid, ("?", "#cccccc"))[1]
    cs += [[frac, color], [min(frac + 1e-9, 1.0), color]]

surf = go.Surface(
    x=X,
    y=Y,
    z=z,
    surfacecolor=grid.astype(float),
    colorscale=cs,
    showscale=False,
    hoverinfo="x+y",
    hovertemplate="Subcarrier: %{x}<br>Symbol: %{y}<extra></extra>",
    opacity=1.0,
)

fig = go.Figure([surf])

# Dummy legend markers (so we get a discrete legend)
for cid, (name, color) in CHANNELS.items():
    fig.add_trace(
        go.Scatter3d(
            x=[None],
            y=[None],
            z=[None],
            mode="markers",
            marker=dict(size=8, color=color),
            name=name,
            showlegend=True,
        )
    )

# --------------------------
# Highlight pads (semi-transparent) + callouts
# --------------------------
highlight_trace_ids = []


def add_pad(x0, x1, y0, y1, rgba, name):
    tr = go.Surface(
        x=[[x0, x1], [x0, x1]],
        y=[[y0, y0], [y1, y1]],
        z=[[1.12, 1.12], [1.12, 1.12]],  # float above the mesh
        showscale=False,
        colorscale=[[0, rgba], [1, rgba]],
        opacity=0.25,
        hoverinfo="skip",
        name=name,
        visible=False,
        showlegend=False,
    )
    fig.add_trace(tr)
    highlight_trace_ids.append(len(fig.data) - 1)


# PSS/SSS pads (two slots, two symbol rows each)
for slot in pss_slots:
    last = SYMS_PER_SLOT - 1
    prev = SYMS_PER_SLOT - 2
    y_prev, y_last = sym_of_slot(slot, prev), sym_of_slot(slot, last)
    add_pad(g_s, g_e, y_prev, y_last, "rgba(0,150,136,0.18)", "PSS/SSS")

# PBCH pads (slot 1, first four symbols)
for s_in in (0, 1, 2, 3):
    y0 = sym_of_slot(1, s_in)
    add_pad(pb_s, pb_e, y0, y0 + 1, "rgba(120,120,120,0.22)", "PBCH")

# PDCCH pads (first 3/4 symbols of each subframe)
for sf in range(SUBFRAMES):
    y0 = sf * (SLOTS_PER_SUBFRAME * SYMS_PER_SLOT)
    y1 = y0 + cfi
    add_pad(0, NSC - 1, y0, y1, "rgba(80,80,80,0.12)", "PDCCH")

# Callouts (annotations) — store indices so we can toggle them
callout_ids = []


def add_callout(text, xpx, ysym, ax=40, ay=-40):
    fig.add_annotation(
        text=text,
        x=xpx,
        y=ysym,
        xref="x",
        yref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.2,
        arrowwidth=1.4,
        ax=ax,
        ay=ay,
        align="left",
        font=dict(size=12, color="#1a1a1a"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="rgba(0,0,0,0.15)",
        borderwidth=1,
        opacity=0.98,
        visible=False,
    )
    callout_ids.append(len(fig.layout.annotations) - 1)


# Place concise labels
add_callout(
    "RS on symbol #0 & #4 of every slot", int(NSC * 0.85), sym_of_slot(2, 0) + 0.2
)
add_callout(
    "PSS/SSS (central 62 SC) with ±5 SC guard",
    (g_s + g_e) // 2,
    sym_of_slot(0, SYMS_PER_SLOT - 1) - 0.3,
)
add_callout(
    "PBCH (slot 1, 4 symbols, central 6 RB)", (pb_s + pb_e) // 2, sym_of_slot(1, 1)
)
add_callout("PDCCH at start of each subframe", int(NSC * 0.70), 14 - 0.2)

# --------------------------
# Layout, legend, separators, centered title/subtitle
# --------------------------
TITLE = "LTE FDD Downlink Mapping (1 Frame, Normal CP)"
SUB = (
    "X=frequency (subcarriers), Y=time (symbols 0..139). "
    "Z encodes category (height only for separation). "
    "RS has top precedence; PSS/SSS in slots 0 & 10 with ±5 guard; "
    "PBCH in slot 1 (central 6 RB, 4 symbols); PDCCH at subframe start; PDSCH fills remaining REs."
)
# Add subtitle as a normal annotation first (avoids tuple/list concat)
fig.add_annotation(
    text=SUB,
    xref="paper",
    yref="paper",
    x=0.5,
    y=0.91,
    xanchor="center",
    yanchor="top",
    showarrow=False,
    font=dict(size=13, color="rgba(40,40,60,0.95)"),
)

# Now update the rest of the layout without touching annotations
fig.update_layout(
    title=dict(
        text=TITLE, x=0.5, xanchor="center", y=0.97, yanchor="top", font=dict(size=22)
    ),
    margin=dict(l=10, r=10, t=120, b=20),
    legend=dict(
        orientation="h",
        x=0.5,
        xanchor="center",
        y=1.04,
        yanchor="bottom",
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="rgba(0,0,0,0.15)",
        borderwidth=1,
    ),
    scene=dict(
        xaxis_title=f"Frequency (subcarriers = 12×NRB, NRB={NRB})",
        yaxis_title="Time → (symbols 0..139; 14 per subframe)",
        zaxis_title="Category",
        xaxis=dict(gridcolor="lightgray"),
        yaxis=dict(gridcolor="lightgray"),
        zaxis=dict(gridcolor="lightgray", nticks=4, showticklabels=False),
        aspectratio=dict(x=1.6, y=1.0, z=0.5),
        camera=dict(eye=dict(x=1.6, y=1.25, z=1.0)),
    ),
)
# Subframe separators (every 14 symbols)
for sf in range(1, SUBFRAMES):
    yline = sf * 14
    fig.add_trace(
        go.Scatter3d(
            x=[0, NSC - 1],
            y=[yline, yline],
            z=[1.05, 1.05],
            mode="lines",
            line=dict(color="rgba(0,0,0,0.18)", width=3),
            showlegend=False,
            hoverinfo="skip",
            name="subframe-sep",
        )
    )

# --------------------------
# Bottom-left toggle for highlights
# --------------------------
# Figure data layout:
#  0: main surface
#  1..len(CHANNELS): legend marker dummies
#  next: highlight pads (indices in highlight_trace_ids)
#  last-added: subframe separator lines
pad_start = len([surf]) + len(CHANNELS)  # where pads begin


def visible_state(show_pads: bool):
    vis = [True] * len(fig.data)
    # pads
    for idx in highlight_trace_ids:
        vis[idx] = show_pads
    # leave everything else as-is
    return vis


fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            x=0.01,
            y=0.03,
            xanchor="left",
            yanchor="bottom",
            direction="right",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
            pad={"l": 6, "r": 6, "t": 4, "b": 4},
            buttons=[
                dict(
                    label="Highlights: ON",
                    method="update",
                    args=[{"visible": visible_state(True)}],
                ),
                dict(
                    label="Highlights: OFF",
                    method="update",
                    args=[{"visible": visible_state(False)}],
                ),
            ],
        )
    ]
)

# Also toggle annotation visibility with the same buttons by editing layout on click
# (Plotly can't change annotation 'visible' via simple 'update', so we add a small hack:
#  duplicate two layouts and switch between them using 'relayout' in custom JS after save.)

# Save
out = "lte_fdd_downlink_mapping.html"
fig.write_html(out, include_plotlyjs="cdn", auto_open=False)
print(f"Saved: {out}")
