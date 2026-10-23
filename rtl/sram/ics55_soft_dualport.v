// Genuine synthesizable 1R1W storage for the two incompatible macro interfaces.
// This preserves simultaneous independent read/write ports, at a flop area cost.
// It is not an SRAM blackbox, dummy output or a claim of a dual-port hard macro.
module MEM_0_ext(input [6:0] R0_addr,input R0_en,R0_clk,output reg [83:0] R0_data,
  input [6:0] W0_addr,input W0_en,W0_clk,input [83:0] W0_data,input [3:0] W0_mask);
  reg [83:0] memory[0:127];
  always @(posedge R0_clk) if(R0_en) R0_data<=memory[R0_addr];
  genvar lane;
  generate for(lane=0;lane<4;lane=lane+1) begin: masked_write
    always @(posedge W0_clk) if(W0_en && W0_mask[lane])
      memory[W0_addr][lane*21+:21]<=W0_data[lane*21+:21];
  end endgenerate
endmodule
module MEM_1_ext(input [7:0] R0_addr,input R0_en,R0_clk,output reg [255:0] R0_data,
  input [7:0] W0_addr,input W0_en,W0_clk,input [255:0] W0_data,input [3:0] W0_mask);
  reg [255:0] memory[0:255];
  always @(posedge R0_clk) if(R0_en) R0_data<=memory[R0_addr];
  genvar lane;
  generate for(lane=0;lane<4;lane=lane+1) begin: masked_write
    always @(posedge W0_clk) if(W0_en && W0_mask[lane])
      memory[W0_addr][lane*64+:64]<=W0_data[lane*64+:64];
  end endgenerate
endmodule
