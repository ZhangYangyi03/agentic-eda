module lfsr16(input clk, input rst, output reg [15:0] q);
  always @(posedge clk) begin
    if (rst) q <= 16'd1;
    else begin
      q <= {q[14:0], 1'b0} | ^{q[10], q[11], q[12], q[13], q[15]};
    end
  end
endmodule
