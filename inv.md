# interview

## Q&A

### 负载均衡

将服务压力分摊至各服务器，防止出现单点故障导致无法提供服务。

#### 策略

- 轮询：按照请求列表中的服务器挨个分配请求。
- 最小链接：优先选择链接数最少的服务器分配请求。
- IP_HASH：将请求源IP转换为hash并发往某个服务器，同一ip的请求都将分配至同一服务器。（nginx中的iphash策略不宜应用于当nginx为二层代理，此外负载也不均衡。）

## 网络

### ARP

链路层协议。实现ip->mac地址解析。

#### 过程

- c1广播发送(ffff.ffff.ffff)c2 mac地址arp请求(包含c1 ip、mac，c2 ip)，局域网内不是c2 ip的设备收到请求后不响应，c2接收请求后响应自身mac。
- c1收到c2 mac响应，缓存该mac与c2 ip信息至本地arp表。

### ip

提供面向无连接不可靠传输。

#### 默认字段

- version：协议版本。
- header length：头部长度。20-60byte
- differentiated servies field：服务区分符，标记数据包服务质量。
- total length：数据包总长度。
- identification：用于实现分片重组，标记属于哪个进程。
- flags：标记是否能分片和是否有分片。
- fragment offset：分片偏移量。
- ttl：分片生存时间。
- protocol：标记上层协议，1为icmp，17为udp，6为tcp。
- header checksum：用于校验分片是否完整或被修改过。
- source：源ip。
- destination：目的ip。

> 默认字段中  
> -- source、destination标记分片源目ip
> -- total length、header length标记头部和分片边界
> -- id、flags、fo标记分片组，实现数据包分片和重组
> -- ttl生存时间字段防止通信回环
> -- differentiated services field实现流量控制
> -- checksum实现完整性校验
> -- protocol标记上层应用

部分字段解释：

ttl：每经过一个路由器-1，当ttl=0时，路由器返回icmp错误数据包(ttl exceed)。


#### 其他字段 

### DHCP

UDP协议，用于为设备分配ip地址。

67、68、546分别为DHCP协议server、client、ipv6client端口。

#### 过程

- client ---DHCPDISCOVER(广播)--> 局域网内所有设备。在不清楚局域网内所有DHCP服务器地址时，通过广播发送discover报文，所有收到报文的DHCP服务器都会响应。
- DHCP服务器 ---DHCPOFFER--> client。DHCP服务器收到discover报文后向client发送的off报文，包含ip、租期和其他配置信息，此时ip为预分配ip。若不存在可分配ip，则发送DHCPNAK。
- client ---DHCPREQUEST--> DHCP服务器。收到offer报文后，向DHCP服务器发送request报文，请求使用ip。
- DHCP服务器 ---DHCPACK--> client。收到request报文后，发送ack，告知client可以使用，并将ip从ip池标记。(client会发送ARP请求该ip，若无响应则表明该ip可用)
- client ---DHCPRELEASE--> DHCP服务器。client不再使用分配的ip时发送。


## docker

容器化，对进程进行隔离。与虚拟化相比，虚拟化基于物理设备、操作系统模拟隔离，而容器在操作系统之上对进程隔离。

### 架构（自顶向下）

- docker client(例如docker cli，通过调用dockerd提供的rest api与dockerd交互，tcp或unix socket)
- dockerd(docker守护进程，提供tcp或unix socket接口（rest api）)
- containerd(容器运行时，实际上提供容器管理服务（容器生命周期）的进程，容器隔离的实现通过containerd（namespace、control group等等），提供grpc接口)
- shim(将运行中容器与daemon解耦（dockerd、containerd），维护容器stdin、stdout及文件描述符，反馈容器状态，提供grpc接口)
- runc(用于运行容器，生命周期仅存在于创建和运行，容器成功运行后结束，一个cli)

#### 各层级交互细节（TODO）

- runc在拉起容器时接收的参数主要是一个解压的容器的文件系统和一份定义容器状态配置的json（config.json），以上两个统称（OCI bundle）
- runc创建的容器状态存储在/run/runc
- runc在容器创建完成之前是容器的父进程，创建完成之后runc进程退出，由shim进程接管容器进程（stdin、stdout、容器状态），与containerd、dockerd解耦shim与容器进程
- shim进程是由containerd通过grpc调用的，runc进程是由shim直接调用runc包函数（？）
- 

### 功能

从资源隔离、资源限制、存储（文件系统、驱动、镜像、容器）和网络（模型、驱动）

#### 资源

主要指计算机cpu、内存、网络io、块io等资源。containerd对namespace和cgroups调用分别实现了容器资源的隔离和资源源限制。


##### 隔离

**namespace**抽象全局资源，在namespace中的进程感知拥有所有全局资源（即进程是操作系统唯一进程），全局资源的变化仅对相同namespace中的进程可见，对于其他namespace中的进程不可见。namespace提供了**mount（隔离文件系统挂载点）、uts（隔离hostname、domainname）、ipc（隔离进程间通信、POSIX消息队列（？））、pid（隔离进程ID）、network（隔离网络设备、堆栈、端口）、user（隔离用户用户组ID）、time（隔离引导时钟、单调（？）时钟）、cgroup（隔离cgroup根路径）**几种资源隔离机制，各自namespace标识符分别为**CLONE_NEWNS、CLONE_NEWUTS、CLONE_NEWIPC、CLONE_NEWPID、CLONE_NEWNET、CLONE_NEWUSER、CLONE_NEWTIME、CLONE_NEWCROUP**。

与namespace相关的系统调用`clone()`（创建新进程）、`unshare()`（调用进程被移动到新的namespace）、`setns()`（进程加入一个已存在的namespace）、`ioctl()`、`/proc/[pid]/ns（eg.？）`，在执行系统调用时传入**CLONE_**指定namespace。

###### 具体实现/应用（？）



##### 限制

**cgroups**为内核提供的将一系列task及其子task整合或分隔到按资源划分等级的不同的层级中，进行资源管理的框架。

主要作用：

- 资源限制：设定资源总额上限。
- 优先级分配：设定资源分配比例，cpu时间片、带宽等。
- 资源统计：统计资源使用量，cpu时间、内存总量、带宽总量。
- 任务控制：对task挂起恢复。

概念：

- task：进程或线程。linux内核调度管理不对进程线程区分，只有在clone时通过传入参数的不同进行概念区分。
- cgroup：cgroups对资源控制以cgroup为单位。cgroup是按不同资源分配标准划分的任务组，包含一个或多个subsystem。一个task可以在某个cgroup中，也可以迁移到另一个cgroup中。
- subsystem：资源调度控制器。
  - blkio：限制块设备IO
  - cpu：限制cpu访问（时间片分配？）
  - cpuacct：生成cgroup中task的cpu使用报告
  - cpuset：分配独立cpu和内存结点
  - devices：限制task访问设备
  - freezer：暂停或恢复task
  - hugetlb：限制内存页数量
  - memory：限制task可用内存并生成内存使用报告
  - net_cls：使用等级标识符（classid）标记网络数据包，使linux流量控制器识别特定数据包
- hierarchy：层级，一系列cgroup组合的树状结构。

规则（v1？）：
- 一个subsystem只能attach（附加？）在一个hierarchy
- 一个hierarchy可以有多个subsystem

#### 存储

##### 文件系统

##### 驱动

##### 镜像和容器

#### 网络

##### 模型

##### 驱动

