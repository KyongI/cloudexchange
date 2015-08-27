VTN Coodinator API
===================

개요
----
VTN Coodinator의 REST API를 분석 한다.

요청(Request) 메세지
--------------------
| 필드 이름   |    POST      |    PUT       |    GET       |    DELETE    |
|-------------|--------------|--------------|--------------|--------------|
| username    |     yes      |    yes       |     yes      |    yes       |
| password    |     yes      |    yes       |     yes      |    yes       |
| accept      |     no       |    no        |     no       |    no        |
| content-type|     yes      |    yes       |     no       |    no        |
| content-len |     yes      |    yes       |     no       |    no        |
| host        |     yes      |    yes       |     yes      |    yes       |

1. username/password: VTN 코디네이터의 리소스에 접근하는데 필요한 사용자 이름 및 암호.
2. accept: 응답 메세지 포맷의 accept 
3. content type/len: POST/PUT 메세지에서 요청 메세지의 type 및 length 
4. host: VTN 코디네이터 호스트 이름 또는 IP 주소

응답(Response) 메세지
---------------------
Response 메세지는 XML과 JSON 을 지원.

VTN 코디네이터 REST API 
-----------------------
### Show API Version 
***현재 버전에서 지원하지 않음***
- Method : GET
- Request URI : /api_version
- Response Elements 
     - version :VTN API의 버젼. Vn.n (n은 양의 정수)
- Response 
```javascript
{
    "api_version": {
        "version": "{version}"
    }
}
```
### Show Coordinator Version
- Method : GET
- Request URI : /coordinator_version
- Response Elements
     - version :VTN 코디네이터의 버젼. Va.b.c.d (a - major, b - minor, c - revision, d - patch level.)
     - patch_no :코디네이터에 적용된 패치번호 
- Response 
```javascript
{
    "coordinator_version": {
    "version": "{version}",
    "patches": [
        {
            "patch_no": "{patch_no}"
        }
    ]
}
```
### Flow List Functions
##### Create Flow List : Flow 리스트를 생성한다. 
- Method : POST
- Request URI : /flowlists
- Request Elements
     - fl_name :플로우리스트 이름
     - ip_version :ip 버전(default: IP)
- Request
```javascript
{
    "flowlist": {
        "fl_name": "{fl_name}",
        "ip_version":
        "{ip_version}"
    }
}
```
- Response :Response codes

##### Delete Flow List : Flow 리스트를 삭제한다. 
- Method : DELETE
- Request URI : /flowlists/{fl_name}
- Request Elements
     - fl_name :플로우리스트 이름
- Response :Response codes

##### List Flow List : Flow 리스트 목록을 보여준다.  
- Method : GET
- Request URI : /flowlists, /flowlists/detail, /flowlists/count
- QueryString : ?index={fl_name}&max_repetition={max_repetition}&ip_version={ip_version} 
- Request Elements
     - fl_name :플로우리스트 이름
     - max_repetetion :리소스의 개수(확인이 필요)
     - ip_version :IP 버전
- Response :(/flowlists/detail의 경우)
```javascript
{
    "flowlists": [
        {
            "fl_name":
            "{fl_name}",
            "ip_version":
            "{ip_version}"
        }
    ]
}
```
- Response Elements
     - fl_name :플로우리스트 이름
     - ip_version :IP 버전
     - count :플로우리스트의 개수

##### Show Flow List : 지정한 Flow리스트를 보여준다.  
- Method : GET
- Request URI : /flowlists/{fl_name}
- QueryString : ?ip_version={ip_version} 
- Request Elements
     - fl_name :플로우리스트 이름
     - ip_version :IP 버전
- Response 
```javascript
{
    "flowlist": {
        "fl_name": "{fl_name}",
        "ip_version":
    "{ip_version}"
    }
}
```

