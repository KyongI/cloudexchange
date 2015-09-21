Open Daylight VTN feature 설치 및 설정 (PART:1 VTN Coordinator)
======================================

1. ODL VTN Coordinator 설치 (v1.0)
---------------------------

1.참고 싸이트  
<https://wiki.opendaylight.org/view/OpenDaylight_Virtual_Tenant_Network_(VTN):Installation:VTN_Coordinator>   

2.OS 설치 환경  
CentOS 6.6  
kernel: Linux 2.6.32-431.el6.x86_64  

3.패키지 인스톨  
- yum install make glibc-devel gcc gcc-c++ boost-devel openssl-devel ant perl-ExtUtils-MakeMaker unixODBC-devel perl-Digest-SHA uuid libxslt libcurl libcurl-devel git
- boost-devel, openssl-devel은 설치되지 않음
- ssh 가 접속 되지 않는 현상 
> 1.linux 에서 iptables, selinux 확인. 
> 2.linux 에서 'ssh djkim@[idc 서버ip]' 로 외부 접속 확인
> 3.pc 방화벽 확인 ping은 실패함(원래 되어야 함)
> 4.pc의 네트워크 인터페이스에서 vm virtual net 인터페이스가 비활성화 되어 있었음
- boost-devel/openssl-devel 설치시 오류
```
[root@localhost ~]# yum install boost_devel
Loaded plugins: fastestmirror, priorities, refresh-packagekit, security
Setting up Install Process
Loading mirror speeds from cached hostfile
* base: ftp.kaist.ac.kr
* epel: mirror.premi.st
* extras: ftp.kaist.ac.kr
* updates: ftp.kaist.ac.kr
http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/epel-6/repodata/repomd.xml: [Errno 14] PYCURL ERROR 22 - "The requested URL returned error: 404 Not Found"
Trying other mirror.
119 packages excluded due to repository priority protections
No package boost_devel available.
Error: Nothing to do
```

4.Install JDK 7, and add the JAVA_HOME environment variable 
```
yum install java-1.7.0-openjdk-devel 
export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64 
```

5.Install PostgreSQL 9.1
- http://yum.postgresql.org/9.1/redhat/rhel-6.4-x86_64 <--여기에 웹으로 접속해서 해당 rpm 설치(클릭하면 설치한다)
 
6.Install Maven
- http://maven.apache.org/download.cgi <--여기 가서 시키는 데로 /opt 에 maven 압축 풀고 환경변수 등록

7.Install gtest-devel, json-c libraries 
```
wget http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
rpm -Uvh epel-release-6-8.noarch.rpm
yum install gtest-devel json-c json-c-devel
```

8.adduser vtn
```
adduser vtn
passwd vtn
cd /usr/local 
mkdir vtn
su vtn
chown vtn:vtn vtn
```
--> vtn coo~ build에 실패함. mvn -f dist/pom.xml install 에서 error. 더이상 진행 불가.

