module arbiter16(input [15:0] req, output [15:0] gnt);
  wire [15:0] m;
  assign m = req & ~((req << 1) - 1'b1);
  assign gnt = m;
endmodule