### Flow List Entry Functions
##### Create Flow List Entries: Flow리스트 항목을 생성한다. 
- Method : POST
- Request URI : /flowlists/{fl_name}/flowlistentries
- Request
```javascript
{
 "flowlistentry": {
 "seqnum": "{seqnum}",
 "macdstaddr": "{macdstaddr}",
 "macsrcaddr": "{macsrcaddr}",
 "macethertype": "{macethertype}",
 "macvlanpriority": "{macvlanpriority}",
 "ipdstaddr": "{ipdstaddr}",
 "ipdstaddrprefix": "{ipdstaddrprefix}",
 "ipsrcaddr": "{ipsrcaddr}",
 "ipsrcaddrprefix": "{ipsrcaddrprefix}",
 "ipv6dstaddr": "{ipv6dstaddr}",
 "ipv6dstaddrprefix": "{ipv6dstaddrprefix}",
 "ipv6srcaddr": "{ipv6srcaddr}",
 "ipv6srcaddrprefix": "{ipv6srcaddrprefix}",
 "ipproto": "{ipproto}",
 "ipdscp": "{ipdscp}",
 "l4dstport": "{l4dstport}",
 "l4dstendport": "{l4dstendport}",
 "l4srcport": "{l4srcport}",
 "l4srcendport": "{l4srcendport}",
 "icmptypenum": "{icmptypenum}",
 "icmpcodenum": "{icmpcodenum}",
 "ipv6icmptypenum": "{ipv6icmptypenum}",
 "ipv6icmpcodenum": "{ipv6icmpcodenum}"
 }
}
```
- Request Elements (요청 항목들은 SDN flow를 구성하는 22 tuple 항목이다.)
     - seqnum  :일련 번호 
     - macdstaddr :도착지 MAC 주소
     - macsrcaddr :송신지 MAC 주소
     - macethertype :이더넷 프레임 타입
     - macvlanpriority :VLAN priority 태그 번호
     - ipdstaddr :목적지 IP 주소
     - ipdstaddrprefix :목적지 IP 주소의 prefix 길이
     - ipsrcaddr :송신지 IP 주소 
     - ipsrcaddrprefix :송신지 IP 주소의 prefix 길이
     - ipv6dstaddr :목적지 IPv6 주소
     - ipv6dstaddrprefix :목적지 IPv6 주소의 prefix 길이
     - ipv6srcaddr :송신지 IPv6 주소
     - ipv6srcaddrprefix :송신지 IPv6 주소의 prefix 길이
     - ipproto :IP 프로토콜 번호
     - ipdscp :DSCP 값
     - l4dstport :대상 포트 번호
     - l4dstendport :대상end 포트 번호
     - l4srcport :소스 포트 번호
     - l4srcendport :소스end 포트 번호
     - icmptypenum :ICMP 타입 값
     - icmpcodenum :ICMP 코드 값
     - ipv6icmptypenum :IPv6 ICMP 타입 값
     - ipv6icmpcodenum :IPv6 ICMP 코드 값

##### Delete Flow List Entry: Flow리스트 항목을 삭제한다. 
- Method : DELETE
- Request URI : /flowlists/{fl_name}/flowlistentries/{seqnum}
- Request Elements
     - fl_name :플로우리스트 이름
     - seqnum :일련 번호
- Response :없음

##### Update Flow List Entry: Flow리스트 항목을 업데이트 한다.
- Method : PUT
- Request URI : /flowlists/{fl_name}/flowlistentries/{seqnum}.json
- Request
```javascript
{
 "flowlistentry": {
 "macdstaddr": "{macdstaddr}",
 ...생략...
 "ipv6icmpcodenum": "{ipv6icmpcodenum}"
 }
}
```
- Request Elements (Create Flow List Entries 참조)
- Response :없음

##### List Flow List Entries: Flow리스트 항목 정보의 목록을 보여준다. 
- Method : GET
- Request URI : /flowlists/{fl_name}/flowlistentries, /flowlists/{fl_name}/flowlistentries/detail, /flowlists/{fl_name}/flowlistentries/count
- QueryString : ?index={seqnum}&max_repetition={max_repetition}
- Request Elements
     - fl_name :플로우리스트 이름
     - seqnum :일련 번호
     - max_repetetion :리소스의 개수(확인이 필요)
- Response :(/flowlists/{fl_name}/flowlistentries/detail의 경우 Create Flow List Entries의 Request 참조)

##### Show Flow List Entry: Flow리스트 항목을 보여준다. 
- Method : GET
- Request URI : /flowlists/{fl_name}/flowlistentries/{seqnum}.json
- Request Elements (List Flow List Entrie 참조)
- Response :(Create Flow List Entries의 Request 참조)

### VTN Station Functions
***현재 버전에서 지원하지 않음 (생략)***

### VTN Functions
##### Create VTN: VTN을 생성한다. 
- Method : POST
- Request URI : /vtns
- Request
```javascript
{
  "vtn": {
  "vtn_name": "{vtn_name}",
  "description":
  "{description}"
  }
}
```
- Request Elements
      - vtn_name :VTN의 이름(31 char)
      - description :VTN 설명(127 char)
- Response :Response codes
 
##### Delete VTN: VTN을 삭제한다. 
- Method : DELETE
- Request URI : /vtns/{vtn_name}
- Response :Response codes

