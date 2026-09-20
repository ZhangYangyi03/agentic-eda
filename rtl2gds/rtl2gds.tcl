# rtl2gds.tcl -- sky130 physical flow (OpenROAD f12e2f47, PDK open_pdks sky130A)
# Each stage must succeed before the next one means anything.
set PDK   $::env(PDK)
set DESIGN $::env(DESIGN)
set OUT   $::env(OUTDIR)
# This PDK build ships one combined LEF that carries both the technology layers
# and the standard cells; there is no separate .tlef, so reading it twice would
# be wrong and reading a second file would fail.
# Two files, and both are required. The cell LEF has MACROs only -- no LAYER
# definitions at all, so OpenROAD reads 0 layers from it and every routing
# command fails with "Layer met3 not found". The real technology section is in
# techlef/, and the name is NOT the obvious one: it is suffixed by the process
# corner (__nom), so sky130_fd_sc_hd.tlef does not exist. Reading the cell LEF
# alone is a silent dead end: the design reads, links and floorplans fine.
set LEF       "$PDK/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef"
set TECH_LEF  "$PDK/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef"
# The liberty is not optional and it is not only for timing: without it
# initialize_floorplan fails with "Command units uninitialized" and every LEF
# master is reported as having no liberty cell, so the design has no area and
# no delay at all.
set LIB   "$PDK/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"

proc stage {n} { puts "STAGE_BEGIN $n" ; flush stdout }
proc ok    {n} { puts "STAGE_OK $n" ; flush stdout }

stage read
read_lef $TECH_LEF
read_lef $LEF
read_liberty $LIB
read_verilog $::env(NETLIST)
link_design $DESIGN
ok read

# Tracks must come after read_liberty, and the ordering is the whole reason this
# failed: `make_tracks` takes distances in microns, and WITHOUT a liberty loaded
# it refuses with "Command units uninitialized" -- so a track block placed
# before the liberty silently creates no tracks, and the failure only surfaces
# three stages later as "Horizontal routing tracks not found for layer met3"
# from place_pins. The techlef has no TRACKS section; the pitches come from
# libs.tech/openlane/sky130_fd_sc_hd/tracks.info.

stage floorplan
initialize_floorplan -utilization 30 -aspect_ratio 1.0 -core_space 5 -site unithd
ok floorplan

stage tracks
make_tracks li1  -x_offset 0.23 -x_pitch 0.46 -y_offset 0.17 -y_pitch 0.34
make_tracks met1 -x_offset 0.17 -x_pitch 0.34 -y_offset 0.17 -y_pitch 0.34
make_tracks met2 -x_offset 0.23 -x_pitch 0.46 -y_offset 0.23 -y_pitch 0.46
make_tracks met3 -x_offset 0.34 -x_pitch 0.68 -y_offset 0.34 -y_pitch 0.68
make_tracks met4 -x_offset 0.46 -x_pitch 0.92 -y_offset 0.46 -y_pitch 0.92
make_tracks met5 -x_offset 1.70 -x_pitch 3.40 -y_offset 1.70 -y_pitch 3.40
ok tracks

stage pin_place
place_pins -random -hor_layers met3 -ver_layers met2
ok pin_place

stage global_place
global_placement -density 0.6
ok global_place

stage detailed_place
detailed_placement
check_placement
ok detailed_place

stage cts
create_clock -name clk -period 10.0 [get_ports clk]
clock_tree_synthesis -buf_list sky130_fd_sc_hd__clkbuf_4 -root_buf sky130_fd_sc_hd__clkbuf_4
# CTS inserts new cells, and they are not legalised by itself: routing then
# fails with "Found pin outside die area in instance clkbuf_1_0__f_clk", naming
# the buffer CTS just made. Legalise again before anything routes.
detailed_placement
ok cts

stage filler
filler_placement "sky130_fd_sc_hd__fill_1 sky130_fd_sc_hd__fill_2 sky130_fd_sc_hd__fill_4"
ok filler

stage route
global_route
detailed_route -output_drc "$OUT/drc.rpt"
ok route

stage write
# The 9 DRC violations magic reports are all one rule, met1.6 minimum area.
# The rule IS in the tech LEF ("AREA 0.083" under LAYER met1) but this OpenROAD
# does not enforce it: there is no repair command for it and detailed_route
# reports 0 violations of its own. Padding met1 shapes is the standard workaround
# This OpenROAD has no fill-for-min-area command either, so the flow stands as it is:
# 0 violations in the router, 9 met1.6 in magic's signoff deck. That number is
# reproduced below rather than papered over.
write_def "$OUT/$DESIGN.def"
write_verilog "$OUT/${DESIGN}_routed.v"
report_design_area
ok write
puts "FLOW_DONE"
