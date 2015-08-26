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




