Open Daylight VTN feature 설치 및 설정 (PART:1 Controller 설치)
======================================

1. ODL SDN Controller 설치 (v1.0)
---------------------------

##### 1.git, JDK 등 설치
```
sudo apt-get update
sudo apt-get install pkg-config gcc make  ant g++ maven git libboost-dev libcurl4-openssl-dev libjson0-dev libssl-dev openjdk-7-jdk unixodbc-dev xmlstarlet
export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64 <---이 내용을 ~/.bash_profile에 쓰고 저장
```

##### 2.Maven 설치 
- 14.04에서 필요 없다고 했으나 Venkatrangan G 로부터 온 메일에 의하면 maven 3.1.1 이상 버젼이 필요.
- 14.04에는 3.0.4 가 설치 되어 있으므로 /opt 폴더에 압축해제후 export 명령으로 PATH를 등록. 
- export PATH=/opt/apache-maven-3.3.3/bin:$PATH ---이 내용을 ~/.bash_profile에 쓰고 저장

##### 3.home/ubuntu 에서 
```
git clone https://git.opendaylight.org/gerrit/p/controller.git
cd controller
git checkout stable/helium  --> error 나는 경우 git checkout -f stable/helium 
```

##### 3.1.빌드전에 vtn.ini 적용
- vtn.ini 파일 내용
```
bridgename=br-int
portname=eth1
protocols=OpenFlow13
failmode=secure
```
- 빌드전에 vtn.ini를 두는것이 맞다면, 다음의 패스중 하나임. 
```
cp vtn.ini controller/opendaylight/netconf/config-persister-impl/target/configuration
cp vtn.ini controller/opendaylight/md-sal/samples/clustering-test-app/configuration
cp vtn.ini controller/opendaylight/configuration
cp vtn.ini controller/opendaylight/distribution/opendaylight/src/main/resources/configuration
cp vtn.ini controller/opendaylight/distribution/opendaylight-karaf-resources/src/main/resources/configuration

아래 패스는 빌드 후에 생성됨
cp vtn.ini controller/opendaylight/distribution/opendaylight/target/configuration
```

##### 4.build & config
```
cd ~/controller/opendaylight/distribution/opendaylight
mvn clean install
cd target/distribution.opendaylight-osgipackage/opendaylight
vi configuration/vtn.ini
```
- vtn.ini 파일 내용
```
bridgename=br-int
portname=eth1
protocols=OpenFlow13
failmode=secure
```

##### 5.실행
```
cd target/distribution.opendaylight-osgipackage/opendaylight
./run.sh
```
- 기다리다가 멈춰 있으면 엔터를 치면 'osgi>' 콘솔 프롬프트가 보이면 실행 완료
- 실행시 ‘java.lang.OutOfMemoryError: PermGen space’ 에러가 뜨는 경우가 있습니다. 메모리 부족 현상 이므로 
export MAVEN_OPTS=”-Xmx1024m -XX:MaxPermSize=512” 하고 다시 빌드.
- 다시 빌드해도 에러가 나면 재부팅 후 다시 빌드해 본다. (메모리 해제 문제임)

##### 5.웹으로 접속
- http://121.78.77.162:8080/
- id/pass : admin/admin
