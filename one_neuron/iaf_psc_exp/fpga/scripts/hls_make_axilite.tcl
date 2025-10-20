open_project -reset iaf_hls_project
set_top iaf_psc_exp_hls
add_files ./fpga_package_iaf_20251020_0807/src_hls/iaf_psc_exp_hls.cpp
add_files ./fpga_package_iaf_20251020_0807/src_hls/iaf_psc_exp_hls.h
open_solution -reset solution1
set_part xc7z020clg400-1
create_clock -period 10 -name default
csynth_design
export_design -format ip_catalog -output ./iaf_hls_project/solution1/impl/ip
exit
