# run_step_feedback.py (Final Fix for Spike Output Format)
from pynq import Overlay
import struct, csv, time

def f2u32(x):
    """Converts a float to its 32-bit unsigned integer representation for the FPGA."""
    import struct
    return struct.unpack("<I", struct.pack("<f", float(x)))[0]

def u32f(u):
    """Converts a 32-bit unsigned integer back to a float."""
    import struct
    return struct.unpack("<f", struct.pack("<I", int(u)))[0]

# --- Simulation and Input Parameters ---
BITFILE = "system_i_wrapper.bit"
# ❗️ CHANGE 1: Increase steps to cover 40.0 ms (400 steps @ 0.1 ms/step)
T_STEPS = 2001    # Total number of simulation steps (0 to 400)
DT_MS   = 0.1    # Time step size (ms)
I_BASE  = 0.0    # Base current (pA)
I_PULSE = 1000.0 # Current during pulse (pA)

# --- Neuron Parameters (Matching NEST iaf_psc_exp defaults) ---
E_L=-65.0; V_INIT=-65.0; V_TH=-50.0; V_RESET=-65.0
TAU_M=10.0; TAU_EX=5.0; TAU_IN=10.0; C_M=250.0; T_REF_MS=2.0

# --- PYNQ Setup ---
ol = Overlay(BITFILE)
iaf = ol.iaf_hls_kernel
rm  = iaf.register_map

# --- Set Static Parameters in FPGA Registers ---
rm.dt=f2u32(DT_MS); rm.E_L=f2u32(E_L); rm.V_th=f2u32(V_TH); rm.V_reset=f2u32(V_RESET)
rm.tau_m=f2u32(TAU_M); rm.tau_ex=f2u32(TAU_EX); rm.tau_in=f2u32(TAU_IN)
rm.C_m=f2u32(C_M); rm.t_ref_ms=f2u32(T_REF_MS)

# --- Initialize State Variables ---
V_in=V_INIT; psc_ex_in=0.0; psc_in_in=0.0; tref_left_in=0.0

# --- Main Simulation Loop ---
rows=[]; t0=time.time()
for t in range(T_STEPS):
    # Determine the current I_DRIVE based on the step number
    # Pulse 1: steps 0 to 49 (0.0 ms to 4.9 ms)
    # Pulse 2: steps 350 to 399 (35.0 ms to 39.9 ms)
    if (0 <= t <= 49) or (350 <= t <= 399):
        I_DRIVE = I_PULSE
    else:
        I_DRIVE = I_BASE

    # Write input state and current to the FPGA
    rm.V_in=f2u32(V_in); rm.psc_ex_in=f2u32(psc_ex_in); rm.psc_in_in=f2u32(psc_in_in)
    rm.t_ref_left_in=f2u32(tref_left_in); rm.I_e=f2u32(I_DRIVE)

    # Start the computation and wait for it to finish
    rm.CTRL.AP_START = 1
    while rm.CTRL.AP_DONE == 0:
        pass

    # Read output state and spike from the FPGA
    V_out           = u32f(rm.V_out)
    psc_ex_out      = u32f(rm.psc_ex_out)
    psc_in_out      = u32f(rm.psc_in_out)
    tref_left_out   = u32f(rm.t_ref_left_out)
    
    # 🌟 NEW FIX: Explicitly cast the Register object to a standard Python integer.
    spike_int       = int(rm.spike_out)

    # Prepare for next iteration (Feedback)
    V_in = V_out
    psc_ex_in = psc_ex_out
    psc_in_in = psc_in_out
    tref_left_in = tref_left_out
    
    # Store results
    rows.append((t, I_DRIVE, V_out, spike_int))


# --- Finalization and Output ---
t1 = time.time()
print(f"Ran {T_STEPS} steps in {t1 - t0:.6f} s")

# Write trace to CSV
with open('trace.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['step', 'I', 'V', 'S'])
    writer.writerows(rows)
print("Wrote trace.csv")
