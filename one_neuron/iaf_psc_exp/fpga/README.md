IAF-PSC-EXP Single Neuron FPGA Package
======================================

This folder contains the complete source, configuration, and final binaries used to implement and validate the **Integrate-and-Fire (IAF-PSC-EXP) HLS kernel** on the **PYNQ-Z1** (Zynq-7000 SoC).

The design uses **AXI-Lite** for all register-based parameter loading (e.g., $V\_{th}$, $\\tau\_m$, $I\_{ext}$) and state reading (e.g., $V\_m$, spike).

📂 Folder Overview
------------------

### **bitstream/**

*   `system\_i\_wrapper.bit`: The **final FPGA configuration file**. This is loaded onto the PYNQ-Z1 to configure the FPGA fabric.
    
*   `system\_i\_wrapper.hwh`: The **hardware description metadata** (Hardware Handoff file). PYNQ Python uses this to automatically discover IP blocks and AXI register offsets, enabling communication between the ARM processor and the custom hardware.
    
*   `system\_i\_wrapper.xsa`: The Xilinx Shell Archive, often preferred for Vitis/PYNQ deployment as it bundles the hardware description and bitstream.
    

### **src\_hls/**

*   `iaf\_psc\_exp\_hls.cpp`, `iaf\_psc\_exp\_hls.h`: Your **HLS C++ source code** implementing the single-step neuron logic, which models the IAF-PSC-EXP differential equation.
    
*   All inputs and outputs are mapped to **AXI-Lite registers** (`s\_axilite`) so they can be set and read directly by the ARM processor at runtime.
    


### **scripts/**

*   `hls\_make\_axilite.tcl`: Tcl script used to build and export the HLS IP from C++ source.
    
*   `vivado\_wire\_axilite.tcl`: **Critical script** for automating the Vivado flow, including instantiating the HLS IP and connecting its control interface to the Zynq's **`M\_AXI\_GP0`** port.
    
*   Other Tcl scripts (e.g., `vivado\_refresh\_hls.tcl`) for maintaining the Vivado project.
    

