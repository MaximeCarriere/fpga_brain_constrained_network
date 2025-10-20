# Open project & BD
open_project ./iaf_fpga_hw.xpr
open_bd_design ./iaf_fpga_hw.srcs/sources_1/bd/system_i/system_i.bd
current_bd_design [get_bd_designs system_i]

# Point Vivado at the freshly exported HLS IP repo and refresh catalog
set HLS_IP_REPO_PATH [file normalize [file join [pwd] "iaf_hls_project/solution1/impl/ip"]]
set_property ip_repo_paths $HLS_IP_REPO_PATH [current_project]
update_ip_catalog -rebuild

# Delete old HLS cell if present (clears lock)
set old [get_bd_cells -quiet iaf_hls_kernel]
if {$old ne ""} {
  puts "INFO: Deleting old HLS cell 'iaf_hls_kernel' (this clears lock)"
  delete_bd_objs $old
}

# Instantiate the HLS IP again (expected VLNV)
set vlnv "xilinx.com:hls:iaf_psc_exp_hls:1.0"
puts "INFO: Instantiating HLS IP VLNV: $vlnv"
create_bd_cell -type ip -vlnv $vlnv iaf_hls_kernel

# Wire both AXI-Lite slaves (s_axi_control and s_axi_control_r) to PS M_AXI_GP0
set ctrl_ifcs  [get_bd_intf_pins -of_objects [get_bd_cells iaf_hls_kernel] -quiet \
                 -filter {MODE==Slave && VLNV =~ "xilinx.com:interface:aximm_rtl:*" && NAME =~ "s_axi_control*"}]
foreach ifc [lsort $ctrl_ifcs] {
  puts "INFO: Wiring [get_property NAME $ifc] -> zynq_ps/M_AXI_GP0"
  apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config {Master "/zynq_ps/M_AXI_GP0"} $ifc
}

# If you had m_axi gmem ports to DDR via sc_hp0, reconnect them here as needed
# (left out because current kernel is per-step control only)

# Address map / validate / save
assign_bd_address
validate_bd_design
save_bd_design

# Re-gen wrapper and rebuild
generate_target all [get_files ./iaf_fpga_hw.srcs/sources_1/bd/system_i/system_i.bd]
make_wrapper -files [get_files ./iaf_fpga_hw.srcs/sources_1/bd/system_i/system_i.bd] -top -import
set_property top system_i_wrapper [current_fileset]

if {[catch {launch_runs synth_1 -jobs 4} msg]} {
  if {[string match *reset* $msg]} { reset_run synth_1; launch_runs synth_1 -jobs 4 }
}
wait_on_run synth_1

if {[catch {launch_runs impl_1 -to_step write_bitstream -jobs 4} msg]} {
  if {[string match *reset* $msg]} { reset_run impl_1; launch_runs impl_1 -to_step write_bitstream -jobs 4 }
}
wait_on_run impl_1

# Export XSA (includes .bit + .hwh)
write_hw_platform -fixed -include_bit -force ./fpga_package_iaf_20251020_0807/bitstream/system_i_wrapper.xsa
