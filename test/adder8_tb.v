module tb; reg [7:0] a,b; reg cin; wire [7:0] s; wire cout;
adder8 dut(.a(a),.b(b),.cin(cin),.s(s),.cout(cout));
integer i, fd;
initial begin
  fd = $fopen("D:/eda/test/iverilog_out.txt","w");
  for (i=0;i<2000;i=i+1) begin
    a = $random; b = $random; cin = $random;
    #1 $fwrite(fd, "%d %d %d %d %d\n", a, b, cin, s, cout);
  end
  $fclose(fd); $finish;
end
endmodule
