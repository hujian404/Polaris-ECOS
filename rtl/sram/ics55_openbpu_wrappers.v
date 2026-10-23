// Real ICS55 hard macro instances for the three compatible 1RW interfaces.
// MEM_0_ext and MEM_1_ext require independent R/W ports and are NOT stubbed.
`timescale 1ns/1ps
module MEM_ext(input [6:0] RW0_addr,input RW0_en,RW0_clk,RW0_wmode,
               input [73:0] RW0_wdata,output [73:0] RW0_rdata);
  ics55_ecos_sram_128x74_m4 macro_mem(.A(RW0_addr),.D(RW0_wdata),
    .Q(RW0_rdata),.CLK(RW0_clk),.CEB(~RW0_en),.GWEB(~RW0_wmode),
    .WEB(74'b0),.MARE(1'b0),.MAR(4'b0));
endmodule

module MEM_2_ext(input [8:0] RW0_addr,input RW0_en,RW0_clk,RW0_wmode,
  input [75:0] RW0_wdata,output [75:0] RW0_rdata,input [3:0] RW0_wmask);
  wire [75:0] web={{19{~RW0_wmask[3]}},{19{~RW0_wmask[2]}},
                  {19{~RW0_wmask[1]}},{19{~RW0_wmask[0]}}};
  ics55_ecos_sram_512x76_m4 macro_mem(.A(RW0_addr),.D(RW0_wdata),
    .Q(RW0_rdata),.CLK(RW0_clk),.CEB(~RW0_en),.GWEB(~RW0_wmode),
    .WEB(web),.MARE(1'b0),.MAR(4'b0));
endmodule

module MEM_3_ext(input [11:0] RW0_addr,input RW0_en,RW0_clk,RW0_wmode,
  input [255:0] RW0_wdata,output [255:0] RW0_rdata,input [3:0] RW0_wmask);
  genvar lane;
  generate for(lane=0;lane<4;lane=lane+1) begin: bank
    ics55_ecos_sram_4096x64_m4 macro_mem(.A(RW0_addr),
      .D(RW0_wdata[lane*64+:64]),.Q(RW0_rdata[lane*64+:64]),
      .CLK(RW0_clk),.CEB(~RW0_en),.GWEB(~RW0_wmode),
      .WEB({64{~RW0_wmask[lane]}}),.MARE(1'b0),.MAR(4'b0));
  end endgenerate
endmodule
