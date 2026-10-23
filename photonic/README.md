photonic/ —— 光芯片（硅光）辅助设计
====================================

这个目录是 agentic-eda 的光学半边。电子半边（RTL→GDS）不变；这一边把同一套
"设计 → 验证 → 版图" 的形状搬到光子学上，判据换成物理的。

一条命令：

    .venv-photonic\Scripts\python photonics_demo.py --dL 30

或者按三步拆开写：

    from photonic import mzi, check_mzi, co_design

    S, wl = mzi(dL_um=30.0)          # 1. 电路级：参数化网表 -> 频谱
    print(check_mzi(dL_um=30.0).lines())   # 2. 物理闸门：通过/拒绝 + 数值
    print(co_design(dL_um=30.0).lines())   # 3. 版图级：GDS + 与电路参数对拍

实测输出（本机，401 点，1500–1600 nm）：

    MZI dL=30um
      out2 功率 均值 0.9781 区间 [0.9777, 0.9785]
      能量守恒 max|P1+P2-1| = 8.88e-16

    VERDICT: ACCEPTED
      [ok] unitarity S^H S = I: max|S^H S - I| = 6.661e-16
      [ok] reference (analytic): max|S - S_ref| = 3.342e-16 over 4 paths
      [ok] causality dphi/dlambda <= 0: 0/401 points with positive group delay
      [ok] ports complete (no dangling): all inputs carry power

    CO-DESIGN: CONSISTENT
      circuit: dL=30.0um ports=['in1','in2','out1','out2']
      layout : dL=30.0um ports=['o1','o2','o3','o4'] gds=11762B

为什么有 physgate
-----------------
与电子侧"等价性证明"同一个角色：一个设计在没通过独立参考之前不算设计。
四条判据都是可判定的——幺正性、与解析解逐点对拍、因果性（群延迟符号）、
端口完备。任何一条不过就是 rejected，并给出差多少。

闸门自己也要被检验：test_physgate_rejects_broken_model 把一个不平衡的
耦合器（0.8/0.6）塞进去，闸门必须拒绝。拒绝不了坏设计，这门就等于没有。

上游的两个坑（已锁进测试）
--------------------------
1. SAX 0.18：用 instances[].connections 连多级电路会**静默返回 0**，不报错。
   必须用 netlist 的 "nets": [{"p1": "inst,port", "p2": "inst,port"}, ...]。
   见 test_sax_connections_bug_is_real。
2. 波长轴：模型内部用闭包波长、直接返回 batch 的 S（形状 = 波长点数），
   整条电路就是 batch 的。一旦有实例不 batch，SAX 会退化成标量并对不齐。
   所以 waveguide() 永远返回数组，mmi2x2() 返回标量（会被广播）。

Windows 上还有两处环境坑，layout.py 里已经处理：
  * gdsfactory 调 getpass.getuser()，嵌入环境下会 import pwd 失败 → 需 USERNAME。
  * 不激活 PDK 时 get_cross_section 直接抛 ValueError。

依赖与运行
----------
    .venv-photonic/Scripts/python -m pip install numpy scipy sax jax jaxlib
        klujax jaxtyping xarray optax sympy lark scikit-rf gdsfactory

测试分两级（本机 13.7 GB 内存，gdsfactory+jax 同时载入会 OOM）：

    # 电路级（轻）
    PHOTONIC_SKIP_CODESIGN=1 pytest photonic/test_photonic.py -q
    # 协同/版图级（重）
    pytest photonic/test_photonic.py -q -k co_design

现状与边界
----------
真做了：MMI、波导（含一阶色散）、相移器、MZI 单元；SAX 电路求解；四条物理
判据；gdsfactory 版图与参数对拍；14 条回归用例。

没做：跑真实 FDTD/FDE 仿真（本机无 Lumerical/Tidy3D）；真实 PDK 签名数据
（当前 neff/ng 是通用量级，不是某家 foundry 的）；有源器件（调制器/探测器）；
环形谐振器与 WDM 阵列。

下一步最有价值的一件事：找一组真实的 foundry 器件 S 参数（Touchstone），
用 sax.read 读进来替换理想模型，physgate 不用改——它比的是"同一设计的两条
独立路径"，不是"理想 vs 理想"。
