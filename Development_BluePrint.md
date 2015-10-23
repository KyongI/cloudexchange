CloudExchange Development Configuration 
=========================================

1. 구성도
---------

##### 1.1 전체 시스템 구성도
![CloudeExBP](https://github.com/KyongI/cloudexchange/blob/master/heat/CloudExBluePrint.png)

##### 1.2 노드 정보

| 노드        | Private NIC | Private IP | 용도              | 비고    |
|-------------|-------------|------------|-------------------|---------| 
|121.78.77.162|eth1         |192.168.0.1 |ODLVTN+Coordinator | Cloud B |
|121.78.77.163|eth2         |192.168.1.2 |ODLVTN             | Cloud A |
|121.78.77.164|eth1         |192.168.0.3 |Control Node       | Cloud B |
|121.78.77.165|eth1         |192.168.1.4 |Control Node       | Cloud A |
|121.78.77.166|eth1         |192.168.0.5 |Compute Node       | Cloud B |
|121.78.77.167|eth1         |192.168.1.6 |Compute Node       | Cloud A |

2. ODL VTN feature 
----------------------
##### 2.1 전체 설치 순서 
1.  ODL VTN Coordinator( DB setup 까지)
2.  ODL VTN Manager 설치 (kataf 실행까지 전체 설치)
3.  Coordinator 실행 및 확인
4.  Controller 설치 및 실행

##### 2.2 VTN Coordinator 설치 및 구성
- <strike>[ODL VTN Coordinator install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNCoordinator_install_v1.md) 참조하여 설치</strike>
- [ODL VTN Coordinator install v2](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNCoordinator_install_v2.md) 참조하여 설치
- 빌드 후에 db setup 까지만 한다. 

##### 2.3 VTN Manager 설치 및 구성
- [ODL VTN Manager install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNManager_install_v1.md) 참조하여 설치 
- 빌드 후 실행

##### 2.1 ODL Controller 설치 및 구성
- [ODL Controller install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_Controller_install_v1.md) 참조하여 설치
- 빌드 전에 vtn.ini 생성하는것이 중요함.

##### 2.4 설치 및 설정 확인 
- vtn coodinator 를 실행한다. 
- manager 확인
```
curl --user "admin":"admin" -H "Accept: application/json" -H "Content-type: application/json" -X GET http://localhost:8080/controller/nb/v2/vtn/default/vtns                          
{"vtn":[]}
```
- coordinator 확인
```
curl --user admin:adminpass -H 'content-type: application/json' -X GET 'http://127.0.0.1:8083/vtn-webapi/api_version.json'  
{"api_version":{"version":"V1.2"}}
```
- controller 실행 및 포트 확인
```
6633/6653 - OpenFlow Ports
6640 - OVS Manager Port
8080 - Port for REST API
```
  * controller가 웹으로 접속 되지 않음. VTN manager rest api포트와 겹친다. (?웹서비스 포트를 옮김?)

##### 2.5 ODL VTN Feature SDN Controller 서비스 데몬 실행순서
- 재부팅 후에도 동작하기 위해서 데몬 형태롤 실행하는 방법

1. manager 실행
```
su - 
cd /usr/local/vtn/manager/dist-karaf/target/assembly/bin
chmod 777 ./start
./start
netstat -ntlp |grep '*' --> 여기서 8080 확인
```

2. coordinator 확인 (코디네이터는 이미 항상 실행중이다.)
```
코디네이터는 이미 실행중이다. 2.4의 Rest API 로 확인하여 응답이 없는 경우에 다음과 같이 실행 한다.
/usr/local/vtn/bin/vtn_start
```

3. Controller 실행
```
cd ~/controller/opendaylight/distribution/opendaylight/target/distribution.opendaylight-osgipackage/opendaylight
./run.sh -start
```

3. Control/Compute Node
------------------------

##### 3.1 Control/Compute Node 설치 및 구성
- [DevStack install v1](https://github.com/KyongI/cloudexchange/blob/master/heat/DevstackNode_install_v1.md) 참조하여 설치 

##### 3.2 설치시 문제점 해결
- 설치시 생기는 문제점은 [이곳](https://github.com/KyongI/cloudexchange/blob/master/heat/Devstack_Install_TroubleShooting.md)을 참조한다.
- Control Node가 계속해서 설치 되지 않는 원인
    - 설치 시스템에 openstack이 깔려 있는 경우 100% 제거하고 다시 설치하기가 어려움.
    - 포멧하고 OS 부터 다시 설치 하는 방법을 일반적으로 권유함.

4. VTN 통신 실험
-----------------

##### 4.1 설정 관련 이슈 
- VTN Manager와 ODL SDN Controller 포트 충돌 이슈 [(Issue151016_PortConflict.md)](https://github.com/KyongI/cloudexchange/blob/master/vtn/Issue151016_PortConflict.md)

