module mult4 (a,
    b,
    p);
 input [3:0] a;
 input [3:0] b;
 output [7:0] p;

 wire _059_;
 wire _060_;
 wire _061_;
 wire _062_;
 wire _063_;
 wire _064_;
 wire _065_;
 wire _066_;
 wire _067_;
 wire _068_;
 wire _069_;
 wire _070_;
 wire _071_;
 wire _072_;
 wire _073_;
 wire _074_;
 wire _075_;
 wire _076_;
 wire _077_;
 wire _078_;
 wire _079_;
 wire _080_;
 wire _081_;
 wire _082_;
 wire _083_;
 wire _084_;
 wire _085_;
 wire _086_;
 wire _087_;
 wire _088_;
 wire _089_;
 wire _090_;
 wire _091_;
 wire _092_;
 wire _093_;
 wire _094_;
 wire _095_;
 wire _096_;
 wire _097_;
 wire _098_;
 wire _099_;
 wire _100_;
 wire _101_;
 wire _102_;
 wire _103_;
 wire _104_;
 wire _105_;
 wire _106_;
 wire _107_;

 sky130_fd_sc_hd__nand2_1 _108_ (.A(b[1]),
    .B(a[0]),
    .Y(_059_));
 sky130_fd_sc_hd__nand2_1 _109_ (.A(a[1]),
    .B(b[0]),
    .Y(_060_));
 sky130_fd_sc_hd__xor2_1 _110_ (.A(_059_),
    .B(_060_),
    .X(_101_));
 sky130_fd_sc_hd__nand2_1 _111_ (.A(a[0]),
    .B(b[2]),
    .Y(_061_));
 sky130_fd_sc_hd__and2_0 _112_ (.A(b[0]),
    .B(a[0]),
    .X(_100_));
 sky130_fd_sc_hd__nand2_1 _113_ (.A(b[0]),
    .B(a[2]),
    .Y(_062_));
 sky130_fd_sc_hd__and4_1 _114_ (.A(a[1]),
    .B(b[1]),
    .C(_100_),
    .D(_062_),
    .X(_063_));
 sky130_fd_sc_hd__nand4_1 _115_ (.A(a[1]),
    .B(b[0]),
    .C(b[1]),
    .D(a[2]),
    .Y(_064_));
 sky130_fd_sc_hd__a22o_1 _116_ (.A1(a[1]),
    .A2(b[1]),
    .B1(a[2]),
    .B2(b[0]),
    .X(_065_));
 sky130_fd_sc_hd__a2bb2oi_1 _117_ (.A1_N(_059_),
    .A2_N(_060_),
    .B1(_064_),
    .B2(_065_),
    .Y(_066_));
 sky130_fd_sc_hd__nor3_2 _118_ (.A(_061_),
    .B(_063_),
    .C(_066_),
    .Y(_067_));
 sky130_fd_sc_hd__o21ai_0 _119_ (.A1(_063_),
    .A2(_066_),
    .B1(_061_),
    .Y(_068_));
 sky130_fd_sc_hd__and2b_1 _120_ (.A_N(_067_),
    .B(_068_),
    .X(_102_));
 sky130_fd_sc_hd__nand2_1 _121_ (.A(a[1]),
    .B(b[2]),
    .Y(_069_));
 sky130_fd_sc_hd__nand4_2 _122_ (.A(b[0]),
    .B(a[0]),
    .C(b[3]),
    .D(a[3]),
    .Y(_070_));
 sky130_fd_sc_hd__a22oi_4 _123_ (.A1(a[0]),
    .A2(b[3]),
    .B1(a[3]),
    .B2(b[0]),
    .Y(_071_));
 sky130_fd_sc_hd__lpflow_isobufsrc_2 _124_ (.A(_070_),
    .SLEEP(_071_),
    .X(_072_));
 sky130_fd_sc_hd__nand2_1 _125_ (.A(b[1]),
    .B(a[2]),
    .Y(_073_));
 sky130_fd_sc_hd__a21oi_1 _126_ (.A1(a[1]),
    .A2(b[0]),
    .B1(_073_),
    .Y(_074_));
 sky130_fd_sc_hd__xnor3_1 _127_ (.A(_069_),
    .B(_072_),
    .C(_074_),
    .X(_075_));
 sky130_fd_sc_hd__o21ai_2 _128_ (.A1(_063_),
    .A2(_067_),
    .B1(_075_),
    .Y(_076_));
 sky130_fd_sc_hd__xnor2_1 _129_ (.A(_072_),
    .B(_074_),
    .Y(_077_));
 sky130_fd_sc_hd__o22a_1 _130_ (.A1(_064_),
    .A2(_072_),
    .B1(_077_),
    .B2(_069_),
    .X(_078_));
 sky130_fd_sc_hd__and2_0 _131_ (.A(a[2]),
    .B(b[2]),
    .X(_079_));
 sky130_fd_sc_hd__and4_4 _132_ (.A(a[1]),
    .B(b[1]),
    .C(b[3]),
    .D(a[3]),
    .X(_080_));
 sky130_fd_sc_hd__a22oi_1 _133_ (.A1(a[1]),
    .A2(b[3]),
    .B1(a[3]),
    .B2(b[1]),
    .Y(_081_));
 sky130_fd_sc_hd__nor2_4 _134_ (.A(_080_),
    .B(_081_),
    .Y(_082_));
 sky130_fd_sc_hd__a21oi_2 _135_ (.A1(_073_),
    .A2(_070_),
    .B1(_071_),
    .Y(_083_));
 sky130_fd_sc_hd__xor2_1 _136_ (.A(_082_),
    .B(_083_),
    .X(_084_));
 sky130_fd_sc_hd__xnor2_1 _137_ (.A(_079_),
    .B(_084_),
    .Y(_085_));
 sky130_fd_sc_hd__xor2_1 _138_ (.A(_078_),
    .B(_085_),
    .X(_086_));
 sky130_fd_sc_hd__xnor2_1 _139_ (.A(_076_),
    .B(_086_),
    .Y(_104_));
 sky130_fd_sc_hd__maj3_2 _140_ (.A(_076_),
    .B(_078_),
    .C(_085_),
    .X(_087_));
 sky130_fd_sc_hd__maj3_1 _141_ (.A(_079_),
    .B(_082_),
    .C(_083_),
    .X(_088_));
 sky130_fd_sc_hd__nand2_1 _142_ (.A(b[2]),
    .B(a[3]),
    .Y(_089_));
 sky130_fd_sc_hd__a21oi_1 _143_ (.A1(a[2]),
    .A2(b[3]),
    .B1(_080_),
    .Y(_090_));
 sky130_fd_sc_hd__a21oi_1 _144_ (.A1(a[2]),
    .A2(_080_),
    .B1(_090_),
    .Y(_091_));
 sky130_fd_sc_hd__xnor2_1 _145_ (.A(_089_),
    .B(_091_),
    .Y(_092_));
 sky130_fd_sc_hd__nor2_1 _146_ (.A(_088_),
    .B(_092_),
    .Y(_093_));
 sky130_fd_sc_hd__nand2_1 _147_ (.A(_088_),
    .B(_092_),
    .Y(_094_));
 sky130_fd_sc_hd__nor2b_1 _148_ (.A(_093_),
    .B_N(_094_),
    .Y(_095_));
 sky130_fd_sc_hd__xnor2_1 _149_ (.A(_087_),
    .B(_095_),
    .Y(_105_));
 sky130_fd_sc_hd__o21a_1 _150_ (.A1(_087_),
    .A2(_093_),
    .B1(_094_),
    .X(_096_));
 sky130_fd_sc_hd__a2bb2oi_1 _151_ (.A1_N(_089_),
    .A2_N(_090_),
    .B1(a[2]),
    .B2(_080_),
    .Y(_097_));
 sky130_fd_sc_hd__nand3_1 _152_ (.A(b[3]),
    .B(a[3]),
    .C(_097_),
    .Y(_098_));
 sky130_fd_sc_hd__xor2_1 _153_ (.A(_096_),
    .B(_098_),
    .X(_106_));
 sky130_fd_sc_hd__nor3_1 _154_ (.A(_063_),
    .B(_067_),
    .C(_075_),
    .Y(_099_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _155_ (.A(_076_),
    .SLEEP(_099_),
    .X(_103_));
 sky130_fd_sc_hd__o21ai_0 _156_ (.A1(_096_),
    .A2(_098_),
    .B1(_097_),
    .Y(_107_));
 sky130_fd_sc_hd__fill_4 FILLER_0_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_8 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_14 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_20 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_34 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_38 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_42 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_54 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_62 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_66 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_70 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_74 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_8 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_12 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_27 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_29 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_53 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_57 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_61 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_65 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_69 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_53 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_57 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_61 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_65 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_69 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_36 ();
 sky130_fd_sc_hd__fill_2 FILLER_3_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_53 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_57 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_61 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_65 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_69 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_16 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_69 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_31 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_35 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_71 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_32 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_71 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_24 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_51 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_55 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_57 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_71 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_33 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_72 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_16 ();
 sky130_fd_sc_hd__fill_2 FILLER_9_20 ();
 sky130_fd_sc_hd__fill_1 FILLER_9_22 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_34 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_52 ();
 sky130_fd_sc_hd__fill_1 FILLER_9_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_71 ();
 sky130_fd_sc_hd__fill_2 FILLER_9_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_24 ();
 sky130_fd_sc_hd__fill_2 FILLER_10_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_72 ();
 sky130_fd_sc_hd__fill_1 FILLER_10_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_36 ();
 sky130_fd_sc_hd__fill_1 FILLER_11_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_52 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_60 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_72 ();
 sky130_fd_sc_hd__fill_1 FILLER_11_76 ();
 assign p[0] = _100_;
 assign p[1] = _101_;
 assign p[2] = _102_;
 assign p[3] = _103_;
 assign p[4] = _104_;
 assign p[5] = _105_;
 assign p[6] = _106_;
 assign p[7] = _107_;
endmodule
