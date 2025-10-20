#!/usr/bin/env python3
import nest
import numpy as np
import csv
import time
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- FPGA-MATCHED PARAMETERS ----------------
NSTEPS = 2000        # samples (K)
DT     = 0.1         # ms per sample (NEST resolution)
T_total = NSTEPS * DT # ms total simulation time

# LIF params
V_INIT  = -65.0
E_L     = -65.0
V_TH    = -50.0
V_RESET = -65.0
TAU_M   = 10.0
C_M     = 250.0   # pF
T_REF   = 2.0     # ms
I_E     = 0.0   # pA baseline

# Pulses on i0 (DC pulses in NEST)
PULSE_AMP  = 1000.0   # pA
PULSES_MS  = [(0.0, 5.0), (35.0, 40.0)]

OUT_CSV = Path("nest_single_neuron.csv")
# ---------------------------------------------------------

# =========================================================
# NEST SIMULATION
# =========================================================
def run_nest_simulation():
    print("Setting up NEST simulation...")

    # -------- NEST setup --------
    nest.ResetKernel()
    nest.SetKernelStatus({"resolution": DT, "local_num_threads": 1})

    cell_params = dict(
        V_m = V_INIT,
        E_L = E_L,
        V_th = V_TH,
        V_reset = V_RESET,
        tau_m = TAU_M,
        C_m = C_M,
        t_ref = T_REF,
        I_e = I_E # Static baseline current
    )

    # 1. Create the single neuron
    neuron = nest.Create("iaf_psc_exp", 1, params=cell_params)
    gid0 = neuron[0].get("global_id")

    # 2. Add Current Pulses using multiple dc_generators
    dc_generators = []
    for start, stop in PULSES_MS:
        dc = nest.Create("dc_generator", params={
            "amplitude": PULSE_AMP,
            "start": start,
            "stop": stop
        })
        # Connect pulse to the neuron
        nest.Connect(dc, neuron)
        dc_generators.append(dc)

    # 3. Create Multimeter (Voltage) and Spike Recorder
    # FIX: Removed the invalid "withtime": True parameter.
    mm = nest.Create("multimeter", params={"record_from": ["V_m"], "interval": DT})
    sr = nest.Create("spike_recorder")
    nest.Connect(mm, neuron)
    nest.Connect(neuron, sr)

    # -------- Run --------
    print(f"Simulating for T_total = {T_total:.1f} ms...")
    t_start = time.time()
    nest.Simulate(T_total)
    t_end = time.time()
    print(f"Simulation done in {t_end - t_start:.3f} seconds.")

    # -------- Extract traces --------
    m_events = nest.GetStatus(mm)[0]["events"]
    # The 'multimeter' uses 'times' when 'withtime' is false or absent
    times = m_events["times"]
    V_all = m_events["V_m"]

    t = times
    V0 = V_all
    L = len(t)
    dt_grid = t[1] - t[0] if L > 1 else DT

    # Calculate Injected Current I0 (I_e + Pulses)
    I0 = np.full_like(t, I_E) # Start with baseline I_E
    for start, stop in PULSES_MS:
        I0[((t >= start) & (t < stop))] += PULSE_AMP

    # Spikes → bin to grid
    sr_events = nest.GetStatus(sr, "events")[0]
    spikes_t = sr_events["times"]
    edges = np.concatenate(([t[0] - 0.5*dt_grid], t + 0.5*dt_grid))
    S0 = (np.histogram(spikes_t, bins=edges)[0] > 0).astype(int)

    # -------- Save CSV --------
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_ms", "V_mV", "spike", "I0_pA"])
        for k in range(L):
            w.writerow([float(t[k]),
                        float(V0[k]),
                        int(S0[k]),
                        float(I0[k])])
    print(f"Saved {OUT_CSV} (samples: {L}, dt={dt_grid:.3f} ms)")
    return OUT_CSV

