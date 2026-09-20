
drc off
gds readonly true
gds rescale false
gds read cnt4.gds
load cnt4
select top cell
drc check
drc catchup
puts "DRC_TOTAL [drc list count]"
foreach v [drc listall why] { puts "VIOL $v" }
quit -noprompt
