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
- Request URI : /v1/{tenant_id}/stacks
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
     - template_url (Optional) :특별한 작업을 수행하는 stack 템플릿이 위치한 URI이다. 
     - template (Optional) :The stack template on which to perform the specified operation. 
        - This parameter is always provided as a string in the JSON request body. 
        - The content of the string is a JSON- or YAML-formatted Orchestration template.
     - files (Optional) :Supplies the contents of files referenced in the template or the environment. 
     - parameters (Optional) :Supplies arguments for parameters defined in the stack template. 
     - tags (Optional) :One or more simple string tags to associate with the stack.
- Response 
```javascript
{
    "stack": {
        "id": "3095aefc-09fb-4bc7-b1f0-f21a304e864c",
        "links": [
            {
                "href": "http://192.168.123.200:8004/v1/eb1c63a4f77141548385f113a28f0f52/stacks/simple_stack/3095aefc-09fb-4bc7-b1f0-f21a304e864c",
                "rel": "self"
            }
        ]
    }
}
```
- Response Elements
     - environment (Optional) :A JSON environment for the stack. 
     - param_name-n (Optional) :User-defined parameter names to pass to the template. 
     - param_value-n (Optional) :User-defined parameter values to pass to the template. 
     - timeout_mins (Optional) :The timeout for stack creation in minutes. 
     - disable_rollback (Optional) :Enables or disables deletion of all previously-created stack resources when stack creation fails.
     - stack_id :The system-assigned ID for the stack. 
     - links :A list of URLs for the stack. 
     - rel :A reference to the stack's parent. If no parent, reference is self. 
 
##### Adopt stack :존재하는 리소스로 부터 stack 을 생성 한다. 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks
- Request
```javascript
{
    "adopt_stack_data": {
        "action": "CREATE",
        "id": "bxxxxx4-0xx2-4xx1-axx6-exxxxxxxc",
        "name": "teststack",
        "resources": {
            "MyServer": {
                "action": "CREATE",
                "metadata": {},
                "name": "MyServer",
                "resource_data": {},
                "resource_id": "cxxxx3-dxx3-4xx-bxx2-3xxxxxxxxa",
                "status": "COMPLETE",
                "type": "OS::Trove::Instance"
            }
        },
        "status": "COMPLETE",
        "template": {}
    },
    "stack_name": "{stack_name}",
    "template_url": "{template_url}",
    "timeout_mins": "{timeout_mins}"
}
```
- Request Elements
     - adopt_stack_data :Existing resources data to adopt a stack. Data returned by abandon stack could be provided as adopt_stack_data. 
- Response 
```javascript
{
    "action": "CREATE",
    "id": "46c927bb-671a-43db-a29c-16a2610865ca",
    "name": "trove",
    "resources": {
        "mysql_server": {
            "action": "CREATE",
            "metadata": {},
            "name": "mysql_server",
            "resource_data": {},
            "resource_id": "74c5be7e-3e62-41e7-b455-93d1c32d56e3",
            "status": "COMPLETE",
            "type": "OS::Trove::Instance"
        }
    },
    "status": "COMPLETE",
    "template": {
        "heat-template-version": "2013-05-23",
        "description": "MySQL server instance",
        "parameters": {
            "instance_name": {
                "description": "The database instance name",
                "type": "string"
            }
        },
        "resources": {
            "mysql_server": {
                "properties": {
                    "databases": [
                        {
                            "name": "testdbonetwo"
                        }
                    ],
                    "flavor": "m1.medium",
                    "name": "test-trove-db",
                    "size": 30,
                    "users": [
                        {
                            "databases": [
                                "testdbonetwo"
                            ],
                            "name": "testuser",
                            "password": "testpass123"
                        }
                    ]
                },
                "type": "OS::Trove::Instance"
            }
        }
    }
}
```

##### List stack data :stack 목록을 보여준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks
- Request
```javascript 
{
    "stacks": [
        {
            "creation_time": "2014-06-03T20:59:46Z",
            "description": "sample stack",
            "id": "3095aefc-09fb-4bc7-b1f0-f21a304e864c",
            "links": [
                {
                    "href": "http://192.168.123.200:8004/v1/eb1c63a4f77141548385f113a28f0f52/stacks/simple_stack/3095aefc-09fb-4bc7-b1f0-f21a304e864c",
                    "rel": "self"
                }
            ],
            "stack_name": "simple_stack",
            "stack_status": "CREATE_COMPLETE",
            "stack_status_reason": "Stack CREATE completed successfully",
            "updated_time": "",
            "tags": ""
        }
    ]
}
```
- Request Elements
     - id (Optional) :Filters the stack list by a specified stack ID. 
     - status (Optional) :Filters the stack list by a specified status. 
     - name (Optional) :Filters the stack list by a specified name. 
     - action (Optional) :Filters the stack list by a specified action. 
     - tenant (Optional) :Filters the stack list by a specified tenant. 
     - username (Optional) :Filters the stack list by a specified user name. 
     - owner_id (Optional) :Filters the stack list by a specified owner ID, which is the ID of the parent stack of listed stack. 
     - limit (Optional) :Requests a specified page size of returned items from the query. 
     - marker (Optional) :Specifies the ID of the last-seen item. 
     - show_deleted (Optional) :Specifies whether to include deleted stacks in the list. 
     - show_nested (Optional) :Specifies whether to include nested stacks in the list. 
     - sort_keys (Optional) :Sorts the stack list by name, status, created_at, or updated_at key. 
     - tags (Optional) :Lists stacks that contain one or more simple string tags. 
     - tags_any (Optional) :Lists stacks that contain one or more simple string tags. 
     - not_tags (Optional) :Lists stacks that do not contain one or more simple string tags. 
     - not_tags_any (Optional) :Lists stacks that do not contain one or more simple string tags. 
     - sort_dir (Optional) :The sort direction of the list. A valid value is asc (ascending) or desc (descending). 
     - global_tenant (Optional) :Specifies whether to include stacks from all tenants in the stack list. Policy requirements are specified in the Orchestration policy.json file. 
     - with_count (Optional) Specifies whether to include a count key in the response. The count key value is the number of stacks that match the query criteria.