# =========================================================
# PLOTTING FUNCTIONS
# =========================================================
def load_csv(path: Path):
    with path.open() as f:
        r = csv.DictReader(f)
        cols = {k: [] for k in r.fieldnames}
        for row in r:
            for k,v in row.items():
                cols[k].append(v)
    out = {}
    for k, lst in cols.items():
        try:
            out[k] = np.array([float(x) for x in lst], dtype=float)
        except Exception:
            out[k] = np.array(lst)
    return out

def plot_single_neuron(csv_path):
    D = load_csv(csv_path)
    
    t = D["t_ms"]
    V0 = D["V_mV"]
    I0 = D["I0_pA"]
    S0 = D["spike"]

    dt = float(np.mean(np.diff(t))) if len(t)>1 else 1.0
    T  = (t[-1]-t[0]+dt) if len(t) else 0.0
    sec = max(T/1000.0, 1e-9)
    spk0 = int(np.nansum(S0))
    fr0 = spk0/sec

    # Stim windows guessed from I0 > I_E (pulses)
    stim_mask = (I0 > I_E)
    starts = ends = []
    if np.any(stim_mask):
        on = np.where(stim_mask)[0]
        edges = np.where(np.diff(on)>1)[0]
        starts = [on[0]] + [on[e+1] for e in edges]
        ends   = [on[e]  for e in edges] + [on[-1]]

    # ----- Plot setup -----
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.35)
    palette = sns.color_palette("colorblind", 2)
    lw = 2.6; marker_size=5.0; markevery=5

    fig, axes = plt.subplots(3, 1, figsize=(11.2, 8.5),
                             sharex=True, gridspec_kw={"height_ratios":[2.4, 1.5, 1.8]})

    # (A) V
    axV = axes[0]
    axV.plot(t, V0, label="Neuron 0", color=palette[0], linestyle="-",
             linewidth=lw, marker="o", markevery=markevery, ms=marker_size)
    axV.hlines(V_TH, t[0], t[-1], color="red", linestyle=":", label="V_th", zorder=0)
    for s,e in zip(starts, ends):
        axV.axvspan(t[s], t[e], color="0.90", zorder=0)
    axV.set_ylabel("V (mV)")
    axV.set_title("Membrane Potential")
    axV.legend(frameon=True, loc="best")

    # (B) I
    axI = axes[1]
    axI.plot(t, I0, label="I0 (pA)", color=palette[0], linestyle="-",
             linewidth=lw, marker="o", markevery=markevery, ms=marker_size)
    for s,e in zip(starts, ends):
        axI.axvspan(t[s], t[e], color="0.90", zorder=0)
    axI.set_ylabel("I (pA)")
    axI.set_title("Injected Current")
    axI.legend(frameon=True, loc="best")

    # (C) Spike raster
    axS = axes[2]
    t_spk0 = t[S0>0.5]
    for _t in t_spk0:
        axS.vlines(_t, 0.25-0.12, 0.25+0.12, color=palette[0], linewidth=1.4, linestyles="-")
    axS.text(t[0], 0.25, "N0", va="center", ha="left", fontsize=11)
    for s,e in zip(starts, ends):
        axS.axvspan(t[s], t[e], color="0.93", zorder=0)
    axS.set_ylim(0, 1.05)
    axS.set_xlabel("Time (ms)")
    axS.set_ylabel("Spikes")
    axS.set_title("Spike Times (Raster)")

    # Summary box
    txt = (f"T = {T:.1f} ms, dt = {dt:.1f} ms\n"
           f"N0: {spk0} spikes, {fr0:.1f} Hz")
    axV.text(0.99, 0.02, txt, transform=axV.transAxes,
             ha="right", va="bottom", family="monospace",
             bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.75", alpha=0.95))

    # Ticks & cosmetics
    for ax in axes:
        ax.minorticks_on()
        ax.grid(True, which="major", alpha=0.28)
        ax.grid(True, which="minor", alpha=0.12)
    sns.despine(fig)
    fig.suptitle(f"Single-neuron LIF (NEST) Simulation", y=1.03)

    out_png = csv_path.with_name(f"{csv_path.stem}_plot.png")
    fig.savefig(out_png, dpi=400, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    csv_out_path = run_nest_simulation()
    # The plot will show up when the script finishes successfully
    plot_single_neuron(csv_out_path)