##### Update VTN: VTN을 업데이트한다. 
- Method : PUT
- Request URI : /vtns/{vtn_name}
- Request
```javascript
{
  "vtn": {
  "description":
  "{description}"
  }
}
```
- Response :Response codes
 
##### List VTNs: 지정한 VTN 정보 목록을 보여준다.
- Method : GET
- Request URI : /vtns, /vtns/detail, /vtns/count
- QueryString : ?index={vtn_name}&max_repetition={max_repetition}
- Response (/vtns/detail의 경우)
```javascript
{
  "vtns": [
    {
              "vtn_name":
   "{vtn_name}",
              "description":
   "{description}",
              "operstatus":
   "{operstatus}",
              "createdtime":
   "{createdtime}",
              "lastcommittedtime":
   "{lastcommittedtime}",
              "alarmstatus":
   "{alarmstatus}"
      }
  ]
}
```
- Request Elements
      - vtn_name :VTN의 이름(31 char)
      - description :VTN 설명(127 char)
      - operstatus :VTN 작동 상태
      - createdtime :생성 후 경과 시간(초)
      - lastcommittedtime :마지막 commit후 경과 시간(초)
      - alarmstatus :알람 상태값
      - count :VTN 개수

##### Show VTNs :지정된 VTN 정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}
- Response
```javascript
{
   "vtn": {
       "vtn_name": "{vtn_name}",
       "description":
  "{description}",
       "operstatus":
  "{operstatus}",
       "createdtime":
  "{createdtime}",
       "lastcommittedtime":
  "{lastcommittedtime}",
       "alarmstatus":
  "{alarmstatus}"
     }
}
```
- Request Elements (List VTNs 참조)

### VTN Mapping Functions
***현재 버전에서 지원하지 않음 (생략)***

### Controller Data Flow function
***현재 버전에서 지원하지 않음 (생략)***

### Data Flow function
##### Show Data Flows : 데이터플로우를 보여줌.
- Method : GET
- Request URI : /dataflows
- QueryString : ?controller_id={controller_id}&switch_id={switch_id}&port_name={port_name}&vlan_id={vlan_id}&no_vlan_id={no_vlan_id}&srcmacaddr={srcmacaddr}
- Request Elements
      - controller_id  :Controller ID. (31 char)
      - switch_id  :Switch ID. 
      - port_name  :Port name. 
      - vlan_id  :VLAN ID. 
      - no_vlan_id  :No VLAN ID. 
      - srcmacaddr  :Source MAC address.  
