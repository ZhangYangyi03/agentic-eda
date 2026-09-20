
# def2gds.tcl -- DEF -> GDS through magic, using the PDK's own tech file.
# The cell GDS library must be read first: the DEF only names cells
# (sky130_fd_sc_hd__dfrtp_1 ...), magic needs their geometry to exist before
# def read can resolve them.
drc off
crashbackups stop
set PDK $::env(PDK)
set DEF $::env(DEF)
set OUT $::env(GDSOUT)
gds readonly true
gds rescale false
gds read $PDK/libs.ref/sky130_fd_sc_hd/gds/sky130_fd_sc_hd.gds
puts "GDS_LIB_READ"
def read $DEF
puts "DEF_READ"
load cnt4 -dereference
select top cell
puts "TOP [cellname list top]"
gds write $OUT
puts "GDS_WRITTEN"
quit -noprompt
