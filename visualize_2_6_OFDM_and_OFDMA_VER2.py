#!/usr/bin/env python3
"""
Small-HTML LTE OFDMA/SC-FDMA arched-lobes plot.

Key idea: we DO NOT embed X/Y/Z arrays. We embed only lobe params and
reconstruct surfaces in the browser. This reduces file size massively.

Output: lte_lobes_like_figure_small.html
Dependencies: none at runtime except Plotly (loaded from CDN)
"""

import json
import random

# --------------------
# Tunables (same feel, lighter payload)
# --------------------
N_SC = 12  # visible subcarriers
N_SYM = 6  # symbols
N_USERS = 4
SEED = 7

SUBCARRIER_SPACING_KHZ = 15.0
SIGMA_F = 0.38  # lobe width (subcarrier units)
CP_RATIO = 0.12  # time CP fraction (visual gap)
AMP_JITTER = 0.15  # small amplitude variation

# ↓ smaller grids keep it smooth enough but tiny
GRID_F_PTS = 25  # 35 looked great; 25 is still nice & smaller
GRID_T_PTS = 17  # 25→17: still smooth top & edges

random.seed(SEED)

# Simple palette (indices referenced in HTML)
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


def make_allocations(mode="OFDMA"):
    """
    Return allocation list of tuples for a mode:
    [(symbol_idx, subcarrier_idx, user_id, amplitude), ...]
    """
    alloc = []
    if mode == "OFDMA":
        # Interleaved stripes that hop slowly
        stripes = []
        scs = list(range(N_SC))
        step = max(1, N_SC // N_USERS)
        for u in range(N_USERS):
            stripes.append(scs[u::N_USERS])
        for t in range(N_SYM):
            for u, sc_list in enumerate(stripes):
                shift = (2 * t + 3 * u) % N_SC
                for k in sc_list:
                    kk = (k + shift) % N_SC
                    amp = 1.0 + AMP_JITTER * (random.random() - 0.5)
                    alloc.append((t, kk, u, round(amp, 3)))
    else:  # SC-FDMA: contiguous blocks per symbol
        block = max(1, N_SC // N_USERS)
        for t in range(N_SYM):
            for u in range(N_USERS):
                start = (u * block + 2 * t) % N_SC  # slow slide
                for i in range(block):
                    kk = (start + i) % N_SC
                    amp = 1.0 + AMP_JITTER * (random.random() - 0.5)
                    alloc.append((t, kk, u, round(amp, 3)))
    return alloc


payload = {
    "title": "OFDMA vs SC-FDMA (arched lobes per subcarrier & symbol)",
    "subtitle": "Smooth lobes per subcarrier and symbol; empty gap before each symbol is the CP.",
    "n_sc": N_SC,
    "n_sym": N_SYM,
    "n_users": N_USERS,
    "sigma_f": SIGMA_F,
    "cp_ratio": CP_RATIO,
    "grid_f_pts": GRID_F_PTS,
    "grid_t_pts": GRID_T_PTS,
    "palette": PALETTE,
    "alloc_ofdma": make_allocations("OFDMA"),
    "alloc_scfdma": make_allocations("SCFDMA"),
}

HTML = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>LTE lobes (small HTML)</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Arial, sans-serif; }}
    #titlebox {{ text-align:center; padding-top:14px; }}
    #titlebox h1 {{ margin:0; font-size:22px; font-weight:700; }}
    #titlebox p  {{ margin:4px 0 8px; font-size:14px; color:#333; }}
    #controls {{ position:fixed; left:12px; bottom:12px; background:rgba(255,255,255,0.9);
                 border:1px solid rgba(0,0,0,.15); border-radius:8px; padding:6px 8px; display:flex; gap:6px; z-index:10; }}
    #controls button {{ border:1px solid #c9c9c9; background:#fff; padding:6px 10px; border-radius:6px; cursor:pointer; }}
    #controls button.active {{ background:#ecf3ff; border-color:#7aa7ff; }}
    #plot {{ width:100vw; height: calc(100vh - 96px); }}
  </style>
