module adder8 (cout,
    cin,
    a,
    b,
    s);
 output cout;
 input cin;
 input [7:0] a;
 input [7:0] b;
 output [7:0] s;

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

 sky130_fd_sc_hd__maj3_2 _077_ (.A(a[0]),
    .B(b[0]),
    .C(cin),
    .X(_054_));
 sky130_fd_sc_hd__maj3_2 _078_ (.A(a[1]),
    .B(b[1]),
    .C(_054_),
    .X(_055_));
 sky130_fd_sc_hd__maj3_2 _079_ (.A(a[2]),
    .B(b[2]),
    .C(_055_),
    .X(_056_));
 sky130_fd_sc_hd__maj3_2 _080_ (.A(a[3]),
    .B(b[3]),
    .C(_056_),
    .X(_057_));
 sky130_fd_sc_hd__maj3_2 _081_ (.A(a[4]),
    .B(b[4]),
    .C(_057_),
    .X(_058_));
 sky130_fd_sc_hd__maj3_2 _082_ (.A(a[5]),
    .B(b[5]),
    .C(_058_),
    .X(_059_));
 sky130_fd_sc_hd__maj3_2 _083_ (.A(a[6]),
    .B(b[6]),
    .C(_059_),
    .X(_060_));
 sky130_fd_sc_hd__maj3_1 _084_ (.A(a[7]),
    .B(b[7]),
    .C(_060_),
    .X(_053_));
 sky130_fd_sc_hd__xnor2_1 _085_ (.A(a[0]),
    .B(b[0]),
    .Y(_061_));
 sky130_fd_sc_hd__xnor2_1 _086_ (.A(cin),
    .B(_061_),
    .Y(_069_));
 sky130_fd_sc_hd__xnor2_1 _087_ (.A(a[1]),
    .B(b[1]),
    .Y(_062_));
 sky130_fd_sc_hd__xnor2_1 _088_ (.A(_054_),
    .B(_062_),
    .Y(_070_));
 sky130_fd_sc_hd__xnor2_1 _089_ (.A(a[2]),
    .B(b[2]),
    .Y(_063_));
 sky130_fd_sc_hd__xnor2_1 _090_ (.A(_055_),
    .B(_063_),
    .Y(_071_));
 sky130_fd_sc_hd__xnor2_1 _091_ (.A(a[3]),
    .B(b[3]),
    .Y(_064_));
 sky130_fd_sc_hd__xnor2_1 _092_ (.A(_056_),
    .B(_064_),
    .Y(_072_));
 sky130_fd_sc_hd__xnor2_1 _093_ (.A(a[4]),
    .B(b[4]),
    .Y(_065_));
 sky130_fd_sc_hd__xnor2_1 _094_ (.A(_057_),
    .B(_065_),
    .Y(_073_));
 sky130_fd_sc_hd__xnor2_1 _095_ (.A(a[5]),
    .B(b[5]),
    .Y(_066_));
 sky130_fd_sc_hd__xnor2_1 _096_ (.A(_058_),
    .B(_066_),
    .Y(_074_));
 sky130_fd_sc_hd__xnor2_1 _097_ (.A(a[6]),
    .B(b[6]),
    .Y(_067_));
 sky130_fd_sc_hd__xnor2_1 _098_ (.A(_067_),
    .B(_059_),
    .Y(_075_));
 sky130_fd_sc_hd__xnor2_1 _099_ (.A(a[7]),
    .B(b[7]),
    .Y(_068_));
 sky130_fd_sc_hd__xnor2_1 _100_ (.A(_060_),
    .B(_068_),
    .Y(_076_));
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
 sky130_fd_sc_hd__fill_1 FILLER_0_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_52 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_56 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_36 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_56 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_24 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_52 ();
 sky130_fd_sc_hd__fill_2 FILLER_2_56 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_24 ();
 sky130_fd_sc_hd__fill_2 FILLER_3_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_3_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_10 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_18 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_22 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_26 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_34 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_38 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_42 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_0 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_22 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_26 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_30 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_34 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_10 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_19 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_28 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_51 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_12 ();
 sky130_fd_sc_hd__fill_2 FILLER_8_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_50 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_58 ();
 assign cout = _053_;
 assign s[0] = _069_;
 assign s[1] = _070_;
 assign s[2] = _071_;
 assign s[3] = _072_;
 assign s[4] = _073_;
 assign s[5] = _074_;
 assign s[6] = _075_;
 assign s[7] = _076_;
endmodule
