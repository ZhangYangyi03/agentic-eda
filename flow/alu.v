
module alu(input clk, input rst, input [7:0] a, input [7:0] b, input [2:0] op,
           output reg [15:0] y);
  reg [15:0] r;
  always @(*) begin
    case (op)
      3'd0: r = a + b;
      3'd1: r = a - b;
      3'd2: r = a * b;
      3'd3: r = a & b;
      3'd4: r = a | b;
      3'd5: r = a ^ b;
      3'd6: r = {a[3:0], b[7:4]};
      default: r = {8'd0, a} << b[2:0];
    endcase
  end
  always @(posedge clk) if (rst) y <= 16'd0; else y <= r;
endmodule
