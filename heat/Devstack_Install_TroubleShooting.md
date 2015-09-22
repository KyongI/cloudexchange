DevStack Control/Compute Node 설치 문제 해결
===========================================

##### error in setup command: Invalid environment marker: (python_version=='2.7') 
- 해결 방법 :
```
해당 *.py 파일을 열어서 (다음과 같이 바꾼다. 왠일인지 주석으로는 반영되지 않았음)
- ldappool>=1.0:python_version=='2.7' 
+ ldappool>=1.0
```

##### create_network_postcommit failed.
```
2015-09-15 05:09:05.317 | ++ neutron net-create --tenant-id c9c0a95dd6564175939baf46fa012d72 private
2015-09-15 05:09:05.317 | ++ read data
2015-09-15 05:09:06.674 | create_network_postcommit failed.
2015-09-15 05:09:06.750 | + NET_ID=
2015-09-15 05:09:06.750 | + die_if_not_set 532 NET_ID 'Failure creating NET_ID for  c9c0a95dd6564175939baf46fa012d72'
2015-09-15 05:09:06.750 | + local exitcode=0
2015-09-15 05:09:06.758 | [Call Trace]
2015-09-15 05:09:06.758 | ./stack.sh:1293:create_neutron_initial_network
2015-09-15 05:09:06.758 | /home/stack/devstack/lib/neutron:532:die_if_not_set
2015-09-15 05:09:06.759 | /home/stack/devstack/functions-common:284:die
2015-09-15 05:09:06.789 | [ERROR] /home/stack/devstack/functions-common:532 Failure creating NET_ID for c9c0a95dd6564175939baf46fa012d72
2015-09-15 05:09:07.811 | Error on exit
2015-09-15 05:09:07.968 | df: '/run/user/1000/gvfs': Permission denied
2015-09-15 05:09:07.968 | df: '/media/djkim/VBOXADDITIONS_5.0.2_102096': Permission denied
```
- 해결 방법
'create_network_postcommit failed' 발생하는 이유는 ODL 설치가 잘못 되어서 인데. VTN manager 가 설지 되지 않은 문제.
