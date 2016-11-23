# dnspod.py

dnspod.py 是基于 [DNSPod](http://www.dnspod.cn/docs/records.html#dns) 服务的动态 DNS 脚本，用于检测 IP 变化并更新至 DNSPod。支持 Linux 设备，包括树莓派（[Raspberry Pi](https://www.raspberrypi.org/)）。

# Prerequisites

1. python
1. pyyaml
1. requests

python 的模块可通过 ```pip install``` 命令安装。如果未安装 [pip](https://pip.pypa.io/)，请先安装 pip。

# Installation

安装 [git](https://git-scm.com/) 客户端，通过本命令获取 dnspod.py

<pre>
git clone https://github.com/migege/dnspod.git
</pre>

然后到 dnspod 目录下新建 ```conf.yaml``` 文件，根据您的 DNSPod 设置，填入以下内容：

<pre>
token : &lt;your_api_token&gt;
domain_id : &lt;your_domain_id&gt;
record_id : &lt;your_record_id&gt;
sub_domain: &lt;sub_domain&gt;
</pre>

最后设置 crontab 定时任务

<pre>
*/10 * * * * cd &lt;path_to_dnspod&gt;; /usr/bin/python dnspod.py conf.yaml &gt; /dev/null 2&gt;&1 &
</pre>

# Tips

1. */10 表示每 10 分钟执行一次 dnspod.py
1. 如果 python 可执行路径不是 /usr/bin/python，请自行替换
