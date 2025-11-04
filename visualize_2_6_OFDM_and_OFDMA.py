#!/usr/bin/env python3
"""
LTE OFDMA / SC-FDMA "arched lobe" 3D visual (like textbook figures)

- Each subcarrier+symbol is a smooth lobe in (frequency, time, amplitude)
- Colors indicate user allocation
- CP shown as empty gap between symbols
- Toggle between OFDMA (interleaved users) and SC-FDMA (contiguous blocks)

Output: lte_lobes_like_figure.html
Dependencies: numpy, plotly
"""

import numpy as np
import plotly.graph_objs as go

# --------------------
# Tunables
# --------------------
N_SC = 12  # number of visible subcarriers
N_SYM = 6  # number of OFDM symbols to show
N_USERS = 4
SEED = 7

subcarrier_spacing_kHz = 15.0
sigma_f = 0.38  # lobe width in subcarrier units (0.3..0.5 looks nice)
cp_ratio = 0.12  # CP fraction of a symbol (visual gap on time axis)
amp_jitter = 0.15  # small random per-lobe amplitude variation

grid_f_pts = 35  # resolution of each lobe along freq
grid_t_pts = 25  # resolution of each lobe along time

np.random.seed(SEED)

# Simple palette
PALETTE = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#a65628",
    "#f781bf",
    "#999999",
]


def user_color(uid: int) -> str:
    return PALETTE[uid % len(PALETTE)]


# Raised-cosine time window (smooth “arch” in time)
def time_envelope(t, t0, t1, roll=0.15):
    """Smooth window 0..1 on [t0,t1] with raised-cosine edges"""
    L = t1 - t0
    a = roll * L
    w = np.zeros_like(t, dtype=float)
    # flat part
    mid = (t >= (t0 + a)) & (t <= (t1 - a))
    w[mid] = 1.0
    # rise
    r = (t >= t0) & (t < t0 + a)
    if np.any(r):
        tau = (t[r] - t0) / a
        w[r] = 0.5 - 0.5 * np.cos(np.pi * tau)
    # fall
    f = (t > t1 - a) & (t <= t1)
    if np.any(f):
        tau = (t1 - t[f]) / a
        w[f] = 0.5 - 0.5 * np.cos(np.pi * tau)
    return w


def lobe_surface(
    kc,
    tc,
    amp=1.0,
    color="#888888",
    sigma_f=0.35,
    t_len=1.0,
    cp_ratio=0.1,
    grid_f_pts=31,
    grid_t_pts=21,
):
    """
    Build one smooth lobe centered at subcarrier kc during symbol starting at tc.
    Returns a plotly Surface trace.
    """
    # Frequency grid around [kc-1.2, kc+1.2] in subcarrier-index units
    fmin, fmax = kc - 1.2, kc + 1.2
    ff = np.linspace(fmin, fmax, grid_f_pts)

    # Time grid only during useful symbol (CP shown as preceding gap)
    t0 = tc + cp_ratio
    t1 = tc + 1.0
    tt = np.linspace(t0, t1, grid_t_pts)

    # Make 2D mesh
    F, T = np.meshgrid(ff, tt)

    # Frequency “arch” (Gaussian-like)
    Gf = np.exp(-0.5 * ((F - kc) / sigma_f) ** 2)

    # Time envelope (raised cosine edges)
    Gt = time_envelope(T, t0, t1, roll=0.2)

    Z = amp * Gf * Gt

    surf = go.Surface(
        x=F,
        y=T,
        z=Z,
        showscale=False,
        surfacecolor=None,
        opacity=1.0,
        colorscale=[[0, color], [1, color]],  # constant color per lobe
        hovertemplate=f"SC={kc}<br>Sym={tc}<extra></extra>",
    )
    return surf


def make_allocations(mode="OFDMA"):
    """
    Return allocation map [N_SYM, N_SC] with user IDs or -1 for unallocated.
    OFDMA: interleaved stripes that hop across time
    SC-FDMA: each user gets a contiguous block in frequency for a whole symbol
    """
    alloc = -1 * np.ones((N_SYM, N_SC), dtype=int)

    if mode == "OFDMA":
        stripes = np.array_split(np.arange(N_SC), N_USERS)
        for t in range(N_SYM):
            for u, scs in enumerate(stripes):
                # small hop to suggest scheduler movement
                shift = (2 * t + 3 * u) % N_SC
                ids = (scs + shift) % N_SC
                alloc[t, ids] = u
    else:  # SC-FDMA contiguous blocks per symbol
        block = N_SC // N_USERS
        for t in range(N_SYM):
            for u in range(N_USERS):
                start = (u * block + 2 * t) % N_SC  # slow slide across time
                ids = np.arange(start, start + block) % N_SC
                alloc[t, ids] = u
    return alloc


