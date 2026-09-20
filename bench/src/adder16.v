module adder16(input [15:0] a, input [15:0] b, input cin, output [15:0] s, output cout);
  assign {cout, s} = a + b + cin;
endmodule
