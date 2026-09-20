module lfsr16 (clk,
    rst,
    q);
 input clk;
 input rst;
 output [15:0] q;

 wire _05_;
 wire _06_;
 wire _07_;
 wire _08_;
 wire _09_;
 wire _10_;
 wire _11_;
 wire _12_;
 wire _13_;
 wire _14_;
 wire _15_;
 wire _16_;
 wire _17_;
 wire _18_;
 wire _19_;
 wire _20_;
 wire _21_;
 wire _22_;
 wire _23_;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__xor2_4 _41_ (.A(q[13]),
    .B(q[15]),
    .X(_21_));
 sky130_fd_sc_hd__xnor2_1 _42_ (.A(q[11]),
    .B(q[12]),
    .Y(_22_));
 sky130_fd_sc_hd__xnor3_1 _43_ (.A(q[10]),
    .B(_21_),
    .C(_22_),
    .X(_23_));
 sky130_fd_sc_hd__or2_0 _44_ (.A(rst),
    .B(_23_),
    .X(_05_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _45_ (.A(q[0]),
    .SLEEP(rst),
    .X(_12_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _46_ (.A(q[1]),
    .SLEEP(rst),
    .X(_13_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _47_ (.A(q[2]),
    .SLEEP(rst),
    .X(_14_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _48_ (.A(q[3]),
    .SLEEP(rst),
    .X(_15_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _49_ (.A(q[4]),
    .SLEEP(rst),
    .X(_16_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _50_ (.A(q[5]),
    .SLEEP(rst),
    .X(_17_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _51_ (.A(q[6]),
    .SLEEP(rst),
    .X(_18_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _52_ (.A(q[7]),
    .SLEEP(rst),
    .X(_19_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _53_ (.A(q[8]),
    .SLEEP(rst),
    .X(_20_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _54_ (.A(q[9]),
    .SLEEP(rst),
    .X(_06_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _55_ (.A(q[10]),
    .SLEEP(rst),
    .X(_07_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _56_ (.A(q[11]),
    .SLEEP(rst),
    .X(_08_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _57_ (.A(q[12]),
    .SLEEP(rst),
    .X(_09_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _58_ (.A(q[13]),
    .SLEEP(rst),
    .X(_10_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _59_ (.A(q[14]),
    .SLEEP(rst),
    .X(_11_));
 sky130_fd_sc_hd__dfxtp_1 _60_ (.CLK(clknet_1_1__leaf_clk),
    .D(_19_),
    .Q(q[8]));
 sky130_fd_sc_hd__dfxtp_1 _61_ (.CLK(clknet_1_1__leaf_clk),
    .D(_20_),
    .Q(q[9]));
 sky130_fd_sc_hd__dfxtp_1 _62_ (.CLK(clknet_1_1__leaf_clk),
    .D(_06_),
    .Q(q[10]));
 sky130_fd_sc_hd__dfxtp_1 _63_ (.CLK(clknet_1_0__leaf_clk),
    .D(_07_),
    .Q(q[11]));
 sky130_fd_sc_hd__dfxtp_1 _64_ (.CLK(clknet_1_0__leaf_clk),
    .D(_08_),
    .Q(q[12]));
 sky130_fd_sc_hd__dfxtp_1 _65_ (.CLK(clknet_1_1__leaf_clk),
    .D(_09_),
    .Q(q[13]));
 sky130_fd_sc_hd__dfxtp_1 _66_ (.CLK(clknet_1_1__leaf_clk),
    .D(_10_),
    .Q(q[14]));
 sky130_fd_sc_hd__dfxtp_1 _67_ (.CLK(clknet_1_1__leaf_clk),
    .D(_11_),
    .Q(q[15]));
 sky130_fd_sc_hd__dfxtp_1 _68_ (.CLK(clknet_1_1__leaf_clk),
    .D(_05_),
    .Q(q[0]));
 sky130_fd_sc_hd__dfxtp_1 _69_ (.CLK(clknet_1_0__leaf_clk),
    .D(_12_),
    .Q(q[1]));
 sky130_fd_sc_hd__dfxtp_1 _70_ (.CLK(clknet_1_0__leaf_clk),
    .D(_13_),
    .Q(q[2]));
 sky130_fd_sc_hd__dfxtp_1 _71_ (.CLK(clknet_1_0__leaf_clk),
    .D(_14_),
    .Q(q[3]));
 sky130_fd_sc_hd__dfxtp_1 _72_ (.CLK(clknet_1_0__leaf_clk),
    .D(_15_),
    .Q(q[4]));
 sky130_fd_sc_hd__dfxtp_1 _73_ (.CLK(clknet_1_0__leaf_clk),
    .D(_16_),
    .Q(q[5]));
 sky130_fd_sc_hd__dfxtp_1 _74_ (.CLK(clknet_1_1__leaf_clk),
    .D(_17_),
    .Q(q[6]));
 sky130_fd_sc_hd__dfxtp_1 _75_ (.CLK(clknet_1_1__leaf_clk),
    .D(_18_),
    .Q(q[7]));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
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
 sky130_fd_sc_hd__fill_4 FILLER_0_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_52 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_56 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_60 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_62 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_72 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_84 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_0 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_6 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_52 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_77 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_81 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_85 ();
 sky130_fd_sc_hd__fill_2 FILLER_2_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_2 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_19 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_23 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_43 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_51 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_71 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_79 ();
 sky130_fd_sc_hd__fill_2 FILLER_2_83 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_85 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_3_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_23 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_43 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_51 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_71 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_79 ();
 sky130_fd_sc_hd__fill_2 FILLER_3_83 ();
 sky130_fd_sc_hd__fill_1 FILLER_3_85 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_10 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_20 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_28 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_48 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_52 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_60 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_72 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_84 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_10 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_43 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_51 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_55 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_63 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_67 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_71 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_79 ();
 sky130_fd_sc_hd__fill_2 FILLER_5_83 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_85 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_13 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_17 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_21 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_25 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_29 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_41 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_45 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_53 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_57 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_61 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_65 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_69 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_73 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_77 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_81 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_85 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_24 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_30 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_34 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_53 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_57 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_59 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_7_84 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_0 ();
 sky130_fd_sc_hd__fill_2 FILLER_8_25 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_54 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_58 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_62 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_71 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_75 ();
 sky130_fd_sc_hd__fill_4 FILLER_8_79 ();
 sky130_fd_sc_hd__fill_2 FILLER_8_83 ();
 sky130_fd_sc_hd__fill_1 FILLER_8_85 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_0 ();
 sky130_fd_sc_hd__fill_2 FILLER_9_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_9_6 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_9_16 ();
 sky130_fd_sc_hd__fill_2 FILLER_9_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_40 ();
 sky130_fd_sc_hd__fill_1 FILLER_9_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_52 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_72 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_9_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_9_84 ();
 sky130_fd_sc_hd__fill_1 FILLER_10_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_17 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_21 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_25 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_29 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_41 ();
 sky130_fd_sc_hd__fill_2 FILLER_10_45 ();
 sky130_fd_sc_hd__fill_1 FILLER_10_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_66 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_70 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_74 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_78 ();
 sky130_fd_sc_hd__fill_4 FILLER_10_82 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_11_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_11_10 ();
 sky130_fd_sc_hd__fill_1 FILLER_11_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_45 ();
 sky130_fd_sc_hd__fill_2 FILLER_11_49 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_56 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_60 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_72 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_11_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_11_84 ();
 sky130_fd_sc_hd__fill_2 FILLER_12_0 ();
 sky130_fd_sc_hd__fill_1 FILLER_12_2 ();
 sky130_fd_sc_hd__fill_2 FILLER_12_19 ();
 sky130_fd_sc_hd__fill_1 FILLER_12_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_12_70 ();
 sky130_fd_sc_hd__fill_4 FILLER_12_74 ();
 sky130_fd_sc_hd__fill_4 FILLER_12_78 ();
 sky130_fd_sc_hd__fill_4 FILLER_12_82 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_13_17 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_23 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_39 ();
 sky130_fd_sc_hd__fill_1 FILLER_13_43 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_60 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_64 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_68 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_72 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_76 ();
 sky130_fd_sc_hd__fill_4 FILLER_13_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_13_84 ();
endmodule