- Response
```javascript
{
 "dataflows": [
    {
       "reason": "{reason}",
       "controller_dataflows": [
              {
               "controller_id": "{controller_id}",
               "controller_type": "{controller_type}",
               "flow_id": "{flow_id}",
               "status": "{status}",
               "type": "{type}",
               "policy_index": "{policy_index}",
               "vtn_id": "{vtn_id}",
               "ingress_switch_id": "{ingress_switch_id}",
               "ingress_port_name": "{ingress_port_name}",
               "ingress_station_id": "{ingress_station_id}",
               "ingress_domain_id": "{ingress_domain_id}",
               "egress_switch_id": "{egress_switch_id}",
               "egress_port_name": "{egress_port_name}",
               "egress_station_id": "{egress_station_id}",
               "egress_domain_id": "{egress_domain_id}",
          "match": {
             "inport": [
                    "{inport}"
              ],
             "macdstaddr": [
                    "{macdstaddr}"
              ],
             "macdstaddr_mask": [
                    "{macdstaddr_mask}"
              ],
             "macsrcaddr": [
                    "{macsrcaddr}"
              ],
             "macsrcaddr_mask": [
                    "{macsrcaddr_mask}"
              ],
             "macethertype": [
                    "{macethertype}"
              ],
              "vlan_id": [
                     "{vlan_id}"
              ],
              "vlan_priority": [
                     "{vlan_priority}"
              ],
             "iptos": [
                     "{iptos}"
              ],
             "ipproto": [
                     "{ipproto}"
              ],
             "ipdstaddr": [
                     "{ipdstaddr}"
              ],
             "ipdstaddr_mask": [
                     "{ipdstaddr_mask}"
              ],
             "ipsrcaddr": [
                     "{ipsrcaddr}"
              ],
             "ipsrcaddr_mask": [
                     "{ipsrcaddr_mask}"
              ],
             "l4dstport_icmptype": [
                     "{l4dstport_icmptype}"
             ],
             "l4dstport_icmptype_mask": [
                     "{l4dstport_icmptype_mask}"
             ],
             "l4srcport_icmptype": [
                     "{l4srcport_icmptype}"
             ],
             "l4srcport_icmptype_mask": [
                     "{l4srcport_icmptype_mask}"
             ],
             "ipv6dstaddr": [
                     "{ipv6dstaddr}"
             ],
            "ipv6dstaddr_mask": [
                     "{ipv6dstaddr_mask}"
             ],
            "ipv6srcaddr": [
                     "{ipv6srcaddr}"
             ],
            "ipv6srcaddr_mask": [
                     "{ipv6srcaddr_mask}"
             ]
          },
       "action": {
           "outputport": [
                   "{outputport}"
            ],
           "enqueueport": [
                   "{enqueueport}"
            ],
           "queue_id": [
                   "{queue_id}"
            ],
           "setmacdstaddr": [
                    "{setmacdstaddr}"
            ], 
           "setmacsrcaddr": [
                    "{setmacsrcaddr}"
            ],
           "setvlan_id": [
                    "{setvlan_id}"
            ],
           "setvlan_priority": [
                    "{setvlan_priority}"
            ],
           "setipdstaddr": [
                    "{setipdstaddr}"
            ],
           "setipsrcaddr": [
                    "{setipsrcaddr}"
            ],
           "setiptos": [
                    "{setiptos}"
            ],
           "setl4dstport_icmptype": [
                    "{setl4dstport_icmptype}"
            ],
           "setl4srcport_icmptype": [
                    "{setl4srcport_icmptype}"
            ],
            "setipv6dstaddr": [
                    "{setipv6dstaddr}"
            ],
            "setipv6srcaddr": [
                    "{setipv6srcaddr}"
            ],
            "stripvlan": "{stripvlan}"
         },
      "pathinfos": [
      {
        "switch_id": "{switch_id}",
        "in_port_name": "{in_port_name}",
        "out_port_name": "{out_port_name}"
       }
    ]
   }
  ]
 }
]
}
```
- Response Elements
      - reason :Data flows traversal status. 
           - Valid value: success / exceeds_flow_limit / exceeds_hop_limit / dst_not_reached / controller_disconnected / operation_not_supported / flow_not_found / system_error 
           - controller_dataflows Controller Data Flows information

### VTN Data Flows Functions
***현재 버전에서 지원하지 않음 (생략)***

### VTN Flow Filter Functions
##### Create VTN Flow Filter :VTN 플로우 필터를 생성한다. 
- Method : POST
- Request URI : /vtns/{vtn_name}/flowfilters
- Request
```javascript
{
 "flowfilter": {
    "ff_type": "{ff_type}"
  }
}
```
- Request Elements
      - ff_type :입/출력 필터
- Response : 없음

##### Delete VTN Flow Filter :VTN 플로우 필터를 삭제한다. 
- Method : POST
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}
- Response : 없음

##### Show VTN Flow Filter :VTN 플로우 필터를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}
- Response
```javascript
{
 "flowfilter": {
    "ff_type": "{ff_type}"
  }
}
```

### VTN Flow Filter Entry functions
##### Create VTN Flow Filter Entry :VTN 플로우 필터 항목을 생성한다. 
- Method : POST
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries
- Request
```javascript
{
"flowfilterentry": {
     "seqnum": "{seqnum}",
     "fl_name": "{fl_name}",
     "action_type": "{action_type}",
     "nmg_name": "{nmg_name}",
     "priority": "{priority}",
     "dscp": "{dscp}"
     }
}
```
- Request Elements
      - action_type :Action type.
      - nmg_name :Network monitor group name. (31 char)
      - priority :The packet transfer priority order
      - dscp :The DSCP value. 
- Response : 없음

##### Delete VTN Flow Filter Entry :VTN 플로우 필터 항목을 삭제한다. 
- Method : DELETE
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}
- Response : 없음

##### Update VTN Flow Filter Entry :VTN 플로우 필터 항목을 업데이트한다. 
- Method : PUT
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}
- Request
```javascript
{
 "flowfilterentry": {
    "fl_name": "{fl_name}",
    "action_type": "{action_type}",
    "nmg_name": "{nmg_name}",
    "priority": "{priority}",
    "dscp": "{dscp}"
    }
}
```
- Request Elements (Create VTN Flow Filter Entry 참고)
- Response : 없음

