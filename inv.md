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

**概念：**

- task：进程或线程。linux内核调度管理不对进程线程区分，只有在clone时通过传入参数的不同进行概念区分。
- cgroup：cgroups对资源控制以cgroup为单位。cgroup是按不同资源分配标准划分的任务组，包含一个或多个subsystem。一个task可以在某个cgroup中，也可以迁移到另一个cgroup中。
- subsystem：资源调度控制器。
  - blkio：限制块设备IO
  - cpu：限制cpu访问（时间片分配？）
  - cpuacct：生成cgroup中task的cpu使用报告
  - cpuset：分配独立cpu和内存节点
  - devices：限制task访问设备
  - freezer：暂停或恢复task
  - hugetlb：限制内存页数量
  - memory：限制task可用内存并生成内存使用报告
  - net_cls：使用等级标识符（classid）标记网络数据包，使linux流量控制器识别特定数据包
- hierarchy：层级，一系列cgroup组合的树状结构。

**规则（v1？）：**

- 一个subsystem只能attach（附加？）在一个hierarchy
- 一个hierarchy可以有多个subsystem
- 一个task可以在多个cgroup中，但不能是同一hierarchy的cgroup，即同一task不能有多个相同资源的限制。
- 子task默认在父task的cgroup中，可以移动到其他cgroup
- 当创建了新的cgroup时，默认会将系统中所有进程添加至该cgroups中的root节点

**如何实现（提供用户接口）：**

cgroups通过linux的VFS（虚拟文件系统，TODO）提供用户接口，作为一种文件系统，启动后默认挂载至/sys/fs/cgroup（使用systemd的系统）。

**如何操作：**

可以直接echo > /sys/fs/cgroup下各subsystem中的配置参数？不太安全
systemd

**关于v1和v2的区别：**

v1：为每个subsystem创建一个hierarchy，再在下创建cgroup
v2：以cgroup为主导，有一个unified hierarchy，在cgroup中有subsystem

**hierarchy、cgroup、subsystem、slice、scope、service的关系：**

slice、scope、service是systemd创建的unit类型，为cgroup树提供同一层级结构（systemd待补充，TODO）。

service：指由systemd创建的一个或一组进程（举例来说*.service文件配置的服务）。
scope：指一组由非systemd创建的进程（例如用户会话、容器、虚拟机）。
slice：指一组按层级排列的unit，不包含进程，但会组件一个层级，将service和scope放入其中。

以下内容为个人理解。

cgroups需要实现对task或task组实现根据资源限制标准分组或整合，则将cgroups功能分为层级结构（为进程分组）、资源限制（控制进程资源）。

systemd会在系统启动后默认创建systemd.slice（所有系统service）、user.slice（所有用户会话）、machine.slice（所有虚拟机Linux容器）、-.slice（根slice）。在这里完成对cgroups功能中层级结构的实现，不同的进程按照性质加入到不同的slice中（service或scope）。

cgroups文件系统挂载至/sys/fs/cgroup，在该目录下包含所有可用的subsystem（controller?），各subsystem下会有上面根据slice-scope、service创建好的层级结构，在这里对不同service或slice进行subsystem的配置。实现层级结构与资源控制解耦。

粗浅理解为
- hierarchy对应-.slice（顶级，整体的hierarchy，而不是根据具体的被配置了cgroup和subsystem的hierarchy），也可以是root cgroup对应-.slice？
- \*.slice、scope、service对应子cgroup，当然各个\*.slice、scope、service的子cgroup逻辑上与所有subsystem有关。
- task对应真正进程。


#### 存储

docker支持的几种存储驱动或文件系统的描述以及由镜像到容器的存储过程。

##### 机制

**COW copy on write**

在进行写操作时，才进行复制。
对于进程而言，父进程在创建子进程（fork()）后，父子进程共享的是相同的只读地址空间（子进程独立虚页地址，父进程创建子进程时仅付出创建子进程描述符和父进程页表的代价），而当有写操作时，复制内存页，此时父子进程内存页各自独立（代码段还是共享）。
对于文件系统，在进行写操作时，不在原数据位置操作，写操作完成后覆盖原数据。

**分层**

镜像是由多层镜像层构建的，在对容器镜像修改时，仅对最上方读写层做修改。多个不同的镜像可能有相同的底层镜像。

**联合文件系统**

支持将不同物理位置的路径联合挂载到同一个路径下，允许只读和读写路径合并。

**bootfs**

boot loader引导kernel加载到内存，随后boot loader卸载

##### 镜像和容器

**镜像结构->容器结构**

镜像是分层结构，容器同样也是分层结构。联合文件系统如下。

- r/w
- init
- ro
...
- ro

#### 网络

##### 模型

##### 驱动

