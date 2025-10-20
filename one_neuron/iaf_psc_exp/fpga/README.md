IAF-PSC-EXP Single Neuron FPGA Package
======================================

This folder contains the complete source, configuration, and final binaries used to implement and validate the **Integrate-and-Fire (IAF-PSC-EXP) HLS kernel** on the **PYNQ-Z1** (Zynq-7000 SoC).

The design uses **AXI-Lite** for all register-based parameter loading (e.g., $V\_{th}$, $\\tau\_m$, $I\_{ext}$) and state reading (e.g., $V\_m$, spike).

📂 Folder Overview
------------------

### **bitstream/**

*   system\_i\_wrapper.bit: The **final FPGA configuration file**. This is loaded onto the PYNQ-Z1 to configure the FPGA fabric.
    
*   system\_i\_wrapper.hwh: The **hardware description metadata** (Hardware Handoff file). PYNQ Python uses this to automatically discover IP blocks and AXI register offsets, enabling communication between the ARM processor and the custom hardware.
    
*   system\_i\_wrapper.xsa: The Xilinx Shell Archive, often preferred for Vitis/PYNQ deployment as it bundles the hardware description and bitstream.
    

### **src\_hls/**

*   iaf\_psc\_exp\_hls.cpp, iaf\_psc\_exp\_hls.h: Your **HLS C++ source code** implementing the single-step neuron logic, which models the IAF-PSC-EXP differential equation.
    
*   All inputs and outputs are mapped to **AXI-Lite registers** (s\_axilite) so they can be set and read directly by the ARM processor at runtime.
    

### **ip\_export/** (Generated)

*   Contains the **packaged HLS IP** (usually a .zip file and unzipped contents). This is the compiled HDL version of your C++ code, ready to be imported into a Vivado block design.
    

### **vivado\_bd/**

*   iaf\_fpga\_hw.xpr: The **main Vivado project** file.
    
*   system\_i.bd: The **Block Design source** file, showing the connection between the Zynq Processing System (PS), the AXI Interconnect, and your custom HLS kernel (iaf\_psc\_exp\_hls).
    

### **scripts/**

*   hls\_make\_axilite.tcl: Tcl script used to build and export the HLS IP from C++ source.
    
*   vivado\_wire\_axilite.tcl: **Critical script** for automating the Vivado flow, including instantiating the HLS IP and connecting its control interface to the Zynq's **M\_AXI\_GP0** port.
    
*   Other Tcl scripts (e.g., vivado\_refresh\_hls.tcl) for maintaining the Vivado project.
    

✅ Validation and Results
------------------------

The primary validation method is a direct comparison against the gold standard: the same **IAF-PSC-EXP** neuron model implemented in **NEST Simulator**.

The plots below show the response of the FPGA model and the NEST model to a strong input current pulse.

### 1\. **FPGA vs. NEST Comparison**

This figure directly compares the membrane potential ($V$), injected current ($I$), and resulting spike times from both the FPGA and the NEST simulation over the full duration.

The close alignment confirms the fidelity of the fixed-point implementation on the Zynq FPGA.

### 2\. **FPGA Trace**

A closer look at the FPGA trace shows the characteristic behavior:

*   Voltage rises during the current pulse.
    
*   Once the threshold is reached, the neuron spikes (resetting V to $V\_{reset}$) and enters a refractory period.
    

🛠 How to Rebuild the Hardware
------------------------------

1.  **HLS Synthesis (Vitis HLS):** Run the hls\_make\_axilite.tcl script against the C++ sources in src\_hls/ to generate the HLS IP, placing it into ip\_export/.
    
2.  **Block Design (Vivado):** Open vivado\_bd/iaf\_fpga\_hw.xpr and run the necessary Tcl scripts in scripts/ (e.g., vivado\_wire\_axilite.tcl) to instantiate the HLS IP and connect it to the Zynq PS.
    
3.  **Implementation (Vivado):** Run Synthesis, Implementation, and finally Generate Bitstream to produce the final .bit and .hwh files in the bitstream/ folder.
    

To run the full validation, please refer to the Python scripts in the sibling **../python** directory.