##### List VTN Flow Filter Entries :VTN 플로우 필터 항목 정보 목록을 보여준다. 
- Method : GET
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries, /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/detail, /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/count
- QueryString :?index={seqnum}&max_repetition={max_repetition}
- Response (/vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/detail의 경우)
```javascript 
{
  "flowfilterentries": [
   {
    "seqnum": "{seqnum}",
    "fl_name": "{fl_name}",
    "action_type": "{action_type}",
    "nmg_name": "{nmg_name}",
    "priority": "{priority}",
    "dscp": "{dscp}"
    }
   ]
}
```
- Response Elements (Create VTN Flow Filter Entry 참고)

##### Show VTN Flow Filter Entry :VTN 플로우 필터 항목 정보를 보여준다. 
- Method : GET
- Request URI : /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}, /vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}/detail
- QueryString :?controller_id={controller_id}&domain_id={domain_id}
- Request Elements
      - controller_id :Controller identifier. (31 char)
      - domain_id :Domain identifier. (31 char)
- Response (/vtns/{vtn_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}/detail의 경우)
```javascript 
{
  "flowfilterentry": {
  "seqnum": "{seqnum}",
  "fl_name": "{fl_name}",
  "action_type": "{action_type}",
  "nmg_name ": "{nmg_name}",
  "priority": "{priority}",
  "dscp": "{dscp}",
  "nmg_status": "{nmg_status}",
  "statistics": {
       "software": {
          "packets": "{packets}",
          "octets": "{octets}"
         },
       "existingflow": {
          "packets": "{packets}",
          "octets": "{octets}"
         },
       "expiredflow": {
          "packets": "{packets}",
          "octets": "{octets}"
         },
        "total": {
          "packets": "{packets}",
          "octets": "{octets}"
        }
      },
      "flowlist": {
        "flowlistentries": [
           {
         "seqnum": "{seqnum}",
         "statistics": {
               "software": {
                      "packets":
                "{packets}",
                      "octets":
                "{octets}"
                 },
               "existingflow": {
                       "packets":
                "{packets}",
                       "octets":
                "{octets}"
                },
               "expiredflow": {
                       "packets":
                "{packets}",
                       "octets":
                "{octets}"
                },
               "total": {
                       "packets":
               "{packets}",
                       "octets":
                "{octets}"
                }
            }
         }
       ]
    }
  }
}
```
- Response Elements
      - nmg_status :Status of monitored host.
      - statistics :Statistical information.
      - software :VTN을 통해 지나가는 플로우중 플로우 필터와 일치하는 패킷의 개수 또는 바이트 수
      - existingflow :OFS에 설정된 현재 플로우 엔트리에 의해 hard-transferred된 플로우중 플로우 필터 항목과 일치하는 패킷의 개수 또는 바이트수 
      - expiredflow :OFS에 설정된 이전의 플로우 엔트리에 의해 hard-transferred된 플로우중 플로우 필터 항목과 일치하는 패킷의 개수 또는 바이트수 
      - total :플로우 필터 엔트리와 일치하는 플로우의 전체 패킷의 개수 또는 바이트수. 이것은 Software, ExistingFlow, ExpiredFlow의 합과 같다. 
      - packets :Number of frames. 
      - octets :Number of octets in the frames.  

### vBridge Functions
##### Create vBridge :vBridge를 생성한다.
- Method : POST
- Request URI : /vtns/{vtn_name}/vbridges
- Request 
```javascript 
{
       "vbridge": {
           "vbr_name": "{vbr_name}",
           "controller_id":
         "{controller_id}",
           "description":
         "{description}",
           "domain_id": "{domain_id}"
            }
 }
```
- Request Elements
      - vbr_name :vBridge name. (31 char)
      - controller_id :Identifier of the Controller. (31 char)
      - domain_id :Domain identifier. (31 char)
- Response :Response codes

##### Delete vBridge :vBridge를 삭제한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}
- Response :Response codes

##### Update  vBridge :vBridge를 업데이트한다.
- Method : PUT
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}
- Request 
```javascript 
{
   "vbridge": {
       "description": "{description}"
   }
 }
```
- Response :Response codes

##### List vBridge :vBridge의 정보의 목록을 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges, /vtns/{vtn_name}/vbridges/detail, /vtns/{vtn_name}/vbridges/count
- QueryString : ?index={vbr_name}&max_repetition={max_repetition}
- Response (/vtns/{vtn_name}/vbridges/detail의 경우)
```javascript 
{
"vbridges": [
    {
     "vbr_name": "{vbr_name}",
     "controller_id": "{controller_id}",
     "domain_id": "{domain_id}",
     "description": "{description}",
     "status": "{status}"
     }
 ]
}
```
- Response Elements  (Create vBridge 참조)

