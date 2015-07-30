Multiple Cloud Heat Manager의 멀티 계정 관리 모듈(멀티 오픈스택 서비스 환경하에서 계정 관리)

. 관리자: 오픈스택 서비스들을 통합관리한다. 사용자들을 생성한다. 
. 사용자: 사용자는 오픈스택 서비스 리스트에서 원하는 서비스를 이용한다.
. 통합계정 관리에서는 멀티 오픈스택 서비스 계정들을 관리하고, 자원을 이용할 수 있도록 한다. 
  2개 이상의 서비스간에 가상 네트워크를 구성해 이용할 수 있다. 멀티 클라우드 VTN 오케스트레이션 API 호출은 '오픈스택 API 호출 분배기'로 전달되고, 
  다시 개별 오픈스택 API 호출로 이어진다.


* 사용자 
사용자  생성
 . URL: /v1/users/
 . Method: POST
 . 설명: user생성, (멀티 오픈스택 환경하에서..) 디폴트 오픈스택 지정
 
사용자  조회
 . URL: /v1/users/{user_id}
 . Method: GET
 . 설명: user의 상세 정보 + (detail: 오픈스택 키스톤 통합계정 정보들 포함)
 
 사용자  갱신
 . URL: /v1/users/{user_id}
 . Method: PUT
 . 설명: user의 정보 갱신 + 오픈스택 추가
 
 사용자 목록 
 . URL: /v1/users/
 . Method: GET
 . 사용자 목록 반환
 
사용자 삭제
 . URL: /v1/users/{user_id}
 . Method: DELETE
 . 사용자 목록 삭제 

통합계정 인증 
 . URL: /v1/session/
 . Method: POST
 . 설명: Response 값 중 key 를 Auth token으로 사용. 멀티 오픈스택의 인증을 대신한다(키스톤 토큰값들을 관리)
 
* 오픈스택 서비스
오픈스택 서비스 생성 
 . URL: /v1/services/
 . Method: POST
 . 설명: 오픈스택 서비스들 생성 

오픈스택 서비스 조회
 . URL: /v1/services/{service_id}
 . Method: GET
 . 설명: 오픈스택 서비스들 조회

오픈스택 서비스 갱신
 . URL: /v1/services/{service_id}
 . Method: PUT
 . 설명: 오픈스택 서비스 갱신 . 서비스 api 위치, 설명

오픈스택 서비스 삭제
 . URL: /v1/services/{service_id}
 . Method: DELETE
 . 설명: 오픈스택 서비스 삭제

