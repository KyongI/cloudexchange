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

##### 포트 충돌 현상 확인
- 아무 것도 실행 되지 않은 상태 (5432 port : postgresql DB 에서 사용 하는 Port)
```
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp6       0      0 ::1:5432                :::*                    LISTEN      -               
tcp6       0      0 :::22                   :::*                    LISTEN      - 
```

- Vtn coordinator 실행시 
```
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.0.1:12730         0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp6       0      0 ::1:5432                :::*                    LISTEN      -               
tcp6       0      0 ::1:12730               :::*                    LISTEN      -               
tcp6       0      0 :::8083                 :::*                    LISTEN      -               
tcp6       0      0 :::22                   :::*                    LISTEN      -    
```

- Vtn manager + vtn coordinator 실행시
```
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.0.1:12730         0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp6       0      0 127.0.0.1:7800          :::*                    LISTEN      -               
tcp6       0      0 ::1:5432                :::*                    LISTEN      -               
tcp6       0      0 :::8185                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:57657         :::*                    LISTEN      -               
tcp6       0      0 ::1:12730               :::*                    LISTEN      -               
tcp6       0      0 :::44444                :::*                    LISTEN      -               
tcp6       0      0 :::6653                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:59232         :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:44576         :::*                    LISTEN      -               
tcp6       0      0 :::12001                :::*                    LISTEN      -               
tcp6       0      0 :::40004                :::*                    LISTEN      -               
tcp6       0      0 :::8101                 :::*                    LISTEN      -               
tcp6       0      0 :::34343                :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:55336         :::*                    LISTEN      -               
tcp6       0      0 :::6633                 :::*                    LISTEN      -               
tcp6       0      0 :::1099                 :::*                    LISTEN      -               
tcp6       0      0 :::6640                 :::*                    LISTEN      -               
tcp6       0      0 :::8080                 :::*                    LISTEN      -               
tcp6       0      0 :::8083                 :::*                    LISTEN      -               
tcp6       0      0 :::8181                 :::*                    LISTEN      -               
tcp6       0      0 :::49654                :::*                    LISTEN      -               
tcp6       0      0 :::22                   :::*                    LISTEN      -       
```

- ODL Controller vtn coordinator 만 실행시 (8185, 12001, 6633, 8080 포트가 겹친다)
```
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.0.1:12730         0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp6       0      0 127.0.0.1:7800          :::*                    LISTEN      22244/java      
tcp6       0      0 ::1:5432                :::*                    LISTEN      -               
tcp6       0      0 :::8185                 :::*                    LISTEN      22244/java      
tcp6       0      0 ::1:12730               :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:35165         :::*                    LISTEN      22244/java      
tcp6       0      0 127.0.0.1:41150         :::*                    LISTEN      22244/java      
tcp6       0      0 :::12001                :::*                    LISTEN      22244/java      
tcp6       0      0 :::1830                 :::*                    LISTEN      22244/java      
tcp6       0      0 :::6633                 :::*                    LISTEN      22244/java      
tcp6       0      0 :::8080                 :::*                    LISTEN      22244/java      
tcp6       0      0 :::8083                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:49108         :::*                    LISTEN      22244/java      
tcp6       0      0 :::22                   :::*                    LISTEN      -             
```

- 포트 충돌을 회피하기 위해 ~/controller/opendaylight/distribution/opendaylight/target/distribution.opendaylight-osgipackage/opendaylight/configuration/tomcat-server.xml 파일에서 다음의 내용을 수정
```
28   <Service name="Catalina">
29     <Connector port="8080" protocol="HTTP/1.1"
30                connectionTimeout="20000"
31                redirectPort="8443" />
```

- 8080을 8088로 수정함. 수정 후 포트 정보.
```
tcp        0      0 127.0.0.1:5432          0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.0.1:12730         0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp6       0      0 127.0.0.1:50679         :::*                    LISTEN      1847/java       
tcp6       0      0 :::8088                 :::*                    LISTEN      1847/java       
tcp6       0      0 127.0.0.1:36344         :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:7800          :::*                    LISTEN      -               
tcp6       0      0 ::1:5432                :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:7801          :::*                    LISTEN      1847/java       
tcp6       0      0 :::8185                 :::*                    LISTEN      -               
tcp6       0      0 ::1:12730               :::*                    LISTEN      -               
tcp6       0      0 :::44444                :::*                    LISTEN      -               
tcp6       0      0 :::6653                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:56061         :::*                    LISTEN      -               
tcp6       0      0 :::12001                :::*                    LISTEN      -               
tcp6       0      0 :::40004                :::*                    LISTEN      -               
tcp6       0      0 :::8101                 :::*                    LISTEN      -               
tcp6       0      0 :::1830                 :::*                    LISTEN      1847/java       
tcp6       0      0 :::34343                :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:41127         :::*                    LISTEN      -               
tcp6       0      0 :::6633                 :::*                    LISTEN      -               
tcp6       0      0 :::1099                 :::*                    LISTEN      -               
tcp6       0      0 :::49612                :::*                    LISTEN      -               
tcp6       0      0 :::6640                 :::*                    LISTEN      -               
tcp6       0      0 :::8080                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:59089         :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:56530         :::*                    LISTEN      1847/java       
tcp6       0      0 :::8083                 :::*                    LISTEN      -               
tcp6       0      0 127.0.0.1:53268         :::*                    LISTEN      1847/java       
tcp6       0      0 :::8181                 :::*                    LISTEN      -               
tcp6       0      0 :::22                   :::*                    LISTEN      -   
```

- 8080 은 해결 되지만 8185, 12001, 6633는 여전히 문제가 있다. (모두 회피하는것이 맞는가?)
- 나머지 충돌 포트에 대한 controller 실행시 로그 메세지 [(Issue151024_ControllerLog.md )](https://github.com/KyongI/cloudexchange/blob/master/vtn/Issue151024_ControllerLog.md)
- 이제는 ODL SDN Controller 에 윕으로 접속 가능하다. 접속시 두개의 vSwitch 가 등록 되어 있음
![ODL web GUI](https://github.com/KyongI/cloudexchange/blob/master/vtn/ODLController.png)