##### Show vBridge :vBridge의 정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}
- Response 
```javascript 
{
  "vbridge": {
     "vbr_name": "{vbr_name}",
     "controller_id": "{controller_id}",
     "domain_id": "{domain_id}",
     "description": "{description}",
     "status": "{status}"
   }
 }
```
- Response Elements  (Create vBridge 참조)

### Host Address Functions
***현재 버전에서 지원하지 않음 (생략)***

### L2 Domain Function
***현재 버전에서 지원하지 않음 (생략)***

### MAC Entry Function
***현재 버전에서 지원하지 않음 (생략)***

### VLAN Map Functions
##### Create VLAN Map :VLAN map을 생성 한다.
- Method : POST
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps.json
- Request 
```javascript 
{
    "vlanmap": {
       "logical_port_id":
     "{logical_port_id}",
       "vlan_id": "{vlan_id}",
       "no_vlan_id":
     "{no_vlan_id}"
        }
}
```
- Request Elements
      - vbr_name :vBridge name. (31 char)
      - logical_port_id :Logical port identifier. (319 char)
      - vlan_id :Identifier of the mapped VLAN.
      - no_vlan_id :Indicates that no vlan_id is used.
- Response 
```javascript 
{
   "vlanmap": {
       "vlanmap_id":
    "{vlanmap_id}"
     }
}
```
- Request Elements
      - vlanmap_id :VLAN Map identifier. If logical_port_id is specified at creation time, vlanmap_id is "lpid-{logical_port_id}". 

##### Delete VLAN Map :VLAN map을 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps/{vlanmap_id}.json
- Request Elements (Create VLAN Map 참조)
- Response :Response codes
 
##### Update VLAN Map :VLAN map을 Update 한다.
- Method : PUT
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps/{vlanmap_id}.json
- Request 
```javascript 
{
    "vlanmap": {
        "vlan_id": "{vlan_id}",
     "no_vlan_id":
  "{no_vlan_id}"
        }
}
```
- Request Elements (Create VLAN Map 참조)
- Response :Response codes

##### List VLAN Map :VLAN map 정보 목록을 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps.json, /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps/detail.json, /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps/count.json
- QueryString : ?index={vlanmap_id}&max_repetition={max_repetition}
- Response 
```javascript 
{
   "vlanmaps": [
        {
      "vlanmap_id":
   "{vlanmap_id}",
      "logical_port_id":
   "{logical_port_id}",
      "vlan_id":
   "{vlan_id}",
      "no_vlan_id":
   "{no_vlan_id}"
        }
    ]
}
```
- Response Elements (Create VLAN Map 참조)

##### Show VLAN Map :VLAN map 정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/vlanmaps/{vlanmap_id}.json
- Response 
```javascript 
{
     "vlanmap": {
          "vlanmap_id":
    "{vlanmap_id}",
          "logical_port_id":
    "{logical_port_id}",
          "vlan_id": "{vlan_id}",
    "no_vlan_id":
          "{no_vlan_id}"
      }
 }
```
- Response Elements (Create VLAN Map 참조)

### vBridge Flow Filter Functions
##### Create vBridge Flow Filter :vBridge Flow Filter를 생성 한다.
- Method : POST
- Request URI :/vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters
- Request 
```javascript 
{
 "flowfilter": {
    "ff_type": "{ff_type}"
 }
}
```
- Request Elements
      - ff_type :Direction to which the Flow Filter is applied Valid value.
- Response :없음

##### Delete vBridge Flow Filter :vBridge Flow Filter를 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}
- Response :없음

##### Show vBridge Flow Filter :vBridge Flow Filter 정보 목록을 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}
- Response 
```javascript 
{
 "flowfilter": {
     "ff_type": "{ff_type}"
  }
}
```

