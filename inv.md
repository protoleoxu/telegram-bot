- [杂乱笔记](#杂乱笔记)
  - [策略](#策略)
    - [负载均衡](#负载均衡)
      - [策略](#策略-1)
  - [网络](#网络)
    - [ARP](#arp)
    - [ip](#ip)
    - [UDP](#udp)
      - [数据报格式](#数据报格式)
    - [TCP](#tcp)
      - [连接状态](#连接状态)
      - [TCP段格式](#tcp段格式)
      - [握手、挥手](#握手挥手)
      - [可靠传输](#可靠传输)
    - [HTTP](#http)
      - [部分概念（http1.0）](#部分概念http10)
      - [会话](#会话)
      - [一个http请求的大概流程](#一个http请求的大概流程)
      - [各版本http协议特点](#各版本http协议特点)
    - [DHCP](#dhcp)
  - [中间件](#中间件)
    - [nginx](#nginx)
      - [工作模型](#工作模型)
      - [部分概念](#部分概念)
      - [实际应用](#实际应用)
      - [机制](#机制)
  - [数据库](#数据库)
    - [基础概念](#基础概念)
  - [linux](#linux)
    - [分散的一些知识点](#分散的一些知识点)
      - [通信、同步](#通信同步)
        - [通信](#通信)
          - [信号量semphere](#信号量semphere)
      - [signal机制（抄了）](#signal机制抄了)
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
        - [机制](#机制-1)
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

### UDP

面向无连接、不可靠传输；差错检测、分用、复用。

#### 数据报格式

在应用层数据包基础之上封装UDP首部，共四个字段，每个字段各2字节：

- 源端口：需要回信时使用，不需要为0
- 目的端口：必须使用，数据报交付的应用程序；如果client接收解析UDP首部发现源端口不存在，丢弃并返回ICMP 端口不可达 差错报文
- 长度：UDP长度，最小8字节
- 检验和：差错校验

**伪首部**

仅在差错校验时临时添加到UDP首部，12字节，不在网络中传输；伪首部共12字节，源目IP地址（4，4）、0（1）、17（1）、UDP长度（2，与UDP首部相同）

发送方检验和生成：

- 首部检验和置0
- UDP数据字节长度为奇数则添加一个字节，置0
- 按二进制反码计算16位字和
- 填充UDP首部检验和字段

### TCP

面向连接（在进行数据交换前需要建立TCP连接，仅有两方通信）；可靠传输（超时重传-每发送一个报文段都会为其启动一个定时器，等待接收方确认；如果超过定时器事件还未收到确认，则重发报文。丢弃重复的报文段。经过IP层传输的TCP报文段可能失序，TCP可以重新排序。利用窗口进行拥塞控制）

#### 连接状态

LISTEN： 侦听来自远方的TCP端口的连接请求
SYN-SENT： 再发送连接请求后等待匹配的连接请求
SYN-RECEIVED：再收到和发送一个连接请求后等待对方对连接请求的确认
ESTABLISHED： 代表一个打开的连接
FIN-WAIT-1： 等待远程TCP连接中断请求，或先前的连接中断请求的确认
FIN-WAIT-2： 从远程TCP等待连接中断请求
CLOSE-WAIT： 等待从本地用户发来的连接中断请求
CLOSING： 等待远程TCP对连接中断的确认
LAST-ACK： 等待原来的发向远程TCP的连接中断请求的确认
TIME-WAIT： 等待足够的时间以确保远程TCP接收到连接中断请求的确认

#### TCP段格式

首部长度20-60字节，前20字节固定。

首部固定字段：

- 源目端口：2，如果端口不存在，则发送RST
- 序号ISN，seq：4，按字节编号
- 确认号ack：4，期望收到的下一个报文段第一个字节的序号；若确认号=N，表示N字节前的数据正确收到
- 数据偏移量：4，报文段数据部分到报文段起始位置距离
- 保留：6
- URG（紧急）：当URG=1，表示紧急指针有效，报文段有紧急数据，尽快发送
- ACK（确认）：仅当ACK=1，确认号有效；建立连接后所有报文段ACK为1
- PSH（推送）：表示尽快交付接收方应用，不用等待缓存
- RST（复位）：RST=1时，表示连接出错，连接断开
- SYN（同步）：建立连接时同步序号；当SYN=1，ACK=0，表示连接请求报文段；SYN=1，ACK=1表示对方同意连接
- FIN（中止）：释放连接；当FIN=1时，表示报文段发送方不再发送数据，请求释放单向连接
- 窗口：2
- 校验和：2，检查首部和数据部分
- 紧急指针：2，指向紧急数据字节数（紧急数据后为普通数据）
- 选项：常用字段MSS（默认536），最长报文段大小，一般在通信第一个报文段中指定，表示本段能接收的最大长度报文段

当建立连接时，交换的只有TCP首部。

tcp无状态（也可以有），所以数据段是否过期都是由发起方确定。

#### 握手、挥手

建立连接（握手）

1. 客户发送一个SYN（一个同步标志，建立连接时使用）段，指明打算连接的服务器的端口，以及初始序号（ISN）。该报文还包括了win（通知窗口大小）、mss（最大报文段长度）。
2. 服务器发回包含服务器初始序号的SYN报文段，同时将确认序号（ACK）设置为客户的ISN+1，表示期望得到ISN+1的报文段。
3. 将确认序号置为ISN+1，发送给服务器。

```
c - SYN=1,seq=x -> s  s确认c发送正常、接收不清楚，c不清楚s
s - ACK=1,ack=x+1,SYN=1,seq=y -> c c确认s发送正常、接收正常，s确认c发送正常、接收不清楚
c - ACK=1,ack=y+1 -> s s确认c发送正常、接收正常，c确认s发送正常、接受正常
```

断开连接（挥手）

1. 首先主动关闭的一方发送一个FIN。
2. 另一方收到这个FIN，执行被动关闭。发回一个ACK，确认序号+1.
3. 服务器向应用程序传送一个文件结束符，接着这个服务器程序就关闭连接，导致服务器发送一个FIN。
4. 客户收到FIN，返回一个ACK给服务器。Client端等待了2MSL（最大报文段生存时间）后依然没有收到回复，则证明Server端已正常关闭，那好，我Client端也可以关闭连接了。

```
1 - FIN=1,seq=x -> 2
2 - ACK=1,ack=x+1 -> 1
2 - FIN=1,seq=y -> 1
1 - ACK=y,seq=y+1 -> 2
```

先发送FIN包的一端最后关闭，因为要等待（2倍最大报文段生存时间）自己最后发送的另一端连接关闭确认包发送成功。

#### 可靠传输

处理收发两端速率不一致问题；接收方告知发送方接收窗口大小；使用ARQ协议控制重传。

**拥塞窗口**

由发送方维护；当发生了超时重传，认为发生拥塞；

慢启动：建立连接后，收到ACK，发送窗口由小变大（swnd=min(cwnd,rwnd)），直到cwnd>ssthresh（慢启动门限，一般为65535字节）

拥塞避免：收到ACK后，cwnd+=1/cwnd

**滑动窗口**

发送/接收数据的缓存区，缓存区大小由接收方（WIN字段）确定；发送方缓存区中的数据在未收到这段数据的ACK报文时不允许清除，收到ACK后可以清除；接收方缓存区包含已发送ACK、未发送ACK的报文段数据，发送ACK报文段在被上层应用获取后从缓存区清除。

连续ARQ：  
发送方根据接收方的WIN字段连续发送报文段，接收方接收后，根据报文段顺序返回序号（seq）从小到大连续的最大序号（ack）。

重传：连续三次收到相同ACK；超过报文段定时器时间。重发缺失报文段还是重发窗口所有报文段由SACK决定；DSACK告知发送端哪些报文段重复。

### HTTP

超文本传输协议，无状态协议。

#### 部分概念（http1.0）

[一些很细节的字段解释](https://juejin.cn/post/6844903550917541896)

*http连接*

传输层协议通过源目ip端口协议五元组确定一个连接，应用层协议通过url：  

```
scheme://host[:port#]/path/.../[url-params/][?query][#anchor]
scheme：协议
host：目标主机ip/域名
port：如果有（http默认80，https默认443）而且不是默认端口，需要添加
path：访问路径
url-params：人为定义的在path中的字段
query：查询条件
anchor：锚点，定位页面位置
```

*http报文*

http 1.0 中有两种，请求、响应。

请求：

```
method url http协议版本
header

body

method：http定义的请求方式
url：请求目标资源
header：首部字段
body：不一定有，post比较常见
```

响应：

```
http协议版本 code code_detail
header

body

code：标记服务端响应状态
code_detail：响应状态说明
header：首部字段
body：一般有
```

*method*

GET: 获取URL指定的资源；
POST：传输实体信息
PUT：上传文件
DELETE：删除文件
HEAD：获取报文首部，与GET相比，不返回报文主体部分

*code*

1XX：提示信息 - 表示请求已被成功接收，继续处理
2XX：成功 - 表示请求已被成功接收，理解，接受
3XX：重定向 - 要完成请求必须进行更进一步的处理
4XX：客户端错误 - 请求有语法错误或请求无法实现
5XX：服务器端错误 - 服务器未能实现合法的请求

常用：

206：表示请求成功，body包含请求数据区间，根据请求range字段确定
302：Found 重定向，新的url会在resp中的location中返回，浏览器会将使用新的url发出新的请求。
304：Not Modified 代表上次的文档已经被缓存了，使用缓存的文档
400：Bad Request 客户端请求与语法错误，不能被服务器所理解
403：Forbidden 服务器收到请求，但是拒绝提供服务
404：Not Found 请求的资源不存在，url错误
500：Internal Server Error 服务错误
502：Bad Gateway 响应无效
503：Server Unavailable 服务器当前不能处理客户端的请求
504：gateway timeout 服务不可达

#### 会话

http协议本身是无状态的（和Tcp一样）；约定使用Cookie、Set-Cookie字段去表示一个会话（tcp也一样，类似）。

Cookie是客户端请求时加入header的，Set-Cookie时服务端响应时加入header的。

*字段属性*

Set-Cookie

NAME=VALUE：赋予Cookie的名称和值；
expires=DATE: Cookie的有效期；
path=PATH: 将服务器上的目录作为Cookie的适用对象，若不指定，则默认为文档所在的文件目录；
domin=域名：作为Cookies适用对象的域名，若不指定，则默认为创建Cookie的服务器域名；
Secure: 仅在HTTPS安全通信是才会发送Cookie；
HttpOnly: 使Cookie不能被JS脚本访问；

Cookie中的值根据Set-Cookie确定。

#### 一个http请求的大概流程

请求数据的包装细节忽略，应用层程序知道目标主机程序的ip、port（如果仅有host，则先需要请求dns解析，解析过程-查找本地hosts解析记录-请求root域名服务-请求顶级域名服务-请求次级域名服务-请求权威域名服务-获取ip）；与目标主机建立tcp连接；发送http包；

#### 各版本http协议特点

*1.0*

1.0版本的协议中，一次请求响应，就是一个tcp连接建立、传输、断开的过程；当请求数量较多时，建立、断开tcp请求的开销就会变得很大。

*1.1*

长连接支持。keep-alive，tcp连接复用，不用每次请求都建立一个新的连接，keep-alive在tcp协议中实现类似心跳，但如果服务不可用也可能保持连接，故应用层的keep-alive还需要在应用层实现，；pipeline，允许c连续请求，但s必须按收到请求顺序依次响应；理论上c向s请求一次需要等待响应，再发送下一次请求；身份认证、状态管理、缓存处理、断点续传、host请求 。

*2.0*

1.*版本协议字段语义化（文本方式？一目了然？），2.0版本使用二进制帧。

概念：

- 帧：http2.0最小通信单位，所有帧共享8字节首部，包含帧长度、类型、标志、保留位
- 消息：逻辑上的http消息（请求、响应），包含一个或多个帧
- 流：tcp连接虚拟信道

http1.\*消息格式为头部+body，http2.0将http1.\*消息分为多个消息和帧，用二进制编码；头部为header帧，body为data帧。

实现（TODO）：

- 首部压缩
- 多路复用
- 请求优先级
- 服务器推送

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

#### 工作模型

```
           |-----worker
master-----|-----worker
           |-----worker
```

nginx启动后会有一个master进程和多个worker进程

- master负责管理worker进程；接收外界信号、监控worker状态、向worker发送信号
- worker负责处理网络事件
- 多个worker进程之间是对等的，公平竞争来自客户端的请求；一个请求只能在一个客户端内处理。

启动：nginx启动时，master加载配置文件完成初始化，建立socket（listenfd，按结构应该是worker中调用的epoll监听的事件和fd就是master在启动时创建的listenfd，worker自身只维护与client建立链接的socket），fork() worker进程。

重启：master收到重启信号（SIGNHUP），master重新载入配置文件，向旧worker发送信号停止接收新请求，拉起新worker；旧worker收到信号后，不再接收请求，将正在处理的请求处理完成后退出。

接收请求：所有worker公平竞争新的请求；当新请求进入，所有worker的listenfd可读；在读请求事件注册前，worker尝试竞争accept_mutex，竞争成功的worker注册listenfd读事件；在读事件里调用accept接受该连接。当一个worker进程在accept这个连接之后，就开始读取请求，解析请求，处理请求，产生数据后，再返回给客户端，最后才断开连接。


#### 部分概念

**connection**

对tcp链接的封装，包含socket、读写事件（封装socket？），ngx_connection_t；单独的worker进程能够处理的链接数和内核nofile及worker_connections有关，前者是系统最大文件打开数，后者是一个worker进程能建立的链接数；nginx为每个worker维护一个当前worker的大小为worker_connects的ngx_connection_t结构体数组，和一个大小free_connections的空闲ngx_connection_t链表；每创建一个链接从free_connections中取一个，释放连接后添加到free_connections；nginx能承受的最大并发是worker_process * worker_connections 或者 worker_process * worker_connection / 2（反代）；worker在竞争新连接的accept_mutex时会先判断自己的free_connections数量与设置的worker_connections/8的大小，如果大则放弃竞争。

[**抄的，晚点整理**](https://tengine.taobao.org/book/chapter_02.html#keepalive)
keepalive
当然，在nginx中，对于http1.0与http1.1也是支持长连接的。什么是长连接呢？我们知道，http请求是基于TCP协议之上的，那么，当客户端在发起请求前，需要先与服务端建立TCP连接，而每一次的TCP连接是需要三次握手来确定的，如果客户端与服务端之间网络差一点，这三次交互消费的时间会比较多，而且三次交互也会带来网络流量。当然，当连接断开后，也会有四次的交互，当然对用户体验来说就不重要了。而http请求是请求应答式的，如果我们能知道每个请求头与响应体的长度，那么我们是可以在一个连接上面执行多个请求的，这就是所谓的长连接，但前提条件是我们先得确定请求头与响应体的长度。对于请求来说，如果当前请求需要有body，如POST请求，那么nginx就需要客户端在请求头中指定content-length来表明body的大小，否则返回400错误。也就是说，请求体的长度是确定的，那么响应体的长度呢？先来看看http协议中关于响应body长度的确定：

对于http1.0协议来说，如果响应头中有content-length头，则以content-length的长度就可以知道body的长度了，客户端在接收body时，就可以依照这个长度来接收数据，接收完后，就表示这个请求完成了。而如果没有content-length头，则客户端会一直接收数据，直到服务端主动断开连接，才表示body接收完了。
而对于http1.1协议来说，如果响应头中的Transfer-encoding为chunked传输，则表示body是流式输出，body会被分成多个块，每块的开始会标识出当前块的长度，此时，body不需要通过长度来指定。如果是非chunked传输，而且有content-length，则按照content-length来接收数据。否则，如果是非chunked，并且没有content-length，则客户端接收数据，直到服务端主动断开连接。
从上面，我们可以看到，除了http1.0不带content-length以及http1.1非chunked不带content-length外，body的长度是可知的。此时，当服务端在输出完body之后，会可以考虑使用长连接。能否使用长连接，也是有条件限制的。如果客户端的请求头中的connection为close，则表示客户端需要关掉长连接，如果为keep-alive，则客户端需要打开长连接，如果客户端的请求中没有connection这个头，那么根据协议，如果是http1.0，则默认为close，如果是http1.1，则默认为keep-alive。如果结果为keepalive，那么，nginx在输出完响应体后，会设置当前连接的keepalive属性，然后等待客户端下一次请求。当然，nginx不可能一直等待下去，如果客户端一直不发数据过来，岂不是一直占用这个连接？所以当nginx设置了keepalive等待下一次的请求时，同时也会设置一个最大等待时间，这个时间是通过选项keepalive_timeout来配置的，如果配置为0，则表示关掉keepalive，此时，http版本无论是1.1还是1.0，客户端的connection不管是close还是keepalive，都会强制为close。

如果服务端最后的决定是keepalive打开，那么在响应的http头里面，也会包含有connection头域，其值是”Keep-Alive”，否则就是”Close”。如果connection值为close，那么在nginx响应完数据后，会主动关掉连接。所以，对于请求量比较大的nginx来说，关掉keepalive最后会产生比较多的time-wait状态的socket。一般来说，当客户端的一次访问，需要多次访问同一个server时，打开keepalive的优势非常大，比如图片服务器，通常一个网页会包含很多个图片。打开keepalive也会大量减少time-wait的数量。

pipe
在http1.1中，引入了一种新的特性，即pipeline。那么什么是pipeline呢？pipeline其实就是流水线作业，它可以看作为keepalive的一种升华，因为pipeline也是基于长连接的，目的就是利用一个连接做多次请求。如果客户端要提交多个请求，对于keepalive来说，那么第二个请求，必须要等到第一个请求的响应接收完全后，才能发起，这和TCP的停止等待协议是一样的，得到两个响应的时间至少为2*RTT。而对pipeline来说，客户端不必等到第一个请求处理完后，就可以马上发起第二个请求。得到两个响应的时间可能能够达到1*RTT。nginx是直接支持pipeline的，但是，nginx对pipeline中的多个请求的处理却不是并行的，依然是一个请求接一个请求的处理，只是在处理第一个请求的时候，客户端就可以发起第二个请求。这样，nginx利用pipeline减少了处理完一个请求后，等待第二个请求的请求头数据的时间。其实nginx的做法很简单，前面说到，nginx在读取数据时，会将读取的数据放到一个buffer里面，所以，如果nginx在处理完前一个请求后，如果发现buffer里面还有数据，就认为剩下的数据是下一个请求的开始，然后就接下来处理下一个请求，否则就设置keepalive。

lingering_close
lingering_close，字面意思就是延迟关闭，也就是说，当nginx要关闭连接时，并非立即关闭连接，而是先关闭tcp连接的写，再等待一段时间后再关掉连接的读。为什么要这样呢？我们先来看看这样一个场景。nginx在接收客户端的请求时，可能由于客户端或服务端出错了，要立即响应错误信息给客户端，而nginx在响应错误信息后，大分部情况下是需要关闭当前连接。nginx执行完write()系统调用把错误信息发送给客户端，write()系统调用返回成功并不表示数据已经发送到客户端，有可能还在tcp连接的write buffer里。接着如果直接执行close()系统调用关闭tcp连接，内核会首先检查tcp的read buffer里有没有客户端发送过来的数据留在内核态没有被用户态进程读取，如果有则发送给客户端RST报文来关闭tcp连接丢弃write buffer里的数据，如果没有则等待write buffer里的数据发送完毕，然后再经过正常的4次分手报文断开连接。所以,当在某些场景下出现tcp write buffer里的数据在write()系统调用之后到close()系统调用执行之前没有发送完毕，且tcp read buffer里面还有数据没有读，close()系统调用会导致客户端收到RST报文且不会拿到服务端发送过来的错误信息数据。那客户端肯定会想，这服务器好霸道，动不动就reset我的连接，连个错误信息都没有。

在上面这个场景中，我们可以看到，关键点是服务端给客户端发送了RST包，导致自己发送的数据在客户端忽略掉了。所以，解决问题的重点是，让服务端别发RST包。再想想，我们发送RST是因为我们关掉了连接，关掉连接是因为我们不想再处理此连接了，也不会有任何数据产生了。对于全双工的TCP连接来说，我们只需要关掉写就行了，读可以继续进行，我们只需要丢掉读到的任何数据就行了，这样的话，当我们关掉连接后，客户端再发过来的数据，就不会再收到RST了。当然最终我们还是需要关掉这个读端的，所以我们会设置一个超时时间，在这个时间过后，就关掉读，客户端再发送数据来就不管了，作为服务端我会认为，都这么长时间了，发给你的错误信息也应该读到了，再慢就不关我事了，要怪就怪你RP不好了。当然，正常的客户端，在读取到数据后，会关掉连接，此时服务端就会在超时时间内关掉读端。这些正是lingering_close所做的事情。协议栈提供 SO_LINGER 这个选项，它的一种配置情况就是来处理lingering_close的情况的，不过nginx是自己实现的lingering_close。lingering_close存在的意义就是来读取剩下的客户端发来的数据，所以nginx会有一个读超时时间，通过lingering_timeout选项来设置，如果在lingering_timeout时间内还没有收到数据，则直接关掉连接。nginx还支持设置一个总的读取时间，通过lingering_time来设置，这个时间也就是nginx在关闭写之后，保留socket的时间，客户端需要在这个时间内发送完所有的数据，否则nginx在这个时间过后，会直接关掉连接。当然，nginx是支持配置是否打开lingering_close选项的，通过lingering_close选项来配置。 那么，我们在实际应用中，是否应该打开lingering_close呢？这个就没有固定的推荐值了，如Maxim Dounin所说，lingering_close的主要作用是保持更好的客户端兼容性，但是却需要消耗更多的额外资源（比如连接会一直占着）。


#### 实际应用

**负载均衡策略（[抄了](https://learnku.com/articles/36737)）**

- 轮询（默认）：所有请求依次分配给服务器组内的服务器
- 加权轮询：为服务器组内的服务器设置权重weight
- ip_hash：根据源ip经过hash算法之后得到一个hash值，此后所有符合此hash的请求全部转发到相同服务器
- 最少链接数：判断服务器组中的服务器哪个active connection最少，分配给它

context：upstream

```
upstream serverName {
  server host|ip weight max_fails fail_timeout backup down;
}
```

**连接限制**

*漏桶算法*

限制桶（连接缓存空间）漏水（接收请求）速度，当桶中的水满了，后续添加的水丢弃。

*limit_conn_zone*
context：http
```
limit_conn_zone key zone=name:size;
# key 标记，可以是ip、url等等
# zone 保存每个key对应的链接数，共享内存空间
# size zone的大小
```

当共享内存空间被耗尽，新的key请求将会被拒绝，503。

*limit_conn*
context：http、server、location
```
limit_conn zone number;
# number 连接个数
```

**lua**

**缓存、缓冲**

缓存控制主要由HTTP HEADER控制；仅对没有Set-Cookie的GET、HEAD请求响应。

缓冲主要用于反向代理时对upstream请求的响应是否直接返回给客户端。


#### 机制

*惊群效应*

多个worker在等待请求时睡眠，一旦有请求进入（fd可读），将会唤醒所有等待worker。无效调度。

## 数据库

### 基础概念

## linux

linux中包含的各种实现及原理。

### 分散的一些知识点

#### 通信、同步

大部分文章中对把同步和通信一起说了。没太看懂，[按照这个理清了点思路](https://github.com/CyC2018/CS-Notes/issues/106)。

不同进程或线程交换信息或者竞争资源的手段是通信，不同进程或线程按照某种规则访问资源是同步；通信是手段，同步是目的。

##### 通信

###### 信号量semphere

由一个整型变量sem和两个原子操作PV组成。sem表示资源数量；P()请求资源时操作，尝试减少（sem-1；当sem < 0，等待sleep）；V()释放资源时操作，增加（sem+1，当sem<=0，唤醒wakeup等待）。

特点：

- sem初始化后只能通过PV()操作更改
- 操作系统保证PV()操作原子性
- P()可能阻塞（blocked），V()不会
- 信号量等待是公平的（P()不会无限等待，等待队列的FIFO）
- 互斥锁是信号量的一个特殊情况

伪代码实现：

```
struct Semphere {
  Sem int
  WaitQueue []
}

Semphere::P(){
  sem--
  if sem < 0 {
    WaitQueue.append(t)
    block(t)
  }
}

Semphere::V(){
  sem++
  if sem <= 0 {
    t = WaitQueue.pop(0)
    wakeup(t)
  }
}
```

信号量种类：

- sem=1，互斥访问
- sem=n>1，有限资源数量访问




**互斥锁**

**管道**

**消息传递**

**共享内存**


#### signal机制（[抄了](http://gityuan.com/2015/12/20/signal/)）

linux定义了64种信号，分为不可靠信号和可靠信号，每种信号各占32。
不可靠信号不支持排队，信号可能丢失；对进程发送多次相同信号，只能收到一次。1-31。
可靠信号为实时信号，支持排队；信号不会丢失，发多少次就能收到多少次。

用过的信号：
- 1 SIGNHUP 挂起进程（nginx中为重启`nginx -s reload`、`kill -HUP`）
- 9 SIGNKILL kill进程
- 3 SIGNQUIT 退出进程（nginx中为优雅退出`nginx -s quit`）
- 10 SIGNUSR1 用户自定义信号（nginx中为重新打开文件`nginx -s reopen`，用来切割文件）

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

