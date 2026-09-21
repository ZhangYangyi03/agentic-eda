module tb; reg [7:0] a,b; reg cin; wire [7:0] s; wire cout;
adder8 dut(.a(a),.b(b),.cin(cin),.s(s),.cout(cout));
integer i, fd;
initial begin
  fd = $fopen("/mnt/d/eda/test/sim_adder8.txt","w");
  for (i=0;i<1200;i=i+1) begin
    a = $random; b = $random; cin = $random;
    #1 $fwrite(fd, "%b %b %b %b %b\n", a, b, cin, s, cout);
  end
  $fclose(fd); $finish;
end
endmodule