### vBridge Flow Filter Entry Functions
##### Create vBridge Flow Filter Entry:vBridge Flow Filter Entry를 생성 한다.
- Method : POST
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries
- Request 
```javascript 
{
 "flowfilterentry": {
        "seqnum": "{seqnum}",
        "fl_name": "{fl_name}",
        "action_type": "{action_type}",
        "nmg_name": "{nmg_name}",
        "priority": "{priority}",
        "dscp": "{dscp}",
        "redirectdst": {
             "vnode_name": "{vnode_name}",
             "if_name": "{if_name}",
             "direction": "{direction}",
             "macdstaddr": "{macdstaddr}",
             "macsrcaddr": "{macsrcaddr}"
        }
  }
}
```
- Request Elements
      - seqnum :The sequence number.  
      - fl_name :Flow List name. (31 char)
      - action_type :Action that is registered in the Flow Filter entry.
           - pass: Passes the frame. 
           - drop: Discards the frame. 
           - redirect: Transfers a frame to the virtual interface of the virtual node in which the frame is specified. 
      - nmg_name :Network monitor group name.
      - priority :Priority value registered to the Flow Filter entry.
      - dscp :The DSCP value.  
      - vnode_name :Redirect destination virtual node name. 
      - if_name :A virtual interface of a redirect destination virtual node. 
      - direction :Direction. The value that can be specified differ depending on the Interface type specified in vnode_n ame and if_name. 
           - vBridge Interface: in, out ("out" can be specified when the vBridge Interface is set to vLink with boundary map or it has Port Map.) 
           - vTerminal Interface: out 
           - vRouter Interface: in 
      - macdstaddr :Destination MAC address.
      - macsrcaddr :Source MAC address.  
- Response :없음

##### Delete vBridge Flow Filter Entry:vBridge Flow Filter Entry를 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}
- Request Elements (Create vBridge Flow Filter Entry 참조)
- Response :없음
 
##### Update vBridge Flow Filter Entry:vBridge Flow Filter Entry를 Update 한다.
- Method : PUT
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}
- Request 
```javascript 
{
  "flowfilterentry": {
        "fl_name": "{fl_name}",
        "action_type": "{action_type}",
        "nmg_name": "{nmg_name}",
        "priority": "{priority}",
        "dscp": "{dscp}",
        "redirectdst": {
             "vnode_name": "{vnode_name}",
             "if_name": "{if_name}",
             "direction": "{direction}",
             "macdstaddr": "{macdstaddr}",
             "macsrcaddr": "{macsrcaddr}"
         }
   }
}
```
- Request Elements (Create vBridge Flow Filter Entry 참조)
- Response :없음

##### List vBridge Flow Filter Entry:vBridge Flow Filter Entry 정보 목록을 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries, /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/detail, /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/count
- QueryString : ?index={seqnum}&max_repetition={max_repetition} 
- Response (If detail is specified in URI )
```javascript 
{
    "flowfilterentries": [
         {
             "seqnum": "{seqnum}",
             "fl_name":
             "{fl_name}",
             "action_type":
             "{action_type}",
             "nmg_name":
          "{nmg_name}",
             "priority":
          "{priority}",
             "dscp": "{dscp}",
             "redirectdst": {
                      "vnode_name":
                 "{vnode_name}",
                      "if_name":
                 "{if_name}",
                      "direction":
                 "{direction}",
                      "macdstaddr":
                 "{macdstaddr}",
                      "macsrcaddr":
                 "{macsrcaddr}"
         }
    }
  ]
}
```
- Response Elements (Create vBridge Flow Filter Entry 참조)
 
 ##### Show vBridge Flow Filter Entry:vBridge Flow Filter Entry 정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}, /vtns/{vtn_name}/vbridges/{vbr_name}/flowfilters/{ff_type}/flowfilterentries/{seqnum}/detail
- Response (If detail is specified in URI )
```javascript 
{
  "flowfilterentry": {
        "seqnum": "{seqnum}",
        "fl_name": "{fl_name}",
        "action_type":
     "{action_type}",
        "nmg_name ": "{nmg_name}",
     "priority": "{priority}",
        "dscp": "{dscp}",
     "nmg_status":
        "{nmg_status}",
     "redirectdst": {
        "vnode_name":
     "{vnode_name}",
        "if_name":
     "{if_name}",
        "direction":
     "{direction}",
        "macdstaddr":
     "{macdstaddr}",
        "macsrcaddr":
     "{macsrcaddr}"
   },
"statistics": {
        "software": {
               "packets":
          "{packets}",
               "octets":
          "{octets}"
 },
"existingflow": {
        "packets":
     "{packets}",
        "octets":
     "{octets}"
 },
"expiredflow": {
       "packets":
     "{packets}",
       "octets":
     "{octets}"
 },
"total": {
      "packets":
    "{packets}",
      "octets":
    "{octets}"
 }
},
"flowlist": {
    "flowlistentries": [
        {
          "seqnum":
       "{seqnum}",
          "statistics":
                {
                "software": {
                     "packets": "{packets}",
                     "octets": "{octets}"
                 },
                "existingflow": {
                     "packets": "{packets}",
                     "octets": "{octets}"
                 },
                "expiredflow": {
                     "packets": "{packets}",
                     "octets": "{octets}"
                 },
                 "total": {
                     "packets": "{packets}",
                     "octets": "{octets}"
                 }
         }
      }
    ]
  }
 }
}
```
- Response Elements
      - nmg_status :Status of monitored host.  
      - redirectdst :Redirect information. statistics Statistical information. 
      - flowlist :Flow List information.  
      - flowlistentries :Flow List entry list.  

