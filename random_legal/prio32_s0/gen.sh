set -u
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r00"
echo "--BEGIN r00"
cd "/mnt/d/eda/random_legal/prio32_s0/r00" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; fx; strash; dch; dc2; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r00/mapped.blif" 2>/dev/null
echo "--OPT r00 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r00/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r00/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r00"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r01"
echo "--BEGIN r01"
cd "/mnt/d/eda/random_legal/prio32_s0/r01" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; dc2; drw; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r01/mapped.blif" 2>/dev/null
echo "--OPT r01 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r01/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r01/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r01"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r02"
echo "--BEGIN r02"
cd "/mnt/d/eda/random_legal/prio32_s0/r02" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; dc2; rewrite -lz; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r02/mapped.blif" 2>/dev/null
echo "--OPT r02 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r02/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r02/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r02"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r03"
echo "--BEGIN r03"
cd "/mnt/d/eda/random_legal/prio32_s0/r03" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; dch; drw; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r03/mapped.blif" 2>/dev/null
echo "--OPT r03 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r03/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r03/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r03"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r04"
echo "--BEGIN r04"
cd "/mnt/d/eda/random_legal/prio32_s0/r04" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; mfs; strash; rewrite -lz; drw; balance; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r04/mapped.blif" 2>/dev/null
echo "--OPT r04 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r04/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r04/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r04"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r05"
echo "--BEGIN r05"
cd "/mnt/d/eda/random_legal/prio32_s0/r05" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; balance; resub -K 8 -N 2; rewrite -z; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r05/mapped.blif" 2>/dev/null
echo "--OPT r05 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r05/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r05/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r05"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r06"
echo "--BEGIN r06"
cd "/mnt/d/eda/random_legal/prio32_s0/r06" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; rewrite -lz; resub -K 8 -N 2; drw -l; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r06/mapped.blif" 2>/dev/null
echo "--OPT r06 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r06/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r06/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r06"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r07"
echo "--BEGIN r07"
cd "/mnt/d/eda/random_legal/prio32_s0/r07" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; rewrite -l; resub -K 4; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r07/mapped.blif" 2>/dev/null
echo "--OPT r07 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r07/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r07/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r07"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r08"
echo "--BEGIN r08"
cd "/mnt/d/eda/random_legal/prio32_s0/r08" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; dch; drw -l; balance; resub -K 6; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r08/mapped.blif" 2>/dev/null
echo "--OPT r08 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r08/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r08/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r08"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r09"
echo "--BEGIN r09"
cd "/mnt/d/eda/random_legal/prio32_s0/r09" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; strash; balance; drw; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r09/mapped.blif" 2>/dev/null
echo "--OPT r09 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r09/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r09/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r09"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r10"
echo "--BEGIN r10"
cd "/mnt/d/eda/random_legal/prio32_s0/r10" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; strash; if -K 6; balance; drw -l; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r10/mapped.blif" 2>/dev/null
echo "--OPT r10 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r10/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r10/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r10"
mkdir -p "/mnt/d/eda/random_legal/prio32_s0/r11"
echo "--BEGIN r11"
cd "/mnt/d/eda/random_legal/prio32_s0/r11" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; strash; rewrite -lz; rewrite; print_stats; write_blif /mnt/d/eda/random_legal/prio32_s0/r11/mapped.blif" 2>/dev/null
echo "--OPT r11 rc=$?"
if [ -f "/mnt/d/eda/random_legal/prio32_s0/r11/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/random_legal/prio32_s0/r11/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END r11"