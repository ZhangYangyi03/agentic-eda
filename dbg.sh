set -u
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/baseline"
echo "--BEGIN baseline"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/baseline" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite; balance; rewrite; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/baseline/mapped.blif" 2>/dev/null
echo "--OPT baseline rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/baseline/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/baseline/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END baseline"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/drw"
echo "--BEGIN drw"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/drw" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite -l; balance; rewrite -lz; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/drw/mapped.blif" 2>/dev/null
echo "--OPT drw rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/drw/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/drw/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END drw"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/resub6"
echo "--BEGIN resub6"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/resub6" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite; resub -K 6; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/resub6/mapped.blif" 2>/dev/null
echo "--OPT resub6 rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/resub6/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/resub6/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END resub6"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/resub8"
echo "--BEGIN resub8"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/resub8" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite; resub -K 8 -N 2; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/resub8/mapped.blif" 2>/dev/null
echo "--OPT resub8 rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/resub8/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/resub8/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END resub8"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/dc2"
echo "--BEGIN dc2"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/dc2" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite; dc2; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/dc2/mapped.blif" 2>/dev/null
echo "--OPT dc2 rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/dc2/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/dc2/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END dc2"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/if6"
echo "--BEGIN if6"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/if6" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite; if -K 6; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/if6/mapped.blif" 2>/dev/null
echo "--OPT if6 rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/if6/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/if6/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END if6"
mkdir -p "/mnt/d/eda/bench/run/mult4/work/dbg/mix"
echo "--BEGIN mix"
cd "/mnt/d/eda/bench/run/mult4/work/dbg/mix" && timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/gold.blif; strash; balance; rewrite -l; resub -K 8; dc2; if -K 6; balance; print_stats; write_blif /mnt/d/eda/bench/run/mult4/work/dbg/mix/mapped.blif" 2>/dev/null
echo "--OPT mix rc=$?"
if [ -f "/mnt/d/eda/bench/run/mult4/work/dbg/mix/mapped.blif" ]; then
  timeout 240 yosys-abc -c "read_blif /mnt/d/eda/bench/run/mult4/work/dbg/mix/mapped.blif; cec /mnt/d/eda/bench/run/mult4/work/gold.blif" 2>/dev/null
fi
echo "--END mix"