### vBridge Interface Functions
##### Create vBridge Interface :vBridge Interface를 생성 한다.
- Method : POST
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces
- Request
```javascript 
{
   "interface": {
     "if_name": "{if_name}",
     "description":
     "{description}",
     "adminstatus":
     "{adminstatus}"
   }
}
```
- Response :Response codes
 
##### Delete vBridge Interface :vBridge Interface를 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}
- Response :Response codes

##### Update vBridge Interface :vBridge Interface를 Update 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}
- Request
```javascript 
{
  "interface": {
        "description":
  "{description}",
  "adminstatus":
  "{adminstatus}"
  }
}
```
- Request Elements
      - description :Additional information. (127 char)
      - adminstatus :Admin status.  
- Response :Response codes
 
##### List vBridge Interface :vBridge Interface정보 목록을 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces, /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/detail, /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/count
- Response (If detail is specified in URI )
```javascript 
{
   "interfaces": [
         {
         "if_name":
     "{if_name}",
         "description":
     "{description}",
         "adminstatus":
     "{adminstatus}",
         "operstatus":
     "{operstatus}",
         "neighbor": {
             "vnode_name":
        "{vnode_name}",
                "if_name":
        "{if_name}",
                "vlk_name":
        "{vlk_name}"
          }
       }
     ]
}
```
- Response Elements
      - operstatus :Operational status.  
      - neighbor :Information about the neighbor.  
      - count :The number of vBridge Interface.
      - if_name :vBridge Interface name.  (31 char)
      - vnode_name :Virtual node name.  (31 char)
      - vlk_name :vLink name.  (31 char)
 
##### Show vBridge Interface :vBridge Interface 정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}
- Response 
```javascript 
{ 
    "interfaces": {
         "if_name": "{if_name}",
         "description":
      "{description}",
         "adminstatus":
      "{adminstatus}",
         "operstatus":
      "{operstatus}",
         "neighbor": {
                 "vnode_name":
            "{vnode_name}",
                 "if_name":
            "{if_name}",
                 "vlk_name":
            "{vlk_name}" 
                }
          }
}
```
- Response Elements (List vBridge Interface 참조)

### vBridge Interface Port Map Functions
##### Create vBridge Interface Port Map :vBridge Interface Port Map을 생성 한다.
- Method : PUT
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/portmap
- Request
```javascript 
{
   "portmap": {
   "logical_port_id":
   "{logical_port_id}",
   "vlan_id": "{vlan_id}",
   "tagged": "{tagged}"
   }
}
```
- Request Elements
      - logical_port_id :Logical port identifier.  (319 char)
      - vlan_id :Identifier of the mapped VLAN.  
      - tagged :Displays whether VLAN tags are sent and received in the Physical network.  
- Response :Response codes

##### Delete vBridge Interface Port Map :vBridge Interface Port Map을 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/portmap
- Response :Response codes
 
##### Show vBridge Interface Port Map :vBridge Interface Port Map정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/portmap
- Response 
```javascript 
{
   "portmap": {
   "logical_port_id":
   "{logical_port_id}",
   "vlan_id": "{vlan_id}",
   "tagged": "{tagged}"
   }
}
```

### vBridge Interface Flow Filter Functions
##### Create vBridge Interface Flow Filter :vBridge Interface Flow Filter을 생성 한다.
- Method : POST
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/flowfilters
- Request
```javascript 
{
 "flowfilter": {
      "ff_type": "{ff_type}"
  }
}
```
- Response :없음

##### Delete vBridge Interface Flow Filter :vBridge Interface Flow Filter을 삭제 한다.
- Method : DELETE
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/flowfilters/{ff_type} 
- Response :없음

##### Show vBridge Interface Flow Filter :vBridge Interface Flow Filter정보를 보여준다.
- Method : GET
- Request URI : /vtns/{vtn_name}/vbridges/{vbr_name}/interfaces/{if_name}/flowfilters/{ff_type}
- Response 
```javascript 
{
 "flowfilter": {
     "ff_type": "{ff_type}"
  }
}
```

 



