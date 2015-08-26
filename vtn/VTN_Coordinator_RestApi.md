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
####### Response 메세지는 XML과 JSON 을 지원.

VTN 코디네이터 REST API 
-----------------------
#### Show API Version 
- Method : GET
- Request URI : /api_version
- Element : VTN API의 버젼. Vn.n (n은 양의 정수)
- Response 
    {
        "api_version": {
            "version": "{version}"
        }
    }

#### Show Coordinator Version
- Method : GET
- Request URI : /coordinator_version
- Element : VTN 코디네이터의 버젼. Va.b.c.d (a - major, b - minor, c - revision, d - patch level.)
- Response 
    {
        "coordinator_version": {
        "version": "{version}",
        "patches": [
          {
            "patch_no": "{patch_no}"
          }
        ]
    }









