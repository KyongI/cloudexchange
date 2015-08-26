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
#### Show API Version 
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
#### Show Coordinator Version
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
#### Flow List Functions
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

#### Flow List Entry Functions
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

