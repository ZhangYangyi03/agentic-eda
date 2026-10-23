
import numpy as np
import photonic.models as M
for nm in ("dc_gap=200nm_Lc=0um","dc_gap=200nm_Lc=10um","Ybranch_Thickness=220width=500"):
    q = M.extract_design_parameters(nm)
    print(f"{nm:32s} split={q['split_power']:.6f}  IL={q['insertion_dB']:+.3f}dB  imbalance={q['imbalance_dB']:+.2f}dB")
