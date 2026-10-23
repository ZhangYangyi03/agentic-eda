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


环形谐振器（add-drop）
----------------------
    from photonic import ring_add_drop, check_ring, check_ring_resonances
    S = ring_add_drop(radius_um=20.0, k1=0.2, k2=0.2, loss_db_per_cm=2.0)
    print(check_ring(radius_um=20.0).lines())
    print(check_ring_resonances(radius_um=20.0).lines())

实测输出：

    VERDICT: ACCEPTED
      [ok] passive (|thru|^2+|drop|^2 <= 1): max total power = 0.999940949
      [ok] reference (independent derivation): max|dthru|=2.12e-15 max|ddrop|=2.20e-15
      [ok] reciprocity S12 == S21: 0.00e+00

    VERDICT: ACCEPTED
      [ok] dip count == integer-order roots: 63 dips measured, 63 roots
      [ok] dip positions: max |dip - root| = 0.00050 nm over 63 dips

环有损耗，S 不幺正，所以这里不用 S^H S = I，换三条：无源、独立推导对拍、互易。
独立推导 `ring_add_drop_analytic` 走的是另一条代数路径（分子分母重新组合、drop 通道
用 sqrt(A) e^{i phi/2}），不是把同一个分式照抄一遍。

谐振位置那条判据最硬：谱线数值找谷 与 整数阶方程 m*lambda = neff(lambda)*L 的根
一一对上。63 个谷全中，最大偏差 0.0005 nm。

在这上面栽过的三个坑（都写进了 models.py 的注释）
------------------------------------------------
1. 回路相位把 L 和 lambda 单位搞错（`(L/1e3)/wl`），相位缩小 1000 倍，谱线全平、
   动态范围 0 dB，**不报任何错**。探针：through 动态范围必须 > 10 dB。
2. neff 的斜率符号写反（写成 (NG-NEFF)/1.55），ng 从 4.2 变成 0.68，FSR 大一倍多。
   谐振**位置**不受影响（相位差个常数可用等价阶数吸收），所以只看谷位发现不了。
   探针：group_index(1.55) 必须等于 4.2。
3. 先猜 order 再解 lambda：neff*L/lambda 在 1.45–1.75 um 从 110 单调降到 93，
   猜错 order 的方程**没有根**，牛顿法滑到无意义处，虚增出一堆假谷。
   正确做法：先定波长，再算 m = neff*L/lambda，整数才收。

已知边界（重要）
----------------
一阶线性色散模型 ng 恒定，`fsr_nm` 因此是常数；真实硅波导的 ng 随波长变，
所以这个模型只适合 **C 波段 ±20 nm**。跨带设计必须换成实测 S 参数。


MZI 与 SAX 0.18 的四个静默坑（每一个都让结果全错且不报错）
----------------------------------------------------------
1. 键序 (输入, 输出) vs (输出, 输入)。错的时候不报错，只给 0。
   本包最终：mmi2x2 / dc_measured / waveguide / phase_shifter 都用 (输入, 输出)。
2. 一个 S 字典里若有两条键指向同一个输入名（例如写出两个 ("in1", *)），
   电路全 0。键必须一一对应。
3. 网表连接：nets 的成对连接 + ports 挂上下游，是唯一能跑出非零的写法；
   在 connections 里直接写 "下一个实例,端口" 会全 0。
4. 相移器 dphi_rad **不是弧度**，是"相移器的等效长度（um）"。
   写成一个与波长无关的常数相位 e^{i phi}，会让干涉谷变成深 1.0 的
   非物理形状（常数相位差 = 无穷长群时延）。现在它与 waveguide 共用
   同一条色散公式，闸门的色散一致性检查会直接抓到这类错。
   要真正实现相位 phi：L = phi * lambda / (2*pi*neff)。

闸门为什么这样写
----------------
`check_mzi` 四条：幺正性、与解析解逐点对拍、色散一致性、端口完备。
第三条我改过四版才写对，错误走法都留在现场：
  * 在 |S| 干涉零点处取相位算群延迟 —— 零点相位跳 180°，梯度爆到 1000+，
    "10/401 违例"全是这些点；
  * 判"相位随波长单调增 = 因果" —— 方向反了；
  * 换成"dphi/dlambda <= 0" —— 同义反复，任何延迟都满足，抓不到错；
  * 最后用**量级**：dphi/dlambda 必须等于 -pi*ng*L/lambda^2。
    实测 -164.50 vs 理论 -164.76 rad/um，比值 0.9984。
    这条能抓到的具体错误：dL 单位多除 1000 时斜率小 1000 倍，
    而 |S| 曲线仍然"看着像干涉"，只看形状的检查全都发现不了。
