#include "VPolaris.h"
#include "verilated.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
static uint64_t simulation_time = 0;
double sc_time_stamp() { return double(simulation_time); }

// RV64I: x1=1; x1+=2; x1+=4; x2=0x80000100; sd x1,0(x2); loop.
static const uint32_t program[] = {
  0x00100093, 0x00208093, 0x00408093, 0x80000137,
  0x10010113, 0x00113023, 0x0000006f, 0x00000013
};
static uint64_t load64(uint32_t addr) {
  uint32_t pos = (addr & ~7u) - 0x80000000u;
  if (pos+7 >= sizeof(program)) return 0x0000001300000013ULL;
  return (uint64_t(program[pos/4+1])<<32) | program[pos/4];
}
int main(int argc, char** argv) {
  Verilated::commandArgs(argc, argv);
  VPolaris d;
  d.clock = 0;
  d.reset = 0;
  d.io_mem_awready = 0;
  d.io_mem_wready = 0;
  d.io_mem_bvalid = 0;
  d.io_mem_bresp = 0;
  d.io_mem_bid = 0;
  d.io_mem_buser = 0;
  d.io_mem_arready = 0;
  d.io_mem_rvalid = 0;
  d.io_mem_rresp = 0;
  d.io_mem_rdata = 0;
  d.io_mem_rlast = 0;
  d.io_mem_rid = 0;
  d.io_mem_ruser = 0;
  d.io_mmio_awready = 0;
  d.io_mmio_wready = 0;
  d.io_mmio_bvalid = 0;
  d.io_mmio_bresp = 0;
  d.io_mmio_bid = 0;
  d.io_mmio_buser = 0;
  d.io_mmio_arready = 0;
  d.io_mmio_rvalid = 0;
  d.io_mmio_rresp = 0;
  d.io_mmio_rdata = 0;
  d.io_mmio_rlast = 0;
  d.io_mmio_rid = 0;
  d.io_mmio_ruser = 0;
  d.io_frontend_awvalid = 0;
  d.io_frontend_awaddr = 0;
  d.io_frontend_awprot = 0;
  d.io_frontend_awid = 0;
  d.io_frontend_awuser = 0;
  d.io_frontend_awlen = 0;
  d.io_frontend_awsize = 0;
  d.io_frontend_awburst = 0;
  d.io_frontend_awlock = 0;
  d.io_frontend_awcache = 0;
  d.io_frontend_awqos = 0;
  d.io_frontend_wvalid = 0;
  d.io_frontend_wdata = 0;
  d.io_frontend_wstrb = 0;
  d.io_frontend_wlast = 0;
  d.io_frontend_bready = 0;
  d.io_frontend_arvalid = 0;
  d.io_frontend_araddr = 0;
  d.io_frontend_arprot = 0;
  d.io_frontend_arid = 0;
  d.io_frontend_aruser = 0;
  d.io_frontend_arlen = 0;
  d.io_frontend_arsize = 0;
  d.io_frontend_arburst = 0;
  d.io_frontend_arlock = 0;
  d.io_frontend_arcache = 0;
  d.io_frontend_arqos = 0;
  d.io_frontend_rready = 0;
  d.io_meip = 0;
  const unsigned stall = argc>1 ? unsigned(std::atoi(argv[1])) : 0;
  unsigned read_delay=0;
  bool rp=false, wp=false, bp=false, pass=false;
  uint32_t ra=0, wa=0; unsigned beats=0, sz=3, rid=0, wid=0;
  unsigned reads=0, writes=0, retired=0;
  for (unsigned cycle=0; cycle<20000; ++cycle) {
    simulation_time = uint64_t(cycle)*2;
    d.clock=0; d.reset=(cycle<16);
    d.io_mem_arready=!rp && !d.reset && (!stall || cycle%(stall+1)==0);
    d.io_mem_rvalid=rp && !read_delay; d.io_mem_rdata=load64(ra);
    d.io_mem_rresp=0; d.io_mem_rlast=rp && beats==1; d.io_mem_rid=rid;
    d.io_mem_awready=!wp && !bp && !d.reset;
    d.io_mem_wready=wp && !bp && (!stall || cycle%(stall+1)==0);
    d.io_mem_bvalid=bp; d.io_mem_bresp=0; d.io_mem_bid=wid;
    d.io_mmio_arready=1; d.io_mmio_awready=1; d.io_mmio_wready=1;
    d.eval();
    bool ar=d.io_mem_arvalid && d.io_mem_arready;
    bool r=d.io_mem_rvalid && d.io_mem_rready;
    bool aw=d.io_mem_awvalid && d.io_mem_awready;
    bool w=d.io_mem_wvalid && d.io_mem_wready;
    bool b=d.io_mem_bvalid && d.io_mem_bready;
    uint32_t na=d.io_mem_araddr, nwa=d.io_mem_awaddr;
    unsigned nb=d.io_mem_arlen+1, ns=d.io_mem_arsize, ni=d.io_mem_arid, nwi=d.io_mem_awid;
    uint64_t data=d.io_mem_wdata; unsigned strb=d.io_mem_wstrb;
    bool last=d.io_mem_wlast;
    if (d.io_ila_WBUvalid) ++retired;
    d.clock=1; d.eval();
    if (read_delay) --read_delay;
    if (r) { if (--beats==0) rp=false; else ra += 1u<<sz; }
    if (ar) { rp=true; ra=na; beats=nb; sz=ns; rid=ni; read_delay=stall; ++reads; }
    if (b) { bp=false; wp=false; }
    if (aw) { wp=true; wa=nwa; wid=nwi; }
    if (w) {
      ++writes;
      std::printf("STORE cycle=%u address=%08x data=%016llx strobe=%02x\n",
        cycle,wa,(unsigned long long)data,strb);
      if (wa==0x80000100u && data==7 && strb==0xff) pass=true;
      if (last) bp=true;
      wa+=8;
    }
    if (pass && !bp && !wp) {
      std::printf("PASS RV64 dependency/add/store smoke test: cycles=%u reads=%u writes=%u observed_wb=%u stall=%u\n",cycle,reads,writes,retired,stall);
      d.final(); return 0;
    }
  }
  std::fprintf(stderr,"FAIL timeout: reads=%u writes=%u observed_wb=%u pc=%llx\n",reads,writes,retired,(unsigned long long)d.io_ila_WBUpc);
  d.final(); return 1;
}
