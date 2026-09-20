module prio32(input [31:0] x, output [31:0] y, output v);
  assign v = |x;
  assign y = x & (~x + 1'b1);
endmodule
