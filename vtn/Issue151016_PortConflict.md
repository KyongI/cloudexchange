##### Issue 151016 : ODL Controller 와 VTN Manager Port 충돌
- ODL Controller 를 설치하면 다음과 같은 포트를 사용합니다.
- 참조 페이지 : 
```
6633/6653 - OpenFlow Ports
6640 - OVS Manager Port
8080 - Port for REST API
```
- 여기에 동일한 시스템에 vtn manager와 vtn coordinator를 설치할때, vtn manager의 rest api 를 위한
포트가 8080입니다. 그러면 포트가 겹쳐서 충돌이 일어난다. 
