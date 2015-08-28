Orchestration (Heat) API
===================

개요
----
Openstack Heat의 Orchestration REST API를 분석 한다.


OpenStack Orchestration REST API 
-----------------------
### API Version 
##### List versions :모든 Orchestration API 버전 목록을 보여준다.
- Method : GET
- Request URI : /
- Response 
```javascript
{
    "versions": [
        {
            "status": "CURRENT",
            "id": "v1.0",
            "links": [
                {
                    "href": "http://23.253.228.211:8000/v1/",
                    "rel": "self"
                }
            ]
        }
    ]
}
```

### Stacks
##### Create stack :stack 을 생성 한다. 
- Method : POST
- Request URI : /v1/?{tenant_id}?/stacks
- Request
```javascript
{
    "files": {},
    "disable_rollback": true,
    "parameters": {
        "flavor": "m1.heat"
    },
    "stack_name": "teststack",
    "template": {
        "heat_template_version": "2013-05-23",
        "description": "Simple template to test heat commands",
        "parameters": {
            "flavor": {
                "default": "m1.tiny",
                "type": "string"
            }
        },
        "resources": {
            "hello_world": {
                "type": "OS::Nova::Server",
                "properties": {
                    "key_name": "heat_key",
                    "flavor": {
                        "get_param": "flavor"
                    },
                    "image": "40be8d1a-3eb9-40de-8abd-43237517384f",
                    "user_data": "#!/bin/bash -xv\necho \"hello world\" &gt; /root/hello-world.txt\n"
                }
            }
        }
    },
    "timeout_mins": 60
}
```
- Request Elements
     - tenant_id :The ID of the tenant. A tenant is also known as an account or project. 
     - stack_name :A name for the new stack. 
     - template_url(Optional) :A URI to the location containing the stack template on which to perform the specified operation.
     - template (Optional) :The stack template on which to perform the specified operation. 
        - This parameter is always provided as a string in the JSON request body. 
        - The content of the string is a JSON- or YAML-formatted Orchestration template.
