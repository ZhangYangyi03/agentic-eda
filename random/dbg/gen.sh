set -u
mkdir -p "/mnt/d/eda/random/dbg/r00"
echo "--BEGIN r00"
cd "/mnt/d/eda/random/dbg/r00" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; mfs; drw -l; fx; renode; print_stats; write_blif /mnt/d/eda/random/dbg/r00/mapped.blif" 2>/dev/null
echo "--OPT r00 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r00/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r00/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r00"
mkdir -p "/mnt/d/eda/random/dbg/r01"
echo "--BEGIN r01"
cd "/mnt/d/eda/random/dbg/r01" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; fx; strash; mfs; dch; rewrite -z; fx; print_stats; write_blif /mnt/d/eda/random/dbg/r01/mapped.blif" 2>/dev/null
echo "--OPT r01 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r01/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r01/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r01"
mkdir -p "/mnt/d/eda/random/dbg/r02"
echo "--BEGIN r02"
cd "/mnt/d/eda/random/dbg/r02" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; mfs; fx; balance; print_stats; write_blif /mnt/d/eda/random/dbg/r02/mapped.blif" 2>/dev/null
echo "--OPT r02 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r02/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r02/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r02"
mkdir -p "/mnt/d/eda/random/dbg/r03"
echo "--BEGIN r03"
cd "/mnt/d/eda/random/dbg/r03" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; balance; if -K 4; if -K 8; rewrite -l; renode; print_stats; write_blif /mnt/d/eda/random/dbg/r03/mapped.blif" 2>/dev/null
echo "--OPT r03 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r03/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r03/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r03"
mkdir -p "/mnt/d/eda/random/dbg/r04"
echo "--BEGIN r04"
cd "/mnt/d/eda/random/dbg/r04" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; mfs; rewrite; if -K 8; print_stats; write_blif /mnt/d/eda/random/dbg/r04/mapped.blif" 2>/dev/null
echo "--OPT r04 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r04/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r04/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r04"
mkdir -p "/mnt/d/eda/random/dbg/r05"
echo "--BEGIN r05"
cd "/mnt/d/eda/random/dbg/r05" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; rewrite -z; mfs; renode; fx; print_stats; write_blif /mnt/d/eda/random/dbg/r05/mapped.blif" 2>/dev/null
echo "--OPT r05 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r05/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r05/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r05"
mkdir -p "/mnt/d/eda/random/dbg/r06"
echo "--BEGIN r06"
cd "/mnt/d/eda/random/dbg/r06" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; renode; strash; resub -K 6; resub -K 4; renode; fx; print_stats; write_blif /mnt/d/eda/random/dbg/r06/mapped.blif" 2>/dev/null
echo "--OPT r06 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r06/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r06/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r06"
mkdir -p "/mnt/d/eda/random/dbg/r07"
echo "--BEGIN r07"
cd "/mnt/d/eda/random/dbg/r07" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; resub -K 4; rewrite -lz; mfs; print_stats; write_blif /mnt/d/eda/random/dbg/r07/mapped.blif" 2>/dev/null
echo "--OPT r07 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r07/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r07/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r07"
mkdir -p "/mnt/d/eda/random/dbg/r08"
echo "--BEGIN r08"
cd "/mnt/d/eda/random/dbg/r08" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; renode; strash; fx; if -K 4; if -K 8; rewrite -lz; print_stats; write_blif /mnt/d/eda/random/dbg/r08/mapped.blif" 2>/dev/null
echo "--OPT r08 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r08/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r08/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r08"
mkdir -p "/mnt/d/eda/random/dbg/r09"
echo "--BEGIN r09"
cd "/mnt/d/eda/random/dbg/r09" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; fx; strash; dch; dc2; print_stats; write_blif /mnt/d/eda/random/dbg/r09/mapped.blif" 2>/dev/null
echo "--OPT r09 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r09/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r09/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r09"
mkdir -p "/mnt/d/eda/random/dbg/r10"
echo "--BEGIN r10"
cd "/mnt/d/eda/random/dbg/r10" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; drw; rewrite -l; dc2; renode; print_stats; write_blif /mnt/d/eda/random/dbg/r10/mapped.blif" 2>/dev/null
echo "--OPT r10 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r10/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r10/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r10"
mkdir -p "/mnt/d/eda/random/dbg/r11"
echo "--BEGIN r11"
cd "/mnt/d/eda/random/dbg/r11" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; dc2; drw; print_stats; write_blif /mnt/d/eda/random/dbg/r11/mapped.blif" 2>/dev/null
echo "--OPT r11 rc=$?"
if [ -f "/mnt/d/eda/random/dbg/r11/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/dbg/r11/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r11"