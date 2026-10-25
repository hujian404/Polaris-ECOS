// ***************************************************************************************
// Copyright (c) 2023-2025 Peng Cheng Laboratory
// Copyright (c) 2023-2025 Institute of Computing Technology, Chinese Academy of Sciences
// Copyright (c) 2023-2025 Beijing Institute of Open Source Chip
//
// iEDA is licensed under Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
// http://license.coscl.org.cn/MulanPSL2
//
// THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
// EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
// MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
//
// See the Mulan PSL v2 for more details.
// ***************************************************************************************
// Focused connection model; not a native CTS integration test.
#include <algorithm>
#include <vector>
#include <cassert>
struct Pin;
struct Net { Pin* driver=nullptr; std::vector<Pin*> loads;
Pin* get_driver() const{return driver;} const std::vector<Pin*>& get_loads() const{return loads;}
void set_driver(Pin* p){driver=p;} void set_loads(const std::vector<Pin*>& v){loads=v;}
void add_load(Pin* p){if(p && std::find(loads.begin(),loads.end(),p)==loads.end())loads.push_back(p);}};
struct Pin { Net* net=nullptr; Net* get_net() const{return net;} void set_net(Net* n){net=n;}};
auto ConnectNet(Net& net, Pin* driver, const std::vector<Pin*>& loads) -> void
{
  auto* old_driver = net.get_driver();
  if (old_driver != nullptr && old_driver != driver && old_driver->get_net() == &net) {
    old_driver->set_net(nullptr);
  }

  for (auto* old_load : net.get_loads()) {
    if (old_load != nullptr && old_load->get_net() == &net) {
      old_load->set_net(nullptr);
    }
  }

  net.set_driver(driver);
  if (driver != nullptr) {
    driver->set_net(&net);
  }

  net.set_loads({});
  for (auto* load : loads) {
    if (load == nullptr) {
      continue;
    }
    net.add_load(load);
    load->set_net(&net);
  }
}

// The source net may already carry non-sink loads (e.g. a traced stage input); they
// must survive the reconnection, so only the sinks being taken over are replaced.
auto ConnectSourceNet(Net& net, Pin* driver, const std::vector<Pin*>& new_loads, Pin* replaced_sink = nullptr) -> void
{
  std::vector<Pin*> loads;
  loads.reserve(net.get_loads().size() + new_loads.size());
  for (auto* load : net.get_loads()) {
    if (load != nullptr && load != replaced_sink && load->get_net() == &net) {
      loads.push_back(load);
    }
  }
  loads.insert(loads.end(), new_loads.begin(), new_loads.end());
  ConnectNet(net, driver, loads);
}


int main(){
 Net clock,last; Pin source,root,other,buffer_in,buffer_out;
 ConnectNet(clock,&source,{&root,&other});
 ConnectSourceNet(clock,&source,{&buffer_in},&root);
 ConnectNet(last,&buffer_out,{&root});
 bool stale=std::find(clock.loads.begin(),clock.loads.end(),&root)!=clock.loads.end();
 assert(stale==false);
 assert(root.net==&last && buffer_in.net==&clock && other.net==&clock);
 assert(std::find(clock.loads.begin(),clock.loads.end(),&other)!=clock.loads.end());
 Net direct;Pin direct_source,direct_sink,ignored;
 ConnectNet(direct,&direct_source,{&direct_sink,&ignored});
 ConnectSourceNet(direct,&direct_source,{&direct_sink});
 assert(direct.loads.size()==2 && direct_sink.net==&direct && ignored.net==&direct);
}
