module barrel16(input [15:0] d, input [3:0] s, output [15:0] q);
  assign q = d << s;
endmodule
