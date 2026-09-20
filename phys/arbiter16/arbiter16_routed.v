module arbiter16 (gnt,
    req);
 output [15:0] gnt;
 input [15:0] req;

 wire _047_;
 wire _048_;
 wire _049_;
 wire _050_;
 wire _051_;
 wire _052_;
 wire _053_;
 wire _054_;
 wire _055_;
 wire _056_;
 wire _057_;
 wire _058_;
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
 wire zero_;

 sky130_fd_sc_hd__and2_0 _096_ (.A(req[1]),
    .B(req[0]),
    .X(_053_));
 sky130_fd_sc_hd__o21ai_0 _097_ (.A1(req[1]),
    .A2(req[0]),
    .B1(req[2]),
    .Y(_062_));
 sky130_fd_sc_hd__nor2_1 _098_ (.A(_053_),
    .B(_062_),
    .Y(_054_));
 sky130_fd_sc_hd__or3_1 _099_ (.A(req[1]),
    .B(req[0]),
    .C(req[2]),
    .X(_063_));
 sky130_fd_sc_hd__and3_1 _100_ (.A(req[3]),
    .B(_062_),
    .C(_063_),
    .X(_055_));
 sky130_fd_sc_hd__or4_4 _101_ (.A(req[1]),
    .B(req[0]),
    .C(req[2]),
    .D(req[3]),
    .X(_064_));
 sky130_fd_sc_hd__nand2_1 _102_ (.A(req[4]),
    .B(_064_),
    .Y(_065_));
 sky130_fd_sc_hd__a21oi_1 _103_ (.A1(req[3]),
    .A2(_063_),
    .B1(_065_),
    .Y(_056_));
 sky130_fd_sc_hd__or2_2 _104_ (.A(req[4]),
    .B(_064_),
    .X(_066_));
 sky130_fd_sc_hd__and3_1 _105_ (.A(req[5]),
    .B(_065_),
    .C(_066_),
    .X(_057_));
 sky130_fd_sc_hd__o21ai_0 _106_ (.A1(req[5]),
    .A2(_066_),
    .B1(req[6]),
    .Y(_067_));
 sky130_fd_sc_hd__a21oi_1 _107_ (.A1(req[5]),
    .A2(_066_),
    .B1(_067_),
    .Y(_058_));
 sky130_fd_sc_hd__nor4_4 _108_ (.A(req[4]),
    .B(req[5]),
    .C(req[6]),
    .D(_064_),
    .Y(_068_));
 sky130_fd_sc_hd__nand2b_1 _109_ (.A_N(_068_),
    .B(req[7]),
    .Y(_069_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _110_ (.A(_067_),
    .SLEEP(_069_),
    .X(_059_));
 sky130_fd_sc_hd__or2b_1 _111_ (.A(req[7]),
    .B_N(_068_),
    .X(_070_));
 sky130_fd_sc_hd__and3_1 _112_ (.A(req[8]),
    .B(_069_),
    .C(_070_),
    .X(_060_));
 sky130_fd_sc_hd__or2_2 _113_ (.A(req[8]),
    .B(_070_),
    .X(_071_));
 sky130_fd_sc_hd__nand2_1 _114_ (.A(req[9]),
    .B(_071_),
    .Y(_072_));
 sky130_fd_sc_hd__a21oi_1 _115_ (.A1(req[8]),
    .A2(_070_),
    .B1(_072_),
    .Y(_061_));
 sky130_fd_sc_hd__or4b_1 _116_ (.A(req[7]),
    .B(req[8]),
    .C(req[9]),
    .D_N(_068_),
    .X(_073_));
 sky130_fd_sc_hd__nand2_1 _117_ (.A(req[10]),
    .B(_073_),
    .Y(_074_));
 sky130_fd_sc_hd__a21oi_1 _118_ (.A1(req[9]),
    .A2(_071_),
    .B1(_074_),
    .Y(_047_));
 sky130_fd_sc_hd__or2_2 _119_ (.A(req[10]),
    .B(_073_),
    .X(_075_));
 sky130_fd_sc_hd__and3_1 _120_ (.A(req[11]),
    .B(_074_),
    .C(_075_),
    .X(_048_));
 sky130_fd_sc_hd__o21ai_0 _121_ (.A1(req[11]),
    .A2(_075_),
    .B1(req[12]),
    .Y(_076_));
 sky130_fd_sc_hd__a21oi_1 _122_ (.A1(req[11]),
    .A2(_075_),
    .B1(_076_),
    .Y(_049_));
 sky130_fd_sc_hd__or4_4 _123_ (.A(req[10]),
    .B(req[11]),
    .C(req[12]),
    .D(_073_),
    .X(_077_));
 sky130_fd_sc_hd__and3_1 _124_ (.A(req[13]),
    .B(_076_),
    .C(_077_),
    .X(_050_));
 sky130_fd_sc_hd__o21ai_0 _125_ (.A1(req[13]),
    .A2(_077_),
    .B1(req[14]),
    .Y(_078_));
 sky130_fd_sc_hd__a21oi_1 _126_ (.A1(req[13]),
    .A2(_077_),
    .B1(_078_),
    .Y(_051_));
 sky130_fd_sc_hd__or3_1 _127_ (.A(req[13]),
    .B(req[14]),
    .C(_077_),
    .X(_079_));
 sky130_fd_sc_hd__and3_1 _128_ (.A(req[15]),
    .B(_078_),
    .C(_079_),
    .X(_052_));
 sky130_fd_sc_hd__fill_4 FILLER_0_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_53 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_32 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_36 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_36 ();
 sky130_fd_sc_hd__fill_2 FILLER_2_40 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_42 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_51 ();
 sky130_fd_sc_hd__fill_2 FILLER_2_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_52 ();
 sky130_fd_sc_hd__fill_1 FILLER_3_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_0 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_6 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_21 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_25 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_29 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_53 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_2 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_17 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_30 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_36 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_38 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_42 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_50 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_51 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_55 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_38 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_42 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_50 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_17 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_21 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_25 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_29 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_53 ();
 assign gnt[10] = _047_;
 assign gnt[11] = _048_;
 assign gnt[12] = _049_;
 assign gnt[13] = _050_;
 assign gnt[14] = _051_;
 assign gnt[15] = _052_;
 assign gnt[1] = _053_;
 assign gnt[2] = _054_;
 assign gnt[3] = _055_;
 assign gnt[4] = _056_;
 assign gnt[5] = _057_;
 assign gnt[6] = _058_;
 assign gnt[7] = _059_;
 assign gnt[8] = _060_;
 assign gnt[9] = _061_;
 assign gnt[0] = zero_;
endmodule
