- [杂乱笔记](#杂乱笔记)
  - [策略](#策略)
    - [负载均衡](#负载均衡)
      - [策略](#策略-1)
  - [网络](#网络)
    - [ARP](#arp)
    - [ip](#ip)
    - [DHCP](#dhcp)
  - [中间件](#中间件)
    - [nginx](#nginx)
  - [数据库](#数据库)
  - [linux](#linux)
    - [分散的一些知识点](#分散的一些知识点)
      - [进程](#进程)
    - [IO](#io)
      - [IO设备访问](#io设备访问)
      - [IO方式](#io方式)
      - [IO模型](#io模型)
        - [阻塞IO](#阻塞io)
        - [非阻塞IO](#非阻塞io)
        - [IO多路复用](#io多路复用)
        - [异步IO](#异步io)
    - [网络协议栈](#网络协议栈)
    - [iptables netfilter](#iptables-netfilter)
      - [netfilter](#netfilter)
      - [iptables](#iptables)
        - [概念](#概念)
        - [iptables规则](#iptables规则)
        - [iptables与docker](#iptables与docker)
        - [iptables部分命令的应用（TODO）](#iptables部分命令的应用todo)
  - [docker](#docker)
    - [架构（自顶向下）](#架构自顶向下)
      - [各层级交互细节（TODO）](#各层级交互细节todo)
    - [功能](#功能)
      - [资源](#资源)
        - [隔离](#隔离)
          - [具体实现/应用（？）](#具体实现应用)
        - [限制](#限制)
          - [概念](#概念-1)
          - [规则（v1？）](#规则v1)
          - [如何实现（提供用户接口）](#如何实现提供用户接口)
          - [如何操作](#如何操作)
          - [关于v1和v2的区别](#关于v1和v2的区别)
          - [hierarchy、cgroup、subsystem、slice、scope、service的关系](#hierarchycgroupsubsystemslicescopeservice的关系)
      - [存储](#存储)
        - [机制](#机制)
        - [镜像和容器](#镜像和容器)
        - [文件系统驱动（TODO）](#文件系统驱动todo)
          - [overlay/overlay2](#overlayoverlay2)
          - [AUFS](#aufs)
          - [devicemapper](#devicemapper)
      - [网络](#网络-1)
        - [模型](#模型)
          - [CNM模型](#cnm模型)
          - [docker网络驱动](#docker网络驱动)
        - [部分机制类型](#部分机制类型)
          - [单机网络模型](#单机网络模型)
          - [全局网络模型](#全局网络模型)
# 杂乱笔记

## 策略

### 负载均衡

将服务压力分摊至各服务器，防止出现单点故障导致无法提供服务。

#### 策略

- 轮询：按照请求列表中的服务器挨个分配请求。
- 最小链接：优先选择链接数最少的服务器分配请求。
- IP_HASH：将请求源IP转换为hash并发往某个服务器，同一ip的请求都将分配至同一服务器。（nginx中的iphash策略不宜应用于当nginx为二层代理，此外负载也不均衡。）

## 网络

### ARP

链路层协议。实现ip->mac地址解析。

**过程**

- c1广播发送(ffff.ffff.ffff)c2 mac地址arp请求(包含c1 ip、mac，c2 ip)，局域网内不是c2 ip的设备收到请求后不响应，c2接收请求后响应自身mac。
- c1收到c2 mac响应，缓存该mac与c2 ip信息至本地arp表。

### ip

提供面向无连接不可靠传输。

**默认字段**

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

**其他字段（TODO）**

### DHCP

UDP协议，用于为设备分配ip地址。

67、68、546分别为DHCP协议server、client、ipv6client端口。

**过程**

- client ---`DHCPDISCOVER`(广播)--> 局域网内所有设备。在不清楚局域网内所有DHCP服务器地址时，通过广播发送discover报文，所有收到报文的DHCP服务器都会响应。
- DHCP服务器 ---`DHCPOFFER`--> client。DHCP服务器收到discover报文后向client发送的off报文，包含ip、租期和其他配置信息，此时ip为预分配ip。若不存在可分配ip，则发送`DHCPNAK`。
- client ---`DHCPREQUEST`--> DHCP服务器。收到offer报文后，向DHCP服务器发送request报文，请求使用ip。
- DHCP服务器 ---`DHCPACK`--> client。收到request报文后，发送ack，告知client可以使用，并将ip从ip池标记。(client会发送ARP请求该ip，若无响应则表明该ip可用)
- client ---`DHCPRELEASE`--> DHCP服务器。client不再使用分配的ip时发送。

## 中间件

### nginx



## 数据库

## linux

linux中包含的各种实现及原理。

### 分散的一些知识点

#### 进程

**用户态&内核态**

简单理解，进程的用户态与内核态区别在于运行是否受限（IO请求、进程切换、内存访问等等），即权限不同。
当进程运行触发系统调用（主动触发，操作系统提供的对计算机资源操作的接口，由用户态进程主动调用，由操作系统执行，本质也是中断，软中断）、异常（被动触发，是进程内部执行触发。IO中断、外部信号）、中断（被动触发，由外部信号触发。进程运算错误）时，会由内核接管cpu。

**上下文切换**

TODO

**文件描述符**

文件描述符是内核返回给进程其所有打开文件的指针。结构上看，进程拥有的是它自己打开文件的指针，指针指向内核维护的操作系统中所有被打开文件的文件描述符表的某条记录，系统的文件描述符表中的记录指向了文件系统维护的文件信息表（ext4的话是inode）。
进程对文件的所有操作都是通过文件描述符（操作系统提供对文件描述符的系统调用？）。

linux中的进程都有（？）预设打开的三个文件，stdin、stdout、stderr。

### IO

#### IO设备访问

PIO：cpu通过执行IO端口指令进行与慢IO设备数据交换的模型。
DMA：直接内存访问，不经过cpu直接访问内存进行与慢IO设备数据交换的模型。
PIO模型下慢IO设备与内存的数据交换是通过cpu控制的；DMA是由cpu向DMA设备发送指令，让DMA设备控制数据传输，传输完成后再通知cpu。

#### IO方式

**缓存IO**

数据从磁盘先通过DMA模式拷贝到内核空间高速缓存页,再从高速缓存页通过cpu拷贝到用户空间应用缓存。缓存I/O被称作为标准I/O，大多数文件系统的默认I/O操作都是缓存I/O。
分离了用户空间和内核空间，减少缓存与磁盘之间的IO次数（？）；但由于数据在内核空间和用户空间之间多次拷贝，拷贝操作会给cpu和内存带来开销。

```
 read()    write()
   ⬆          |
   |          ⬇
----------------------
应用程序缓存（用户空间）
----------------------
   ⬆          |
   |   cpu    ⬇
----------------------
      内核缓存区
----------------------
   ⬆          |
   |          ⬇
----------------------
        物理设备
```
读：操作系统检查内核缓冲区有没有请求数据，如果由，则直接返回缓存；如果没有，从磁盘中读取到内核缓冲区，再复制到用户地址空间。
写：把用户地址空间的缓存复制到内核缓存，此时对用户进程，写操作已经完成；从内核缓存写到磁盘则由操作系统决定，或显示调用sync()。

**直接IO**

数据从磁盘通过DMA模式拷贝到用户空间应用缓存。由于不需要先将数据拷贝到内核缓存，可以减少用户空间和内核空间数据拷贝带来的cpu和内存开销；但当需要访问的数据不再用户缓存中，需要直接请求磁盘，速度比较慢。

```
 read()      write()
   ⬆            |
   |            ⬇
----------------------
应用程序缓存（用户空间）
----------------------
   ⬆            |
   |     cpu    ⬇
----------------------
   |  内核缓存区 |
----------------------
   ⬆             |
   |             ⬇
----------------------
        物理设备
```

**内存映射**

（没太懂TODO

使用内存映射方式进行读写的话，其实是对进程逻辑空间中一个指针进行操作，指针指向需要读写的文件。

#### IO模型

[参考资料](https://www.ibm.com/developerworks/cn/linux/l-async/)

同步模型和异步模型的区别：实际的IO操作有没有被阻塞（数据从设备到内核缓存）。

一次read()（举个例子）调用会经过两个阶段：等待数据准备；将数据从内核拷贝至进程。
IO模型介绍是基于这两个阶段的不同情况。分别有五种IO模型：阻塞式IO、非阻塞式IO、IO复用、信号驱动式IO、异步IO。

##### 阻塞IO

同步模型；
一阶段：使用阻塞IO模型的用户进程在调用系统调用之后，会进入阻塞状态（Blocked）；内核执行系统调用，等待数据；
二阶段：收到数据后，内核返回，将数据从内核空间拷贝到用户空间，返回结果；用户进程解除阻塞。

（懒得画图了，TODO

##### 非阻塞IO

同步模型；与阻塞IO的区别主要是在第一阶段，用户进程调用系统调用之后，会收到内核返回的错误（EWORLDBLOCK/EAGAIN），而不是阻塞进程；用户进程此时知道内核还没有准备好数据，然后不断执行系统调用，直到数据准备完成，进入二阶段。

（懒得画图了，TODO

##### IO多路复用

同步模型、事件驱动IO。
IO多路复用是由内核提供的select、poll、epoll系统调用实现的。逻辑架构是，用户进程调用select()（或poll、epoll）后，可以同时监听多个打开文件的文件描述符（用户进程也可以在用户空间内通过多线程非阻塞IO实现类似的逻辑，这里是由内核实现）并等待，某个文件描述符的数据准备完成后通知用户进程文件可读，进入二阶段。
实际过程，用户进程调用之后，用户进程被select()阻塞（与阻塞IO不同，阻塞IO是由内核等待数据IO阻塞的），select()负责对被监听的文件描述符进行轮询（读/写就绪、异常、超时），当有一个文件描述符就绪，通知进程进行读写。

（懒得画图了，TODO

**关于IO多路复用中select、poll、epoll的部分细节**

简要的描述一下这些系统调用的过程。

select()：

设置文件描述符集合（fd_set，无符号整数（？），每一位表示一个进程自身的文件描述符；有三种，写、读、异常），将想监听的文件描述符的位置对应fd_set中的某一位置1，select()会对传入的fd_set中置1的文件描述符监听；当被监听的文件描述符就绪/或超时，select()将对应位置fd_set置1，未就绪置0，并立即返回就绪文件描述符数量；最后由用户进程判断期望的文件描述符是否就绪（传入的fd_set遍历），开始读写。select()调用之后会遍历每个期望监听的fd；如果没有一个文件描述符就绪，阻塞用户进程，直到就绪。

> 在调用select()时，需要传入fd_set，当监听的fd很多，fd_set会很大，每次调用select()都会将用户空间的fd_set整个拷贝到内核空间；  
> 内核要逐个遍历fd_set中的fd；  
> 能够同时监听的文件描述符不足，默认为1024（32位OS？）；  

poll()：

调用过程差不多，不过用于维护fd的是链表pollfd，且没有限制。

epoll()：  
[（细节太多了](https://imageslr.github.io/2020/02/27/select-poll-epoll.html)  
使用红黑树存储fd；使用队列存储就绪状态fd；每个fd在添加时传入一次，触发事件后修改fd状态（加入就绪队列）。  
调用过程有三步：  
- int epoll_create()：创建一个epoll实例，返回实例的fd。epfd表示epoll实例fd；由于是打开的文件，所以在epoll过程结束后需要close(epfd)；epoll实例内部存储的是所有被监听fd的红黑树、就绪状态fd的队列。
- int epoll_ctl()：对指定fd执行op，返回这次操作状态。epoll_ctl对指定fd执行op（EPOLL_CTL_ADD、EPOLL_CTL_MOD、EPOLL_CTL_DEL，分别对应添加事件、更改事件、删除事件），fd会加入到epoll设置的监听列表，为fd与设备绑定监听事件（回调函数）。当fd触发事件执行回调函数，fd会被加入到epoll就绪队列。
- int epoll_wait()：执行等待epfd触发事件，返回事件数量。监听事件会被传入，从调用之后开始阻塞直到事件触发，返回触发事件的数量。（通过检查epfd指向的就绪队列？）

**水平触发 边缘触发**

水平触发（LT）：当fd就绪时，通知进程；如果进程没有一次性完成数据传输，下次还会通知进程。  
边缘触发（ET）：只有当fd就绪才会通知，之后不通知。

select使用水平触发，epoll两者都支持。

##### 异步IO

异步模型；异步IO在执行系统调用之后（aio）会直接返回，不会阻塞用户进程；等到数据准备好，由内核复制到用户空间后，向进程发送通知。两个阶段都是非阻塞的

（细节TODO

### 网络协议栈

**OSI标准七层**

open system interconnection model，开放式系统互联模型，是一种通信系统标准。
通信系统中的数据流被划分为七层，从跨通信介质传输位的物理实现到分布式应用程序的最高层。每个中间层为上一层提供功能，下一层为自身提供功能。

```

---------------------
|application layer  |
---------------------
|presentation layer |
---------------------
|session layer      |
---------------------
|transport layer    |
---------------------
|network layer      |
---------------------
|data link layer    |
---------------------
|phyical layer      |
---------------------

```

**TCP/IP四层**

osi七层为通信系统标准。实际应用为四层（TCP/IP协议簇）模型（感觉是五层）。

```

---------------------
|application layer  |HTTP、DHCP...
---------------------
|transport layer    |TCP、UDP...
---------------------
|network layer      |IP、ICMP...
---------------------
|link layer         |ARP...
---------------------
|phyical layer      |
---------------------

```

这里划分的还是五层，但是链路层和物理层在其他地方好像合并了，并没有做专门区分。

**linux网络协议栈（TODO）**

（[以下内容均为抄袭...](https://bstanwar.wordpress.com/2010/05/25/anatomy-of-the-linux-networking-stack/)

网络栈结构：

```

-----------------------------
|application layer          | --->   user space
-----------------------------
|system call interface      | ------------
-----------------------------            |
|protocol agnostic interface|            |
-----------------------------            |
|network protocols          |       kernel space
-----------------------------            |
|device agnostic interface  |            |
-----------------------------            |
|device drviers             |-------------
-----------------------------
|physical device hardware   |
-----------------------------

```

[具体实现细节太难了...](http://www.uml.org.cn/embeded/2016041410.asp?artid=17878)，以下为尽量理解理解的内容。

按照结构描述，应用层的用户进程通过内核空间提供的系统调用，创建socket（这里是protocol agnostic interface，也即协议无关层）。socket是对network protocols（传输层协议）操作的抽象，低层协议的具体实现被隐藏，用户进程只需要调用socket提供的api去实现应用层功能。

### iptables netfilter

iptables是linux用户空间用于定义网络数据流向规则的工具，而netfilter则是提供实现对数据过滤的内核hook。按照官方解释，netfilter是内核提供的对报文数据包进行过滤修改的框架，允许将过滤修改的函数在设定的阶段作用于网络协议栈；iptables则是一个用户层工具，用来向netfilter添加规则策略（除了iptables也有别的工具可以这样做）。

#### netfilter

**概念**

netfilter在内核协议栈中定义了5个hook点，当数据包经过hook时会触发内核模块注册的hook函数。

hook点：
- NF_IP_PRE_ROUTING：接收数据包进入协议栈，在路由之前。
- NF_IP_LOCAL_IN：接收数据包经路由之后，目标地址是本机。
- NF_IP_FORWARD：接收数据包经路由之后，目标地址是其他机器。
- NF_IP_LOCAL_OUT：发送数据包进入协议栈。
- NF_IP_POST_ROUTING：发送/转发数据包经路由之后。

数据包流向大概可以表示为：

```
                                ------  user procced     --------
                                ⬆                                |
                                |                                ⬇
                            local in                         local out
                                ⬆                                |
packet in                       |                                ⬇                          packet out
------>  prerouting  ------>  route  ------>  forward  ------>  route  ------>  postrouting  ----->
```

netfiler看起来是工作在网络协议栈的IP层，但是根据[这张图](https://tonybai.com/wp-content/uploads/nf-packet-flow.png)，图中packet流向是经过了链路层的，emmmm，不太清楚细节。

#### iptables

> iptable是专门用来处理ipv4数据包的，ipv6需要使用ip6tables。

##### 概念

iptables使用table管理数据包处理rule。根据类型（作用）被组织为table的rule会注册到netfilter提供的hook点。当数据包经过hook点，根据table中的rule执行对应的hook函数，对数据包进行过滤、跟踪、修改。

table类型（各种作用的rule）：
- filter：过滤数据
- nat：网络地址转换
- mangle：修改数据包
- raw：控制数据包连接跟踪（connection tracking）？标记数据包
- security：给数据包打selinux标记（没用过）

chain类型（对应hook点）：
- PREROUTING：数据包进入路由之前
- INPUT：数据包路由后进入本机
- FORWARD：数据包路由后发往其他主机
- OUTPUT：数据包发出路由之前
- POSTROUTING：数据包路由后发出后

table与chain的关系是多对多的，一个table可以分布在不同chain上，在不同的数据包流向阶段对其进行相同处理；chain中也包含多个table，在同一阶段对数据包做不同功能的处理。

```
                                                   user space
                                     |                                   |
                                     |                                   |
                                     |                                   |
                                     |                                   ⬇
                                     |                                [output]
                                +---------+                         +---------+
                                |  mangle |                         |   raw   |
                                |  filter |                         |  mangle |
                                |nat(SNAT)|                         |nat(DNAT)|
                                +---------+                         |  filter |        
                                   [input]                          +---------+        
                                      ⬆                                  |             
             +---------+              |                                  |             
             |   raw   |              |           +---------+            |             +---------+
             |  mangle |              |           |  mangle |            |             |  mangle |
             |nat(DNAT)|              |           |  filter |            |             |nat(SNAT)|
packet in    +---------+              |           +---------+            ⬇             +---------+   packet out
----------> [prerouting] --------> [route] ------> [forward] -------> [route] -------> [postrouting] ------>
```

table和chain之间的关系如图。同一个chain上的table，有优先级关系（按优先级高到低，raw>mangle>dnat>filter>security>snat）。数据包经过chain时，根据table优先级顺序匹配table中的rule；如果数据包与rule（一是table优先顺序，二是table内rule顺序）匹配成功，则会直接对数据包进行处理，跳过后面的rule。

##### iptables规则

rule的信息分为两部分：
- matching：匹配条件，协议类型、源目IP、源目端口、网卡、header数据、链接状态...
- target：匹配成功后怎么处理，常用（用过的...）DROP（丢弃）、ACCEPT（通过）、RETURN（跳出chain）、QUEUE（将数据包加入用户空间队列，等待处理）、JUMP（跳转到用户自定义chain）、REJECT（拒绝）

raw与connection tracking：connection tracking是netfilter提供的链接跟踪系统，可以让iptables基于链接上下文而不是单个数据包匹配判断。
开启后，connection tracking发生在netfilter框架的NF_IP_PRE_ROUTING和NF_IP_LOCAL_OUT，connection tracking会跟踪每个数据包（除了被raw表中rule标记为NOTRACK的数据包），维护所有链接的状态；维护的链接状态可以供其他表的rule使用，也可以通过/proc/net/ip_conntrack获取链接信息。

链接状态有（[抄了](https://arthurchiao.art/blog/deep-dive-into-iptables-and-netfilter-arch-zh/#2-netfilter-hooks)）：
- NEW：如果到达的包关联不到任何已有的连接，但包是合法的，就为这个包创建一个新连接。对面向连接的（connection-aware）的协议例如TCP以及非面向连接的（connectionless）的协议例如 UDP 都适用
- ESTABLISHED：当一个连接收到应答方向的合法包时，状态从`NEW`变成`ESTABLISHED`。对TCP这个合法包其实就是`SYN/ACK`包；对UDP和ICMP是源和目的IP与原包相反的包
- RELATED：包不属于已有的连接，但是和已有的连接有一定关系。这可能是辅助连接（helper connection），例如FTP数据传输连接，或者是其他协议试图建立连接时的ICMP应答包
- INVALID：包不属于已有连接，并且因为某些原因不能用来创建一个新连接，例如无法识别、无法路由等等
- UNTRACKED：如果在raw table中标记为目标是`UNTRACKED`，这个包将不会进入连接跟踪系统
- SNAT：包的源地址被NAT修改之后会进入的虚拟状态。连接跟踪系统据此在收到反向包时对地址做反向转换
- DNAT：包的目的地址被NAT修改之后会进入的虚拟状态。连接跟踪系统据此在收到反向包时对地址做反向转换

##### iptables与docker

docker安装启动后会自动创建几个chain，并通过jump将数据包从input chain跳转到DOCKER_*的chain上。实际上docker的端口转发也算是通过iptables实现的。

##### iptables部分命令的应用（TODO）


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

###### 概念

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

###### 规则（v1？）

- 一个subsystem只能attach（附加？）在一个hierarchy
- 一个hierarchy可以有多个subsystem
- 一个task可以在多个cgroup中，但不能是同一hierarchy的cgroup，即同一task不能有多个相同资源的限制。
- 子task默认在父task的cgroup中，可以移动到其他cgroup
- 当创建了新的cgroup时，默认会将系统中所有进程添加至该cgroups中的root节点

###### 如何实现（提供用户接口）

cgroups通过linux的VFS（虚拟文件系统，TODO）提供用户接口，作为一种文件系统，启动后默认挂载至/sys/fs/cgroup（使用systemd的系统）。

###### 如何操作

可以直接echo > /sys/fs/cgroup下各subsystem中的配置参数？不太安全
systemd

###### 关于v1和v2的区别

v1：为每个subsystem创建一个hierarchy，再在下创建cgroup
v2：以cgroup为主导，有一个unified hierarchy，在cgroup中有subsystem

###### hierarchy、cgroup、subsystem、slice、scope、service的关系

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

**bootfs & rootfs**

bootfs没有找到非常具体的说明，结合linux启动过程，bootfs指的是boot loader（linux一般为grub）和kernel，这里的kernel应该不是至linux系统真正运行的内核，而是在linux启动过程grub加载的内核镜像及初始磁盘镜像（initrd，虚拟的根文件系统），其中内核镜像会执行解压并加载到内存，内核从grub程序接管硬件，grub卸载；此后initrd镜像也被解压到内存并挂载，挂载后作为临时根文件系统，允许内核在没有挂载任何物理设备时完成引导；内核启动后，在最终根文件系统（rootfs，一种文件系统标准，包含/proc、/etc、/sys等等）挂载之后会卸载initrd或者不卸载；rootfs在最开始挂载时为只读，验证完整性之后会改为读写挂载。

综上bootfs应该是boot loader和临时根文件系统（rootfs），在内核启动后会卸载；rootfs应该是一种根文件系统格式，包含一些规定的文件系统（/proc、/etc、/var...）。

##### 镜像和容器

**镜像结构->容器结构**

镜像和容器都是分层结构，每一层都是一个文件系统，只是在属性上有所区别。

整个打包好的镜像都属于rootfs（R/O），这里每一层的文件都是只读的；容器与镜像之间有init层，这一层为初始化容器时覆盖的部分文件（hosts、resolve.conf...）；最上层为容器层，容器层文件系统是可读写的，所有对容器内文件的修改不会影响到下层。

在此基础上，不同操作系统的容器实际上除了可能共享底层镜像，还有docker host的内核。即与宿主机操作系统的rootfs同一层级，都运行在宿主机内核之上，以实现运行相同内核的不同发行版。

大致的联合文件系统如下。

- r/w
- init
- ro
...
- ro

**镜像->容器的读写（偷懒拷贝了）**

对于读，考虑下列3种场景：

读的文件不在容器层：如果读的文件不在容器层，则从镜像层进行读
读的文件只存在在容器层：直接从容器层读
读的文件在容器层和镜像层：读容器层中的文件，因为容器层隐藏了镜像层同名的文件

对于写，考虑下列场景：

写的文件不在容器层，在镜像层：由于文件不在容器层，因此overlay/overlay2存储驱动使用copy_up操作从镜像层拷贝文件到容器层，然后将写入的内容写入到文件新的拷贝中
删除文件和目录：删除镜像层的文件，会在容器层创建一个whiteout文件来隐藏它；删除镜像层的目录，会创建opaque目录，它和whiteout文件有相同的效果
重命名目录：对一个目录调用rename(2)仅仅在资源和目的地路径都在顶层时才被允许，否则返回EXDEV

##### 文件系统驱动（TODO）

具体（也不是很具体）的联合文件系统是如何组织各镜像层和容器层。

###### overlay/overlay2

overlay文件系统结构上看只有两层，分为lower dir和upper dir。联系镜像与容器的关系，lower dir -> 镜像层联合；upper dir -> 容器层。
在overlay文件系统中，lower dir中所有上层layer目录中的文件（如果没冲突）都是底层layer中文件的硬链接（以此节约硬盘空间），用户直接操作的挂载点称为merged dir，挂载点挂载最上层lower dir和upper dir。
其中lower dir为只读，upper dir为读写，用户实际操作的目录为merged dir。
可以通过`mount | grep overlay`看到实际的挂载信息，显示了lowerdir、upperdir、workdir的路径。能看到lowerdir只有一个路径。（[参考，优缺点也在这了](https://www.itread01.com/content/1541539989.html)）

overlay2与overlay在结构上的区别是，overlay2是多层的，与镜像容器结构相似。overlay2不再使用硬链接方式将lower dir中底层layer的文件硬链接到上一层，lower dir中的上层会有一个指向下层的目录的软连接。挂载点merged dir会挂载lower dir的每一层和upper dir。

一些细节：
- 当存在同名文件时（文件或目录），upper dir的文件会覆盖lower dir的文件，lower dir的文件被隐藏。
- COW发生在对lower dir的文件进行写操作时，COPY_UP，先将lower dir的文件复制到upper dir，再写入。

###### AUFS

同样也是分层的文件系统，不过是多层文件系统是叠加在一起的。默认最上层的文件系统是读写，之下的所有层都是只读的。不过可以指定某一层为读写，如果有多个读写层，当进行写操作时可以按照某种策略执行。
aufs中的层用branch表示，每一个branch代表一个目录，当用aufs挂载时，挂载点可见的文件为每个文件从最高层到最底层的最顶层的文件。
如果最上层不存在某个文件，则会按branch序号由小到大索引。
对照镜像容器结构，只读层的多层叠加文件系统 -> 镜像层；读写层 -> 容器。

###### devicemapper

对block操作的文件系统，aufs和overlayfs都是对文件操作。大概的逻辑类似lvm，逻辑卷，devicemapper提供逻辑设备到物理设备的映射机制。
在docker应用中的粗略描述是，devicemapper会初始化一个资源池（使用thin provisioning，类似动态分配存储，用时分配），资源池可以类比为逻辑卷；接着创建一个带有文件系统的基础设备，这个设备为devicemapper的逻辑设备，所有镜像是基础设备的快照。
在读写操作方面与aufs和overlayfs类似，都使用了cow，不过只有在写时才会分配实际的块给文件。

#### 网络

主要内容是docker的网络模型。

##### 模型

docker使用的网络模型、驱动以及单机网络模型和全局网络模型（跨主机）。

###### CNM模型

包含3种组件：

- sandbox：一个沙盒包含一个容器网络栈信息，对容器接口、路由和DNS进行设置，可以有多个端点和网络。这里用namespace实现举例。
- endpoint：一个端点可以加入一个沙盒和一个网络，并只属于一个沙盒。用VETH PAIR实现举例。
- network：一个网络是一组可以直接互相连通的端点，可以包含多个端点。用brigde实现举例。

**bridge、veth、network namespace**

- bridge：linux虚拟网桥，是一种虚拟设备，类似于交换机，工作在TCP/IP二三层。
- veth：虚拟网卡接口，总是成对出现。
- network namespace：linux提供的用于隔离网络设备、堆栈、端口的机制，创建隔离的网络配置（网络设备、路由表等）。

###### docker网络驱动

docker网络库libnetwork中内置几种驱动：

- bridge：类似于交换机，在tcp/ip做协议交换；docker的默认网络驱动，使用bridge驱动后会默认创建docker0 bridge，所有容器链接到docker0进行数据交换。
- host：使用docker宿主机的网络配置，不会创建新的namespace。
- overlay（抄了）：overlay 驱动采用 IETF 标准的 VXLAN 方式，并且是 VXLAN 中被普遍认为最适合大规模的云计算虚拟化环境的 SDN controller 模式。需要使用额外的配置存储服务。（TODO）类似于构建在集群上的虚拟网络，集群物理网络设备为物理机，overlay网络为虚拟机。
- remote：插件。
- null：仍然拥有容器独立namespace网络配置，但除了lo，没有其他设备配置，需要手动配置。

##### 部分机制类型

###### 单机网络模型

这里仅用bridge驱动构建的网络进行描述，bridge网络驱动也是docker的默认驱动。

单机网络模型大概拓扑：

```
-------------------
|                 |
| container1   |veth1|-------
|                 |         |
-------------------         |
                          docker0-----en0
-------------------         |
|                 |         |
| container2   |veth2|-------
|                 |
-------------------
```

联系CNM模型

sandbox提供网络协议栈配置 -> namespace 提供网络协议栈
endpoint为容器实际通讯端点 -> veth pair 一对veth分别绑定在bridge和容器
network为一组可以互相连通的endpoint -> bridge 作为交换机，多个容器veth通过bridge进行数据交换

在拓扑图中，容器内的数据收发通过veth*，通过本地路由表、arp表记录向其他容器发送或发送至docker0，再由docker0通过en0收发数据；在和不同bridge网络通信时，则是由docker0做路由（FORWARD）。

###### 全局网络模型

