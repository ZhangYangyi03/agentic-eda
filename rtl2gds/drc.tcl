
drc off
gds readonly true
gds rescale false
gds read cnt4.gds
load cnt4
select top cell
puts "TOPCELL [cellname list top]"
puts "BOX [box values]"
drc check
puts "DRC_VIOLATIONS [drc list count]"
drc catchup
puts "DRC_TOTAL [drc list count]"
drc listall why
quit -noprompt
