import sys, collections
bl, name = sys.argv[1], sys.argv[2]
lines=[l.strip() for l in open(bl, encoding="utf-8", errors="replace")]
n_names=sum(1 for l in lines if l.startswith(".names"))
drv={l.split()[1] for l in lines if l.startswith(".names")}
outs=[l for l in lines if l.startswith(".outputs")]
outs=outs[0].split()[1:] if outs else []
lat=sum(1 for l in lines if l.startswith(".latch"))
und=[o for o in outs if o not in drv]
print("%-16s names=%-4d outs=%-3d latches=%-3d undriven=%d %s" % (name, n_names, len(outs), lat, len(und), und[:3]))
