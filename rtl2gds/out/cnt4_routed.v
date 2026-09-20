module cnt4 (clk,
    rst_n,
    q);
 input clk;
 input rst_n;
 output [3:0] q;

 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;
 wire _08_;
 wire clknet_0_clk;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf_clk;

 sky130_fd_sc_hd__nand3_4 _13_ (.A(q[0]),
    .B(q[1]),
    .C(q[2]),
    .Y(_08_));
 sky130_fd_sc_hd__a21oi_1 _14_ (.A1(q[0]),
    .A2(q[1]),
    .B1(q[2]),
    .Y(_07_));
 sky130_fd_sc_hd__lpflow_isobufsrc_1 _15_ (.A(_08_),
    .SLEEP(_07_),
    .X(_05_));
 sky130_fd_sc_hd__xnor2_1 _16_ (.A(q[3]),
    .B(_08_),
    .Y(_06_));
 sky130_fd_sc_hd__inv_1 _17_ (.A(q[0]),
    .Y(_03_));
 sky130_fd_sc_hd__xor2_1 _18_ (.A(q[0]),
    .B(q[1]),
    .X(_04_));
 sky130_fd_sc_hd__dfrtp_1 _19_ (.CLK(clknet_1_0__leaf_clk),
    .D(_03_),
    .RESET_B(rst_n),
    .Q(q[0]));
 sky130_fd_sc_hd__dfrtp_1 _20_ (.CLK(clknet_1_0__leaf_clk),
    .D(_04_),
    .RESET_B(rst_n),
    .Q(q[1]));
 sky130_fd_sc_hd__dfrtp_1 _21_ (.CLK(clknet_1_1__leaf_clk),
    .D(_05_),
    .RESET_B(rst_n),
    .Q(q[2]));
 sky130_fd_sc_hd__dfrtp_1 _22_ (.CLK(clknet_1_1__leaf_clk),
    .D(_06_),
    .RESET_B(rst_n),
    .Q(q[3]));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_4 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__fill_4 FILLER_0_6 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_10 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_14 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_18 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_22 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_26 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_30 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_34 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_38 ();
 sky130_fd_sc_hd__fill_4 FILLER_0_42 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_46 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_4 ();
 sky130_fd_sc_hd__fill_2 FILLER_1_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_10 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_1_43 ();
 sky130_fd_sc_hd__fill_1 FILLER_1_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_4 ();
 sky130_fd_sc_hd__fill_1 FILLER_2_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_32 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_36 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_40 ();
 sky130_fd_sc_hd__fill_4 FILLER_2_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_19 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_23 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_3_43 ();
 sky130_fd_sc_hd__fill_1 FILLER_3_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_4_8 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_4_14 ();
 sky130_fd_sc_hd__fill_2 FILLER_4_26 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_8 ();
 sky130_fd_sc_hd__fill_1 FILLER_5_12 ();
 sky130_fd_sc_hd__fill_4 FILLER_5_44 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_12 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_16 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_18 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_33 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_37 ();
 sky130_fd_sc_hd__fill_4 FILLER_6_41 ();
 sky130_fd_sc_hd__fill_2 FILLER_6_45 ();
 sky130_fd_sc_hd__fill_1 FILLER_6_47 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_0 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_4 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_8 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_16 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_23 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_27 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_31 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_35 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_39 ();
 sky130_fd_sc_hd__fill_4 FILLER_7_43 ();
 sky130_fd_sc_hd__fill_1 FILLER_7_47 ();
endmodule
