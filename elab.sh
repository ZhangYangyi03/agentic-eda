
cd /mnt/d/eda/bench/src
for f in *.v; do
  n="${f%.v}"
  yosys -q -p "read_verilog $f; hierarchy -auto-top; proc; opt; stat" > /tmp/elab_$n.txt 2>&1
  rc=$?
  cells=$(grep -m1 "Number of cells:" /tmp/elab_$n.txt | awk '{print $NF}')
  wires=$(grep -m1 "Number of wire bits:" /tmp/elab_$n.txt | awk '{print $NF}')
  err=$(grep -m1 "ERROR" /tmp/elab_$n.txt | head -c 80)
  echo "$n rc=$rc cells=${cells:-?} wirebits=${wires:-?} $err"
done