def build_scene(mode="OFDMA"):
    """
    Build list of lobe surfaces for the selected mode.
    """
    traces = []
    alloc = make_allocations(mode)
    for t in range(N_SYM):
        for k in range(N_SC):
            uid = alloc[t, k]
            if uid < 0:  # skip unallocated
                continue
            amp = 1.0 + amp_jitter * (np.random.rand() - 0.5)
            color = user_color(uid)
            tr = lobe_surface(
                kc=k,
                tc=t,
                amp=amp,
                color=color,
                sigma_f=sigma_f,
                t_len=1.0,
                cp_ratio=cp_ratio,
                grid_f_pts=grid_f_pts,
                grid_t_pts=grid_t_pts,
            )
            traces.append(tr)
    return traces


# --------------------
# Figure
# --------------------
fig = go.Figure()

# Two modes (left=OFDMA, right=SC-FDMA) via visibility toggles
traces_ofdma = build_scene("OFDMA")
for tr in traces_ofdma:
    tr.visible = True
    fig.add_trace(tr)

traces_scfdma = build_scene("SCFDMA")
for tr in traces_scfdma:
    tr.visible = False
    fig.add_trace(tr)

# CP “brackets” (transparent plates to hint where CP sits)
# Draw faint translucent planes at each symbol start
x_min, x_max = -0.8, N_SC - 1 + 0.8
for s in range(N_SYM):
    y_cp = s + cp_ratio
    cp_plate = go.Surface(
        x=[[x_min, x_max], [x_min, x_max]],
        y=[[y_cp, y_cp], [y_cp, y_cp]],
        z=[[0, 0], [1.15, 1.15]],
        showscale=False,
        opacity=0.10,
    )
    fig.add_trace(cp_plate)

# Axes in “textbook” orientation
TITLE = "OFDMA vs SC-FDMA (arched lobes per subcarrier & symbol)"
SUB = "Smooth lobes per subcarrier and symbol; empty gap before each symbol is the CP."

fig.update_layout(
    title=dict(
        text=TITLE, x=0.5, xanchor="center", y=0.98, yanchor="top", font=dict(size=22)
    ),
    margin=dict(l=0, r=0, t=110, b=0),  # extra top margin for centered subtitle
    scene=dict(
        xaxis_title="Frequency (subcarriers, 15 kHz spacing)",
        yaxis_title="Time (symbols with CP gaps)",
        zaxis_title="Amplitude",
        aspectratio=dict(x=1.6, y=1.0, z=0.6),
        camera=dict(eye=dict(x=1.6, y=1.4, z=0.9)),
        xaxis=dict(gridcolor="lightgray"),
        yaxis=dict(gridcolor="lightgray"),
        zaxis=dict(gridcolor="lightgray"),
    ),
    updatemenus=[  # keep your bottom-left buttons so they don't cover text
        dict(
            type="buttons",
            x=0.01,
            y=0.03,
            xanchor="left",
            yanchor="bottom",
            direction="right",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
            pad={"l": 6, "r": 6, "t": 4, "b": 4},
            buttons=[
                dict(
                    label="OFDMA (downlink)",
                    method="update",
                    args=[
                        {
                            "visible": [True] * len(traces_ofdma)
                            + [False] * len(traces_scfdma)
                            + [True] * N_SYM
                        }
                    ],
                ),
                dict(
                    label="SC-FDMA (uplink-style contiguous)",
                    method="update",
                    args=[
                        {
                            "visible": [False] * len(traces_ofdma)
                            + [True] * len(traces_scfdma)
                            + [True] * N_SYM
                        }
                    ],
                ),
            ],
        )
    ],
    annotations=[
        dict(
            text=SUB,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.93,
            xanchor="center",
            yanchor="top",
            align="center",
            showarrow=False,
            font=dict(size=14, color="rgba(40,40,60,0.95)"),
        )
    ],
)
out = "lte_lobes_like_figure.html"
fig.write_html(out, include_plotlyjs="cdn", auto_open=False)
print(f"Saved: {out}")
