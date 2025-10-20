# **🧠 IAF-PSC-EXP Single Neuron on FPGA (PYNQ-Z1)**

This folder contains the complete implementation of the Current-Based Leaky Integrate-and-Fire Neuron with Exponential Synaptic Currents (IAF-PSC-EXP), designed for real-time simulation on an FPGA.

This work serves as the foundational, validated block for larger brain-constrained network simulations.

## **📁 Directory Structure**

* **fpga/**: Contains all hardware-related files, including the **Vitis HLS C++ source**, Vivado project files, Tcl build scripts, and the final **.bit** and **.hwh** files required for deployment to the PYNQ-Z1.  
* **python/**: Contains the software stack used for controlling the FPGA, running the gold-standard $\\text{NEST}$ simulation, and performing result validation and plotting.

## **✅ Validation and Analysis**

The implementation's fidelity was validated by comparing the FPGA's time-series output against the same model parameters run in the $\\text{NEST}$ simulator (the gold standard).

### **Comparison Plot: FPGA vs. NEST**

The plot below shows the time-series comparison (Membrane Potential $V$ and Spike Raster $S$) between the FPGA (Orange) and $\\text{NEST}$ (Blue).

### **Understanding the Spike Time Shift**

As shown in the raster plot, the FPGA's spikes occur approximately $\\mathbf{0.1\\text{ ms}}$ ($\\text{1 time-step}$) later than the $\\text{NEST}$ spikes. This difference is expected and is due to the inherent difference in integration methods:

1. $\\text{NEST}$ **(Standard):** Uses the **Midpoint or Implicit Euler** method, which tends to predict a spike **within** the current time-step ($\\text{t}$ to $\\text{t} \+ \\Delta\\text{t}$).  
2. **FPGA (iaf\_psc\_exp\_hls.cpp):** Uses the **Explicit Euler (Forward Euler)** method, where the spike check is performed **after** the voltage is updated to time $\\mathbf{t} \+ \\Delta\\mathbf{t}$. The voltage must exceed the threshold at the end of the step before a spike is registered, naturally introducing a one-step delay.

By applying a simple time shift of $\\mathbf{0.1\\text{ ms}}$ in the $\\text{Python}$ plotting script, the spike times are perfectly aligned, confirming the correct behavior of the hardware model.

*tata

_tata

\tata
