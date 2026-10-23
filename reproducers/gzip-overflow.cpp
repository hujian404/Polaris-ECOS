// Minimal reproduction of the bundled Yosys gzip ostream buffering pattern.
// Compare kernel/gzip.{h,cc}, commit 13b43f8c85ec430a33ee55d058fb4c32b42b6910.
#include <zlib.h>
#include <sstream>
#include <iostream>
#include <string>
#include <filesystem>
#include <cstdint>
#include <algorithm>

struct Buffer : std::stringbuf {
  char initial[4096];
  gzFile file;
  Buffer(const char* path) : file(gzopen(path,"wb1")) { setp(initial,initial+4095); }
  int sync() override {
    auto actual=pptr()-pbase();
    int count=actual;
    std::cout<<"buffer_bytes="<<actual<<" narrowed_int="<<count<<"\n";
    if(count>0) {
      if(gzwrite(file,pbase(),count)!=count)return -1;
      pbump(-count);
    }
    return 0;
  }
  ~Buffer() override { sync();gzclose(file); }
};
static void emit(const char* path,uint64_t bytes,bool flush_chunks) {
  const std::string block(1024*1024,'x');
  {
    Buffer buffer(path);
    std::ostream out(&buffer);
    for(uint64_t n=0;n<bytes;) {
      auto count=std::min<uint64_t>(block.size(),bytes-n);
      out.write(block.data(),count);
      if(flush_chunks)out.flush();
      n+=count;
    }
    std::cout<<"ostream_good="<<out.good()<<" requested_bytes="<<bytes<<"\n";
  }
  std::cout<<path<<" gzip_bytes="<<std::filesystem::file_size(path)<<"\n";
}
int main() {
  std::cout<<"zlib="<<zlibVersion()<<"\n";
  emit("small.gz",65536,false);
  emit("large-broken.gz",uint64_t(2147483648)+4096,false);
  emit("large-chunked.gz",uint64_t(2147483648)+4096,true);
}
