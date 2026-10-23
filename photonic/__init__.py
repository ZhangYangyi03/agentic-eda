"""光芯片（硅光）辅助设计：器件模型 + 电路求解 + 物理闸门 + 版图协同。

分工与电子侧一致：本包只负责"给出一个可被检验的设计"，
可不可信由 physgate / co_design 判定，不由模型自己声明。
"""
from .models import (mzi, analytic_mzi, mmi2x2, waveguide, phase_shifter,
                     neff, WL_DEFAULT)
from .physgate import check_mzi, check_unitarity, Verdict
from .codesign import co_design, CoDesignResult

__all__ = ["mzi", "analytic_mzi", "mmi2x2", "waveguide", "phase_shifter",
           "neff", "WL_DEFAULT", "check_mzi", "check_unitarity", "Verdict",
           "co_design", "CoDesignResult"]
