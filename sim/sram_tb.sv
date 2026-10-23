`timescale 1ns/1ps
module memory_case #(parameter WIDTH=74,DEPTH=128,LANES=1,ADDR=7)
  (output reg done=0);
  reg clk=0,en=0,wr=0;
  reg [ADDR-1:0] addr;
  reg [WIDTH-1:0] data;
  reg [LANES-1:0] mask;
  wire [WIDTH-1:0] q;
  reg [WIDTH-1:0] reference[0:DEPTH-1];
  integer checks=0,cycles=0;
  reg [31:0] seed=32'h8baf3019+WIDTH;
  always #5 clk=~clk;
  generate if(WIDTH==74) begin
    MEM_ext dut(addr,en,clk,wr,data,q);
  end else if(WIDTH==76) begin
    MEM_2_ext dut(addr,en,clk,wr,data,q,mask);
  end else begin
    MEM_3_ext dut(addr,en,clk,wr,data,q,mask);
  end endgenerate
  function automatic [31:0] random_word();
    seed=seed^(seed<<13); seed=seed^(seed>>17); seed=seed^(seed<<5);
    return seed;
  endfunction
  task automatic transact(input bit enabled,input bit write_mode,
    input integer address,input [WIDTH-1:0] value,input [LANES-1:0] lane_mask);
    reg [WIDTH-1:0] before_q;
    @(negedge clk);
    before_q=q; en=enabled;wr=write_mode;addr=address;data=value;mask=lane_mask;
    if(enabled && write_mode)
      for(integer l=0;l<LANES;l=l+1)
        if(lane_mask[l] || WIDTH==74) reference[address][l*(WIDTH/LANES)+:(WIDTH/LANES)]=value[l*(WIDTH/LANES)+:(WIDTH/LANES)];
    @(posedge clk); #2;
    cycles=cycles+1;
    if(enabled && !write_mode) begin
      checks=checks+1;
      if(q !== reference[address])
        $fatal(1,"READ mismatch width=%0d address=%0d expected=%h got=%h",WIDTH,address,reference[address],q);
    end
    if(!enabled) begin
      checks=checks+1;
      if(q !== before_q) $fatal(1,"disabled SRAM toggled width=%0d",WIDTH);
    end
  endtask
  reg [WIDTH-1:0] value;
  reg [31:0] control;
  initial begin
    // Initialize every address, then test the complete address range.
    for(integer a=0;a<DEPTH;a=a+1) begin
      for(integer b=0;b<WIDTH;b=b+1) value[b]=(a*17+b*13) % 7 < 3;
      transact(1,1,a,value,{LANES{1'b1}});
    end
    for(integer a=0;a<DEPTH;a=a+1) transact(1,0,a,'0,'0);
    // Deterministic partial writes (including zero mask), reads and disabled cycles.
    for(integer i=0;i<6000;i=i+1) begin
      for(integer b=0;b<WIDTH;b=b+1) value[b]=random_word() & 1;
      control=random_word();
      transact(control[2:0]!=0,control[3],control[31:16]%DEPTH,value,control[7+:LANES]);
    end
    for(integer a=0;a<DEPTH;a=a+1) transact(1,0,a,'0,'0);
    $display("PASS ICS55 wrapper width=%0d depth=%0d cycles=%0d checks=%0d",WIDTH,DEPTH,cycles,checks);
    done=1;
  end
endmodule
module sram_tb;
  wire a,b,c;
  memory_case #(.WIDTH(74),.DEPTH(128),.LANES(1),.ADDR(7)) m0(a);
  memory_case #(.WIDTH(76),.DEPTH(512),.LANES(4),.ADDR(9)) m2(b);
  memory_case #(.WIDTH(256),.DEPTH(4096),.LANES(4),.ADDR(12)) m3(c);
  initial begin wait(a && b && c); $display("PASS all three real SRAM macro interfaces"); $finish; end
  initial begin #1000000; $fatal(1,"timeout"); end
endmodule
