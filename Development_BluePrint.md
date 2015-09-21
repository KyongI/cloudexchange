CloudExchange Development Configuration 
=========================================

1. 구성도
---------

##### 1.1 전체 시스템 구성도

##### 1.2 노드 정보

| 노드        | Private NIC | Private IP | 용도       | 비고            |
|-------------|-------------|------------|------------|-----------------| 
|121.78.77.162|eth1         |192.168.0.1 |Controller  |                 |
|121.78.77.163|eth2         |192.168.0.2 |Controller  |                 |
|121.78.77.164|eth1         |192.168.0.3 |            |OS 재설치 필요   |
|121.78.77.165|eth1         |192.168.0.4 |            |soft reboot 않됨 |
|121.78.77.166|eth1         |192.168.0.5 |Compute node|                 |
|121.78.77.167|eth1         |192.168.0.6 |            |                 |
|121.78.77.168|eth1         |192.168.0.7 |            |                 |

2. ODL VTN feature 
----------------------

##### 2.1 ODL Controller 설치 및 구성
- [ODL Controller install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_Controller_install_v1.md) 참조하여 설치
- 실행 전단계 까지 설치 합니다. 

##### 2.2 VTN coordinator 설치 및 구성
- <strike>[ODL VTN Coordinator install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNCoordinator_install_v1.md) 참조하여 설치</strike>
- [ODL VTN Coordinator install v2](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNCoordinator_install_v2.md) 참조하여 설치
- 빌드 후에 db setup 까지만 한다. 

##### 2.3 VTN manager 설치 및 구성
- [ODL VTN Manager install v1](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODL_VTNManager_install_v1.md) 참조하여 설치 
- 빌드 후 실행

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
- controller 실행
  * controller가 웹으로 접속 되지 않음. VTN manager rest api포트와 겹친다. (?웹서비스 포트를 옮김?)

3. Control/Compute Node
------------------------

##### 3.1 Control Node 설치 및 구성

##### 3.2 Compute Node 설치 및 구성

4. VTN 통신 실험
-----------------
