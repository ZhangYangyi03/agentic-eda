set -u
mkdir -p "/mnt/d/eda/random/prio32_s1/r00"
echo "--BEGIN r00"
cd "/mnt/d/eda/random/prio32_s1/r00" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; dch; fx; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r00/mapped.blif" 2>/dev/null
echo "--OPT r00 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r00/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r00/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r00"
mkdir -p "/mnt/d/eda/random/prio32_s1/r01"
echo "--BEGIN r01"
cd "/mnt/d/eda/random/prio32_s1/r01" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; strash; rewrite -lz; balance; drw; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r01/mapped.blif" 2>/dev/null
echo "--OPT r01 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r01/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r01/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r01"
mkdir -p "/mnt/d/eda/random/prio32_s1/r02"
echo "--BEGIN r02"
cd "/mnt/d/eda/random/prio32_s1/r02" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; renode; strash; if -K 4; balance; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r02/mapped.blif" 2>/dev/null
echo "--OPT r02 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r02/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r02/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r02"
mkdir -p "/mnt/d/eda/random/prio32_s1/r03"
echo "--BEGIN r03"
cd "/mnt/d/eda/random/prio32_s1/r03" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; mfs; strash; balance; fx; mfs; if -K 4; dc2; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r03/mapped.blif" 2>/dev/null
echo "--OPT r03 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r03/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r03/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r03"
mkdir -p "/mnt/d/eda/random/prio32_s1/r04"
echo "--BEGIN r04"
cd "/mnt/d/eda/random/prio32_s1/r04" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; resub -K 8; rewrite -z; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r04/mapped.blif" 2>/dev/null
echo "--OPT r04 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r04/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r04/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r04"
mkdir -p "/mnt/d/eda/random/prio32_s1/r05"
echo "--BEGIN r05"
cd "/mnt/d/eda/random/prio32_s1/r05" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; renode; strash; dch; mfs; renode; fx; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r05/mapped.blif" 2>/dev/null
echo "--OPT r05 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r05/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r05/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r05"
mkdir -p "/mnt/d/eda/random/prio32_s1/r06"
echo "--BEGIN r06"
cd "/mnt/d/eda/random/prio32_s1/r06" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; renode; strash; mfs; rewrite -lz; mfs; resub -K 8 -N 2; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r06/mapped.blif" 2>/dev/null
echo "--OPT r06 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r06/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r06/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r06"
mkdir -p "/mnt/d/eda/random/prio32_s1/r07"
echo "--BEGIN r07"
cd "/mnt/d/eda/random/prio32_s1/r07" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; fx; dch; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r07/mapped.blif" 2>/dev/null
echo "--OPT r07 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r07/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r07/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r07"
mkdir -p "/mnt/d/eda/random/prio32_s1/r08"
echo "--BEGIN r08"
cd "/mnt/d/eda/random/prio32_s1/r08" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; renode; strash; dc2; drw -l; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r08/mapped.blif" 2>/dev/null
echo "--OPT r08 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r08/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r08/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r08"
mkdir -p "/mnt/d/eda/random/prio32_s1/r09"
echo "--BEGIN r09"
cd "/mnt/d/eda/random/prio32_s1/r09" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; mfs; strash; mfs; mfs; drw; fx; renode; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r09/mapped.blif" 2>/dev/null
echo "--OPT r09 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r09/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r09/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r09"
mkdir -p "/mnt/d/eda/random/prio32_s1/r10"
echo "--BEGIN r10"
cd "/mnt/d/eda/random/prio32_s1/r10" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; mfs; strash; balance; fx; dc2; mfs; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r10/mapped.blif" 2>/dev/null
echo "--OPT r10 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r10/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r10/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r10"
mkdir -p "/mnt/d/eda/random/prio32_s1/r11"
echo "--BEGIN r11"
cd "/mnt/d/eda/random/prio32_s1/r11" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; balance; rewrite; fx; dch; print_stats; write_blif /mnt/d/eda/random/prio32_s1/r11/mapped.blif" 2>/dev/null
echo "--OPT r11 rc=$?"
if [ -f "/mnt/d/eda/random/prio32_s1/r11/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random/prio32_s1/r11/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r11"