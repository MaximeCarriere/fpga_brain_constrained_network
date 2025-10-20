#include "iaf_psc_exp_hls.h"
#include <hls_math.h>

// Small helpers to keep HLS timing simple
static inline float safe_exp_decay(float x, float dt, float tau) {
  // exp(-dt/tau) with guards
  if (tau <= 0.f) return 0.f;
  float a = -dt / tau;
  return x * hls::expf(a);
}

extern "C" {
void iaf_psc_exp_hls(
    float  V_in,
    float  psc_ex_in,
    float  psc_in_in,
    float  t_ref_left_in,
    float  I_e,
    float  dt,
    float  E_L,
    float  V_th,
    float  V_reset,
    float  tau_m,
    float  tau_ex,
    float  tau_in,
    float  C_m,
    float  t_ref_ms,
    float *V_out,
    float *psc_ex_out,
    float *psc_in_out,
    float *t_ref_left_out,
    uint32_t *spike_out
) {
#pragma HLS INTERFACE s_axilite port=return       bundle=control
#pragma HLS INTERFACE s_axilite port=V_in         bundle=control
#pragma HLS INTERFACE s_axilite port=psc_ex_in    bundle=control
#pragma HLS INTERFACE s_axilite port=psc_in_in    bundle=control
#pragma HLS INTERFACE s_axilite port=t_ref_left_in bundle=control
#pragma HLS INTERFACE s_axilite port=I_e          bundle=control
#pragma HLS INTERFACE s_axilite port=dt           bundle=control
#pragma HLS INTERFACE s_axilite port=E_L          bundle=control
#pragma HLS INTERFACE s_axilite port=V_th         bundle=control
#pragma HLS INTERFACE s_axilite port=V_reset      bundle=control
#pragma HLS INTERFACE s_axilite port=tau_m        bundle=control
#pragma HLS INTERFACE s_axilite port=tau_ex       bundle=control
#pragma HLS INTERFACE s_axilite port=tau_in       bundle=control
#pragma HLS INTERFACE s_axilite port=C_m          bundle=control
#pragma HLS INTERFACE s_axilite port=t_ref_ms     bundle=control
#pragma HLS INTERFACE s_axilite port=V_out        bundle=control
#pragma HLS INTERFACE s_axilite port=psc_ex_out   bundle=control
#pragma HLS INTERFACE s_axilite port=psc_in_out   bundle=control
#pragma HLS INTERFACE s_axilite port=t_ref_left_out bundle=control
#pragma HLS INTERFACE s_axilite port=spike_out    bundle=control

  // Defaults
  float V    = V_in;
  float pex  = psc_ex_in;
  float pin  = psc_in_in;
  float tref = t_ref_left_in;
  uint32_t spk = 0;

  // Decay PSCs every step (even during refractory)
  pex = safe_exp_decay(pex, dt, tau_ex);
  pin = safe_exp_decay(pin, dt, tau_in);

  if (tref > 0.f) {
    // Absolute refractory: hold V at reset, count down refractory timer
    V    = V_reset;
    tref = tref - dt;
    if (tref < 0.f) tref = 0.f;
    spk  = 0;
  } else {
    // Current-based membrane ODE:
    //   C_m dV/dt = -(V - E_L)/R_m + I_syn + I_e
    // with R_m = tau_m / C_m  =>  dV/dt = (E_L - V)/tau_m + (I_syn + I_e)/C_m
    const float Rm = tau_m / C_m;
    (void)Rm; // kept for clarity above

    const float I_syn = pex - pin; // inhibitory enters with minus sign in current-based model
    const float dV = ((E_L - V) / tau_m) + ((I_syn + I_e) / C_m);
    V = V + dt * dV;

    // Threshold & reset at end-of-step
    if (V >= V_th) {
      spk  = 1u;
      V    = V_reset;
      tref = t_ref_ms;  // start refractory
    } else {
      spk  = 0u;
    }
  }

  // Write back
  *V_out          = V;
  *psc_ex_out     = pex;
  *psc_in_out     = pin;
  *t_ref_left_out = tref;
  *spike_out      = spk;
}
}
