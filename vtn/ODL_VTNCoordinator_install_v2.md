Open Daylight VTN feature 설치 및 설정 (PART:2 VTN Coordinator) - Ver 2.0
======================================

1. Prior preparation
--------------------

##### 1.참고 링크( 여기를 참고 하였으나 ODL Wiki는 시간이 지나면 링크가 사라지거나 변동 된다.)
<https://wiki.opendaylight.org/view/OpenDaylight_Virtual_Tenant_Network_(VTN):Installation:VTN_Coordinator>

##### 2.OS 설치 환경  
ubuntu 14.04

###### 3.패키지 설치
```
sudo apt-get update
sudo apt-get install pkg-config gcc make  ant g++ maven git libboost-dev libcurl4-openssl-dev libjson0-dev libssl-dev openjdk-7-jdk unixodbc-dev xmlstarlet
```

##### 4.JDK 설치 - 14.04에서 필요 없음

##### 5.PostgreSQL 9.1 설치 
```
sudo apt-get install  postgresql postgresql-client postgresql-client-common postgresql-contrib odbc-postgresql
```
- 여기에서 postgresql-9.1로 하면 설치 않됨. 버전 부분을 삭제 하면 postgresql ver 9.3을 설치한다.

##### 6.Maven 설치 
- 14.04에서 필요 없다고 했으나 Venkatrangan G 로부터 온 메일에 의하면 maven 3.1.1 이상 버젼이 필요.
- 14.04에는 3.0.4 가 설치 되어 있으므로 /opt 폴더에 압축해제후 export 명령으로 PATH를 등록. 

##### 7.Install gtest-devel, json-c libraries - 14.04에서 필요없음

2. Build
-------

##### 8.add user 'vtn' 
```
sudo adduser vtn
```

##### 9.Download the code from git.
```
sudo cd /usr/local/
sudo git clone https://git.opendaylight.org/gerrit/p/vtn.git
sudo chown -R vtn:vtn /usr/local/vtn
sudo su - vtn
vi ~/.bash_profile 
export PATH=/opt/apache-maven-3.3.3/bin:$PATH (mvn 실행을 위해 설정)
export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64 (path가 맞는지 확인할것)
:wq!
source ~/.bash_profile
```

##### 10.Build and install VTN Coordinator. 
```
cd vtn
git checkout release/[stable**] <-- 여기에 현재 release 버젼인 lithium으로 빌드하면 mvn 에러가 난다. 원인 불명. 그래서 전버젼인 helium 으로 설치 
cd coordinator
mvn -f dist/pom.xml install 
tar -C/ -jxvf dist/target/distribution.vtn-coordinator-6.0.0.0-Helium-bin.tar.bz2
```

3. Run VTN Coordinator
--------------------------
##### 11.Set up the DB. --> 여기서 PostgreSQL 에러. 다음과 같이 설치 한다. 
``` 
/usr/local/vtn/sbin/db_setup 
Setup completed successfully. <--(확인)
```

##### 12.Start VTN Coordinator. 
```
/usr/local/vtn/bin/vtn_start
```

##### 13.실행 확인 
```
curl --user admin:adminpass -H 'content-type: application/json' -X GET 'http://127.0.0.1:8083/vtn-webapi/api_version.json'  
-->(응답)
{"api_version":{"version":"V1.2"}}
--> 이렇게 나오면 설치 완료
```
