DevStack Control/Compute Node 설치 문제 해결
===========================================

##### error in setup command: Invalid environment marker: (python_version=='2.7') 
- 해결 방법 :
```
해당 *.py 파일을 열어서 (다음과 같이 바꾼다. 왠일인지 주석으로는 반영되지 않았음)
- ldappool>=1.0:python_version=='2.7' 
+ ldappool>=1.0
```

