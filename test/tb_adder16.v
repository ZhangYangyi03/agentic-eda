module tb; reg [15:0] a,b; reg cin; wire [15:0] s; wire cout;
adder16 dut(.a(a),.b(b),.cin(cin),.s(s),.cout(cout));
integer i, fd;
initial begin
  fd = $fopen("/mnt/d/eda/test/sim_adder16.txt","w");
  for (i=0;i<1200;i=i+1) begin
    a = $random; b = $random; cin = $random;
    #1 $fwrite(fd, "%b %b %b %b %b\n", a, b, cin, s, cout);
  end
  $fclose(fd); $finish;
end
endmodule
