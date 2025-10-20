#pragma once
#include <ap_int.h>
#include <stdint.h>

// One-step IAF-PSC-EXP kernel (current-based).
// All ports are mapped to AXI-Lite "control" so the PS can set/read them.
// We keep the top name 'iaf_psc_exp_hls' so your Vivado BD/IP stays compatible.

extern "C" {
void iaf_psc_exp_hls(
    // --- State IN at time t ---
    float  V_in,             // membrane potential [mV]
    float  psc_ex_in,        // excitatory PSC state (current) [pA] (decays with tau_ex)
    float  psc_in_in,        // inhibitory  PSC state (current) [pA] (decays with tau_in)
    float  t_ref_left_in,    // remaining refractory time [ms]

    // --- Stimulation at time t ---
    float  I_e,              // external injected current [pA]
    float  dt,               // time step [ms]

    // --- Parameters (constant over sim unless you change them) ---
    float  E_L,              // leak reversal [mV]
    float  V_th,             // threshold [mV]
    float  V_reset,          // reset potential [mV]
    float  tau_m,            // membrane time constant [ms]
    float  tau_ex,           // excitatory PSC time constant [ms]
    float  tau_in,           // inhibitory PSC time constant [ms]
    float  C_m,              // membrane capacitance [pF]
    float  t_ref_ms,         // absolute refractory time [ms]

    // --- State OUT at time t+dt ---
    float *V_out,
    float *psc_ex_out,
    float *psc_in_out,
    float *t_ref_left_out,
    uint32_t *spike_out      // 1 if spike at end of step, else 0
);
}
