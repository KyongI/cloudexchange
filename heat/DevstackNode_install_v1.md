DevStack Control/Compute Node 설치 및 설정
==================================

##### 1.openssh-server 를 설치 한다. 
```
sudo apt-get install openssh-server vim
```

##### 2. root passwd 설정 후 root 계정 접속
```
sudo passwd
su -
```

##### 3. 네트워크 고정 아이피 설정 : 고정 아이피 지정함. DNS 서버 등록 및 인터넷이 될 수 있는 환경으로 구축해야함
vi /etc/network/interfaces

- 파일내용
```
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address 192.168.1.222
netmask 255.255.255.0
gateway 192.168.1.1
dns-nameservers 8.8.8.8 8.8.4.4

auto eth1
iface eth1 inet static
address 192.168.1.223
```
/etc/init.d/networking restart

##### 4. 확인:
```
nslookup
> naver.com
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	naver.com
Address: 202.179.177.22
Name:	naver.com
Address: 125.209.222.142
Name:	naver.com
Address: 202.179.177.21
Name:	naver.com
Address: 125.209.222.141
> exit
```

> DNS server 변경 방법:
> ```
> vi /etc/resolv.conf
> nameserver 8.8.8.8
> nameserver 8.8.4.4
> ```

##### 5. ssh 활성화, git을 설치
```
service ssh start --> SSH 서비스 실행 
netstat -ntlp | grep '*' --> SSH 서비스 포트 Listen 확인 
apt-get install sysv-rc-conf
sysv-rc-conf ssh on --> 부팅 시 SSH 자동 실행 
apt-get update
apt-get install -y git sudo
ufw disable 
iptables -F 
sudo apt-get install net-tools
```

##### 6. 재부팅 stack 계정 생성
```
reboot
su -
useradd -U -G sudo -s /bin/bash -m stack 
echo “stack ALL=(ALL) NOPASSWD: ALL” >> /etc/sudoers (않되면 "를 다시 쳐본다)
passwd stack
```

##### 7. stack 계정으로 로그인 후 홈 폴더 밑에 devstack을 다운로드 
```
su stack
cd
git clone git://github.com/openstack-dev/devstack 또는 
cd devstack
git checkout stable/juno

다른 방법 
git clone https://github.com/openstack-dev/devstack.git -b stable/juno (icehouse)
```

##### 8. openstack에 대한 네트워크 설정을 정의 한다. 
이 설정은 구성환경별로 설정 방법이 다르다. 
vi ~/devstack/local.conf

- control node
```
[[local|localrc]]
 
#IP Details
HOST_IP=<CONTROL_NODE_MANAGEMENT_IF_IP_ADDRESS> #Control Node (설치 시스템의 eth0 IP)
SERVICE_HOST=$HOST_IP
 
#Instance Details
MULTI_HOST=1
#config Details
RECLONE=yes #Make it "no" after stacking successfully the first time
VERBOSE=True
LOG_COLOR=True
LOGFILE=/opt/stack/logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/logs
#OFFLINE=True #Uncomment this after stacking successfully the first time
 
#Passwords
ADMIN_PASSWORD=labstack 
MYSQL_PASSWORD=supersecret
RABBIT_PASSWORD=supersecret
SERVICE_PASSWORD=supersecret
SERVICE_TOKEN=supersecrettoken
ENABLE_TENANT_TUNNELS=false
 
#ML2 Details
Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=opendaylight
Q_ML2_TENANT_NETWORK_TYPE=local
Q_ML2_PLUGIN_TYPE_DRIVERS=local
disable_service n-net
enable_service q-svc
enable_service q-dhcp
enable_service q-meta
enable_service neutron
 
enable_service odl-compute
ODL_MGR_IP=<ODL_IP_ADDRESS> #ODL IP Address (Controller - 121.78.77.162 또는 163)
OVS_PHYSICAL_BRIDGE=br-int
Q_OVS_USE_VETH=True
 
#Details of the Control node for various services
[[post-config|/etc/neutron/plugins/ml2/ml2_conf.ini]]
[ml2_odl]
url=http://<ODL_IP_ADDRESS>:8080/controller/nb/v2/neutron #ODL IP Address (위와 같음)
username=admin
password=admin
```

- compute node 
```
[[local|localrc]]
 
#IP Details
HOST_IP=<COMPUTE_NODE_MANAGEMENT_IP_ADDRESS> #Compute node Management IP (설치 시스템의 eth0 IP)
SERVICE_HOST=<CONTROLLER_NODE_MANAGEMENT_IP_ADDRESS> #cotnrol Node Management IP (control node 의 eth0 IP)
 
#Instance Details
MULTI_HOST=1
#config Details
RECLONE=yes #Make thgis "no" after stacking successfully once
#OFFLINE=True #Uncomment this line after stacking successfuly first time.
VERBOSE=True 
LOG_COLOR=True
LOGFILE=/opt/stack/logs/stack.sh.log
SCREEN_LOGDIR=/opt/stack/logs
 
#Passwords
ADMIN_PASSWORD=labstack
MYSQL_PASSWORD=supersecret
RABBIT_PASSWORD=supersecret
SERVICE_PASSWORD=supersecret
SERVICE_TOKEN=supersecrettoken
 
#Services
ENABLED_SERVICES=n-cpu,rabbit,neutron
 
#ML2 Details
Q_PLUGIN=ml2
Q_ML2_PLUGIN_MECHANISM_DRIVERS=opendaylight
Q_ML2_TENANT_NETWORK_TYPE=local
Q_ML2_PLUGIN_TYPE_DRIVERS=local
enable_service odl-compute
ODL_MGR_IP=<ODL_IP_ADDRESS> #ODL IP (Controller - 121.78.77.162 또는 163)
OVS_PHYSICAL_BRIDGE=br-int
ENABLE_TENANT_TUNNELS=false
Q_OVS_USE_VETH=True
 
#Details of the Control node for various services
Q_HOST=$SERVICE_HOST
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=$SERVICE_HOST:9292
KEYSTONE_AUTH_HOST=$SERVICE_HOST
KEYSTONE_SERVICE_HOST=$SERVICE_HOST
 
NOVA_VNC_ENABLED=True
NOVNCPROXY_URL="http://<CONTROLLER_NODE_IP_ADDRESS>:6080/vnc_auto.html" #Add Controller Node IP address (control node 의 eth0 IP?)
VNCSERVER_LISTEN=$HOST_IP
VNCSERVER_PROXYCLIENT_ADDRESS=$VNCSERVER_LISTEN
```

##### 9. 설치
~/devstack/stack.sh