</head>
<body>
  <div id="titlebox">
    <h1>{payload["title"]}</h1>
    <p>{payload["subtitle"]}</p>
  </div>
  <div id="controls">
    <button id="btn-ofdma" class="active">OFDMA (downlink)</button>
    <button id="btn-scfdma">SC-FDMA (uplink-style contiguous)</button>
  </div>
  <div id="plot"></div>

  <script>
  const P = {json.dumps(payload, separators=(",", ":"))};

  // Smooth raised-cosine time window
  function timeEnv(t, t0, t1, roll=0.2) {{
    const L = t1 - t0, a = roll*L;
    if (t < t0 || t > t1) return 0;
    if (t < t0 + a) {{
      const tau = (t - t0)/a; return 0.5 - 0.5*Math.cos(Math.PI*tau);
    }}
    if (t > t1 - a) {{
      const tau = (t1 - t)/a; return 0.5 - 0.5*Math.cos(Math.PI*tau);
    }}
    return 1;
  }}

  // Build one lobe Surface (computed client-side)
  function lobeSurface(kc, tc, amp, color) {{
    const fmin = kc - 1.2, fmax = kc + 1.2;
    const t0 = tc + P.cp_ratio, t1 = tc + 1.0;
    const fn = P.grid_f_pts, tn = P.grid_t_pts;

    // Build grids and Z
    let xs = new Array(fn), ys = new Array(tn);
    for (let i=0;i<fn;i++) xs[i] = fmin + (fmax-fmin)*i/(fn-1);
    for (let j=0;j<tn;j++) ys[j] = t0 + (t1-t0)*j/(tn-1);

    // Flat arrays for Surface
    const z = new Array(tn).fill(0).map(_ => new Array(fn).fill(0));
    for (let j=0;j<tn;j++) {{
      const te = timeEnv(ys[j], t0, t1, 0.2);
      for (let i=0;i<fn;i++) {{
        const gf = Math.exp(-0.5 * Math.pow((xs[i]-kc)/P.sigma_f, 2));
        z[j][i] = amp * gf * te;
      }}
    }}
    // Constant-color surface via colorscale endpoints
    return {{
      type: 'surface',
      x: xs, y: ys, z: z,
      showscale: false,
      colorscale: [[0, color],[1, color]],
      opacity: 1.0,
      hoverinfo: 'skip'
    }};
  }}

  function buildMode(mode) {{
    const alloc = (mode === 'OFDMA') ? P.alloc_ofdma : P.alloc_scfdma;
    const traces = [];
    for (const [t, k, u, a] of alloc) {{
      const color = P.palette[u % P.palette.length];
      traces.push(lobeSurface(k, t, a, color));
    }}
    // CP translucent plates
    const xMin = -0.8, xMax = P.n_sc - 1 + 0.8;
    for (let s=0; s<P.n_sym; s++) {{
      const ycp = s + P.cp_ratio;
      traces.push({{
        type:'surface',
        x:[[xMin,xMax],[xMin,xMax]],
        y:[[ycp,ycp],[ycp,ycp]],
        z:[[0,0],[1.15,1.15]],
        showscale:false,
        opacity:0.10,
        hoverinfo:'skip'
      }});
    }}
    return traces;
  }}

  let currentMode = 'OFDMA';
  let traces = buildMode(currentMode);

  const layout = {{
    margin: {{l:0, r:0, t:10, b:0}},
    scene: {{
      xaxis: {{
        title: 'Frequency (subcarriers, 15 kHz spacing)',
        range: [-0.8, P.n_sc-1+0.8],
        gridcolor: 'lightgray'
      }},
      yaxis: {{
        title: 'Time (symbols with CP gaps)',
        range: [-0.1, P.n_sym+0.2],
        gridcolor: 'lightgray'
      }},
      zaxis: {{
        title: 'Amplitude',
        range: [0, 1.2],
        gridcolor: 'lightgray'
      }},
      aspectratio: {{x:1.6, y:1.0, z:0.6}},
      camera: {{eye: {{x:1.6, y:1.4, z:0.9}}}}
    }}
  }};

  Plotly.newPlot('plot', traces, layout, {{responsive:true}});

  // Buttons
  const btnOfdma = document.getElementById('btn-ofdma');
  const btnScf   = document.getElementById('btn-scfdma');
  function setActive(which) {{
    btnOfdma.classList.toggle('active', which==='OFDMA');
    btnScf.classList.toggle('active',   which==='SCFDMA');
  }}
  btnOfdma.onclick = () => {{
    if (currentMode === 'OFDMA') return;
    currentMode = 'OFDMA'; setActive('OFDMA');
    Plotly.react('plot', buildMode('OFDMA'), layout);
  }};
  btnScf.onclick = () => {{
    if (currentMode === 'SCFDMA') return;
    currentMode = 'SCFDMA'; setActive('SCFDMA');
    Plotly.react('plot', buildMode('SCFDMA'), layout);
  }};
  </script>
</body>
</html>
"""

with open("lte_lobes_like_figure_small.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("Saved: lte_lobes_like_figure_small.html")
