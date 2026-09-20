set -u
mkdir -p "/mnt/d/eda/evolve/seed3/g0_00"
echo "--BEGIN g0_00"
cd "/mnt/d/eda/evolve/seed3/g0_00" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; balance; rewrite; strash; balance; rewrite; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_00/mapped.blif" 2>/dev/null
echo "--OPT g0_00 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_00/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_00/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_00"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_01"
echo "--BEGIN g0_01"
cd "/mnt/d/eda/evolve/seed3/g0_01" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; balance; rewrite; strash; dc2; dch; balance; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_01/mapped.blif" 2>/dev/null
echo "--OPT g0_01 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_01/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_01/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_01"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_02"
echo "--BEGIN g0_02"
cd "/mnt/d/eda/evolve/seed3/g0_02" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; mfs; strash; rewrite -l; resub -K 8; dc2; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_02/mapped.blif" 2>/dev/null
echo "--OPT g0_02 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_02/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_02/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_02"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_03"
echo "--BEGIN g0_03"
cd "/mnt/d/eda/evolve/seed3/g0_03" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; renode; strash; fx; drw; if -K 4; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_03/mapped.blif" 2>/dev/null
echo "--OPT g0_03 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_03/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_03/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_03"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_04"
echo "--BEGIN g0_04"
cd "/mnt/d/eda/evolve/seed3/g0_04" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; mfs; strash; renode; dc2; if -K 4; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_04/mapped.blif" 2>/dev/null
echo "--OPT g0_04 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_04/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_04/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_04"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_05"
echo "--BEGIN g0_05"
cd "/mnt/d/eda/evolve/seed3/g0_05" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; fx; strash; if -K 4; mfs; drw; dch; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_05/mapped.blif" 2>/dev/null
echo "--OPT g0_05 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_05/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_05/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_05"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_06"
echo "--BEGIN g0_06"
cd "/mnt/d/eda/evolve/seed3/g0_06" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; dc2; dch; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_06/mapped.blif" 2>/dev/null
echo "--OPT g0_06 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_06/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_06/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_06"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_07"
echo "--BEGIN g0_07"
cd "/mnt/d/eda/evolve/seed3/g0_07" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; renode; strash; resub -K 4; drw; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_07/mapped.blif" 2>/dev/null
echo "--OPT g0_07 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_07/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_07/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_07"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_08"
echo "--BEGIN g0_08"
cd "/mnt/d/eda/evolve/seed3/g0_08" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; mfs; strash; resub -K 8 -N 2; mfs; drw; dc2; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_08/mapped.blif" 2>/dev/null
echo "--OPT g0_08 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_08/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_08/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_08"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_09"
echo "--BEGIN g0_09"
cd "/mnt/d/eda/evolve/seed3/g0_09" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; fx; strash; mfs; rewrite -lz; drw -l; if -K 8; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_09/mapped.blif" 2>/dev/null
echo "--OPT g0_09 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_09/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_09/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_09"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_10"
echo "--BEGIN g0_10"
cd "/mnt/d/eda/evolve/seed3/g0_10" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; renode; strash; mfs; mfs; balance; if -K 8; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_10/mapped.blif" 2>/dev/null
echo "--OPT g0_10 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_10/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_10/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_10"
mkdir -p "/mnt/d/eda/evolve/seed3/g0_11"
echo "--BEGIN g0_11"
cd "/mnt/d/eda/evolve/seed3/g0_11" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif; strash; drw -l; fx; print_stats; write_blif /mnt/d/eda/evolve/seed3/g0_11/mapped.blif" 2>/dev/null
echo "--OPT g0_11 rc=$?"
if [ -f "/mnt/d/eda/evolve/seed3/g0_11/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/evolve/seed3/g0_11/mapped.blif; cec /mnt/d/eda/evolve/prio32/work/elaborate/gold.blif" 2>/dev/null
fi
echo "--END g0_11"