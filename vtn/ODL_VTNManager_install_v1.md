Open Daylight VTN feature 설치 및 설정 (PART:3 VTN Manager) - Ver 1.0
======================================

##### 1.참고 링크
- <https://wiki.opendaylight.org/view/Release/Helium/VTN/Developer_Guide:Hacking:VTN_Manager>

##### 2.다음과 같이 빌드 한다. 
```
cd /usr/local/vtn 
git checkout stable/helium
cd manager/dist-karaf ==> 참고 페이지 에서는 manager/dist/karaf로 되어 있는데 dist-karaf가 맞다. 
mvn clean install -DskipTests
```

##### 3.실행
```
cd target/assembly
./bin/karaf

vtn@/usr/local/vtn/vtn/manager/dist-karaf/target/assembly$ ./bin/karaf 
                                                                                           
    ________                       ________                .__  .__       .__     __       
    \_____  \ ______   ____   ____ \______ \ _____  ___.__.|  | |__| ____ |  |___/  |_     
     /   |   \\____ \_/ __ \ /    \ |    |  \\__  \<   |  ||  | |  |/ ___\|  |  \   __\    
    /    |    \  |_> >  ___/|   |  \|    `   \/ __ \\___  ||  |_|  / /_/  >   Y  \  |      
    \_______  /   __/ \___  >___|  /_______  (____  / ____||____/__\___  /|___|  /__|      
            \/|__|        \/     \/        \/     \/\/            /_____/      \/          
                                                                                           

Hit '<tab>' for a list of available commands
and '[cmd] --help' for help on a specific command.
Hit '<ctrl-d>' or type 'system:shutdown' or 'logout' to shutdown OpenDaylight.

opendaylight-user@root>GossipRouter started at Tue Sep 15 15:09:17 KST 2015
Listening on port 12001 bound on address 0.0.0.0/0.0.0.0
Backlog is 1000, linger timeout is 2000, and read timeout is 0
SLF4J: Class path contains multiple SLF4J bindings.
SLF4J: Found binding in [bundleresource://266.fwk936259672:1/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [bundleresource://266.fwk936259672:2/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [bundleresource://266.fwk936259672:3/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
SLF4J: Actual binding is of type [org.slf4j.impl.JDK14LoggerFactory]
opendaylight-user@root>feature:list |grep vtn <== test
odl-vtn-manager-all                   | 0.2.5-SNAPSHOT      | x         | vtn-manager-0.2.5-SNAPSHOT             | OpenDaylight VTN Manager All                      
odl-vtn-manager-java-api              | 0.2.5-SNAPSHOT      | x         | vtn-manager-0.2.5-SNAPSHOT             | OpenDaylight :: VTN Manager :: Java API           
odl-vtn-manager-northbound            | 0.2.5-SNAPSHOT      | x         | vtn-manager-0.2.5-SNAPSHOT             | OpenDaylight :: VTN Manager :: Northbound         
odl-vtn-manager-neutron               | 0.2.5-SNAPSHOT      | x         | vtn-manager-0.2.5-SNAPSHOT             | OpenDaylight :: VTN Manager :: Neutron Interface 

```

##### 4.Rest API test 
```
--> tenant network 생성
djkim@djkim-VirtualBox:~$ curl --user "admin":"admin" -H "Accept: application/json" -H "Content-type: application/json" -X POST http://localhost:8080/controller/nb/v2/vtn/default/vtns/Tenant1 -d '{"description": "My First Virtual Tenant Network"}'
--> 확인
djkim@djkim-VirtualBox:~$ curl --user "admin":"admin" -H "Accept: application/json" -H "Content-type: application/json" -X GET http://localhost:8080/controller/nb/v2/vtn/default/vtns
{"vtn":[{"description":"My First Virtual Tenant Network","name":"Tenant1","idleTimeout":300,"hardTimeout":0}]}
```
