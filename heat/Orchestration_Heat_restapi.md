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

***
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
            ...
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
            ...
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
        ...
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
            ...
        }
    }
}
```

##### List stack data :stack 목록을 보여준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks
- QueryString : ?id={id}&status={status}&name={name}&action={action}&tenant={tenant}&username={username}&owner_id={owner_id}&limit={limit}&marker={marker}&show_deleted={show_deleted}&show_nested={show_nested}&sort_keys={sort_keys}&tags={tags}&tags_any={tags_any}&not_tags={not_tags}&not_tags_any={not_tags_any}&sort_dir={sort_dir}&global_tenant={global_tenant}&with_count={with_count}
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
- Response 
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

##### Preview stack : 지정된 stack의 Preview를 보여 준다.
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/preview
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
            ...
        }
    },
    "timeout_mins": 60
}
```
- Response 
```javascript
{
    "stack": {
        "capabilities": [],
        "creation_time": "2015-01-31T15:12:36Z",
        "description": "HOT template for Nova Server resource.\n",
        "disable_rollback": true,
        "id": "None",
        "links": [
            {
                "href": "http://192.168.122.102:8004/v1/6e18cc2bdbeb48a5basad2dc499f6804/stacks/test_stack/None",
                "rel": "self"
            }
        ],
        "notification_topics": [],
        "parameters": {
            ...
        },
        "parent": null,
        "resources": [
            {
                ...
            },
            {
                "attributes": {
                    ...
                },
                "description": "",
                "metadata": {},
                "physical_resource_id": "",
                "properties": {
                    ...
                },
                "required_by": [],
                "resource_action": "INIT",
                "resource_identity": {
                    ...
                },
                "resource_name": "hello_world",
                "resource_status": "COMPLETE",
                "resource_status_reason": "",
                "resource_type": "OS::Nova::Server",
                "stack_identity": {
                    ...
                },
                "stack_name": "teststack",
                "updated_time": "2015-01-31T15:12:36Z"
            }
        ],
        "stack_name": "test_stack",
        "stack_owner": "admin",
        "template_description": "HOT template for Nova Server resource.\n",
        "timeout_mins": null,
        "updated_time": null
    }
}
```
- Response Elements
     - parent :The stack ID of the parent stack, if this is a nested stack. 
     - id :The stack ID. 
     - template_description :A description of the template that defines the stack. 
     - capabilities :List of stack capabilities for stack. 
     - notification_topics :List of notification topics for stack. 
     - updated_time :Time of last stack update in the following format: YYYY-MM-DDThh:mm:ssTZD, where TZD is the time zone designator. 
     - stack_owner :Stack owner name. 
     - parameters :List of parameters defined for the stack. 
     - resources :List of stack resources. 

##### Find stack : 지정된 스택에서 표준 URL을 찾는다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}
- Request
```javascript
{
    "stack": {
        "capabilities": [],
        "creation_time": "2014-06-04T20:36:12Z",
        "description": "sample stack",
        "disable_rollback": true,
        "id": "5333af0c-cc26-47ee-ac3d-8784cefafbd7",
        "links": [
            {
                ...
            }
        ],
        "notification_topics": [],
        "outputs": [],
        "parameters": {
            ...
        },
        "stack_name": "simple_stack",
        "stack_status": "CREATE_COMPLETE",
        "stack_status_reason": "Stack CREATE completed successfully",
        "template_description": "sample stack",
        "timeout_mins": null,
        "updated_time": null
    }
}
```
- Response :Response codes

##### Find stack resources : 지정된 스택의 리소스 목록을 위한 표준 URL을 찾는다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/resources
- Response :Response codes

##### Show stack details : 지정된 스택을 자세히 보여 준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Response 
```javascript
{
    "stack": {
        "capabilities": [],
        "creation_time": "2014-06-03T20:59:46Z",
        "description": "sample stack",
        "disable_rollback": "True",
        "id": "3095aefc-09fb-4bc7-b1f0-f21a304e864c",
        "links": [
            {
                ...
            }
        ],
        "notification_topics": [],
        "outputs": [],
        "parameters": {
            ...
        },
        "stack_name": "simple_stack",
        "stack_status": "CREATE_COMPLETE",
        "stack_status_reason": "Stack CREATE completed successfully",
        "template_description": "sample stack",
        "timeout_mins": "",
        "updated_time": "",
        "tags": ""
    }
}
```

##### Update stack : 지정된 스택을 업데이트 한다. 
- Method : PUT
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Request
```javascript
{
    "template": {
        "heat_template_version": "2013-05-23",
        "description": "Create a simple stack",
        "parameters": {
            "flavor": {
                "default": "m1.tiny",
                "type": "string"
            }
        },
        "resources": {
            ...
        }
    },
    "parameters": {
        "flavor": "m1.small"
    }
}
```
- Response :Response codes
 
##### Delete stack : 지정된 스택과 그 스택에 모든 snapshot들을 삭제한다. 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Response :Response codes
 
##### Abandon stack : 지정된 스택을 삭제는 하지만, 스텍과 리소스를 표현하는 반환 데이터와 리소스를 그대로 남겨둔다. 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/abandon
- Response 
```javascript
{
    "status": "COMPLETE",
    "name": "g",
    "dry_run": true,
    "template": {
        "outputs": {
            "instance_ip": {
                "value": {
                    "str_replace": {
                        "params": {
                            "username": "ec2-user",
                            "hostname": {
                                "get_attr": [
                                    "server",
                                    "first_address"
                                ]
                            }
                        },
                        "template": "ssh username@hostname"
                    }
                }
            }
        },
        "heat_template_version": "2013-05-23",
        "resources": {
            ...
        },
        "parameters": {
            "key_name": {
                "default": "heat_key",
                "type": "string"
            },
            "image": {
                "default": "fedora-amd64",
                "type": "string"
            },
            "flavor": {
                "default": "m1.small",
                "type": "string"
            }
        }
    },
    "action": "CREATE",
    "id": "16934ca3-40e0-4fb2-a289-a700662ec05a",
    "resources": {
        ...
    }
}
```

##### Snapshot stack : 스택에있는 모든 리소스의 스냅 샷을 얻는다. 모든 스냅 샷은 스택의 삭제시 삭제된다.
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots
- Request
```javascript
{
    "name": "vol_snapshot"
}
```
- Response 
```javascript
{
    "id": "13c3a4b5-0585-440e-85a4-6f96b20e7a78",
    "name": "vol_snapshot",
    "status": "IN_PROGRESS",
    "status_reason": null,
    "data": null
}
```

##### List snapshots : 스택 스냅 샷 목록을 보여 준다.
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots
- Response 
```javascript
{
    "snapshots": [
        {
            "id": "7c4e1ef4-bf1b-41ab-a0c8-ce01f4ffdfa1",
            "name": "vol_snapshot",
            "status": "IN_PROGRESS",
            "status_reason": null,
            "data": null
        }
    ]
}
```

##### Show snapshot : 지정된 스냅 샷을 자세히 보여 준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}
- Response 
```javascript
{
    "snapshot": {
        "id": "7c4e1ef4-bf1b-41ab-a0c8-ce01f4ffdfa1",
        "name": "vol_snapshot",
        "status": "COMPLETE",
        "status_reason": "Stack SNAPSHOT completed successfully",
        "data": {
            "status": "COMPLETE",
            "name": "stack_vol1",
            "stack_user_project_id": "fffa11067b1c48129ddfb78fba2bf09f",
            "environment": {
                "parameters": {},
                "resource_registry": {
                    "resources": {}
                }
            },
            "template": {
                "heat_template_version": "2013-05-23",
                "resources": {
                    ...
                }
            },
            "action": "SNAPSHOT",
            "project_id": "ecdb08032cd042179692a1b148f6565e",
            "id": "656452c2-e151-40da-8704-c844e69b485c",
            "resources": {
                ...
            }
        }
    }
}
```

##### Delete snapshot : 스냅 샷을 삭제 한다. 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}
- Response :Response codes
 
##### Restore snapshot : 스냅 샷을 복원 한다. 스냅 샷에서 활성화된 스택만 복원 가능하다. 삭제된 스택은 다시 생성해야만 한다. 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}/restore
- Response :Response codes

***
### Stacks actions
##### Suspend stack : stack을 보류 시킨다. (suspend)
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/actions
- Request
```javascript
{
    "suspend": null
}
```
- Request Elements
     - suspend :Specify the suspend action in the request body. 
- Response :Response codes

##### Resume stack: 보류되었던 stack을 재개한다.(resume)
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/actions
- Request
```javascript
{
    "resume": null
}
```
- Request Elements: 
     - resume :Specify the resume action in the request body. 
- Response :Response codes

##### Cancel stack update : 스택의 현재 실행중인 업데이트를 취소한다.
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/actions
- Request
```javascript
{
    "cancel_update": null
}
```
- Request Elements
     - cancel_update :Specify the cancel_update action in the request body. 
- Response :Response codes

##### Check stack resources : 지정된 스택의 상태에서 요청된 리소스인지 확인한다. 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/actions
- Request
```javascript
{
    "check": null
}
```
- Request Elements
     - check :Specify the check action in the request body. 
- Response :Response codes

***
### Stacks resources
##### List resources : stack의 리소스 목록을 보여준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/resources
- QueryString : ?nested_depth={nested_depth}&with_detail={with_detail}
- Request Elements
     - nested_depth (Optional) :Includes resources from nested stacks up to the nested_depth levels of recursion. 
     - with_detail (Optional) :Enables detailed resource information for each resource in list of resources. 
- Response 
```javascript
{
    "resources": [
        {
            "creation_time": "2015-06-25T14:59:53",
            "links": [
                {
                    "href": "http://hostname/v1/1234/stacks/mystack/629a32d0-ac4f-4f63-b58d-f0d047b1ba4c/resources/random_key_name",
                    "rel": "self"
                },
                {
                    "href": "http://hostname/v1/1234/stacks/mystack/629a32d0-ac4f-4f63-b58d-f0d047b1ba4c",
                    "rel": "stack"
                }
            ],
            "logical_resource_id": "random_key_name",
            "physical_resource_id": "mystack-random_key_name-pmjmy5pks735",
            "required_by": [],
            "resource_name": "random_key_name",
            "resource_status": "CREATE_COMPLETE",
            "resource_status_reason": "state changed",
            "resource_type": "OS::Heat::RandomString",
            "updated_time": "2015-06-25T14:59:53"
        }
    ]
}
```

##### Show resource data : 지정된 리소스의 데이터를 보여준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/resources/{resource_name}
- Request Elements
     - resource_name :The name of a resource in the stack. 
- Response 
```javascript
{
    "resource": {
        "attributes": {
            "value": "I9S20uIp"
        },
        "creation_time": "2015-06-25T14:59:53",
        "description": "",
        "links": [
            {
                "href": "http://hostname/v1/1234/stacks/mystack/629a32d0-ac4f-4f63-b58d-f0d047b1ba4c/resources/random_key_name",
                "rel": "self"
            },
            {
                "href": "http://hostname/v1/1234/stacks/mystack/629a32d0-ac4f-4f63-b58d-f0d047b1ba4c",
                "rel": "stack"
            }
        ],
        "logical_resource_id": "random_key_name",
        "physical_resource_id": "mystack-random_key_name-pmjmy5pks735",
        "required_by": [],
        "resource_name": "random_key_name",
        "resource_status": "CREATE_COMPLETE",
        "resource_status_reason": "state changed",
        "resource_type": "OS::Heat::RandomString",
        "updated_time": "2015-06-25T14:59:53"
    }
}
```

##### Show resource metadata : 지정된 리소스의 metadata를 보여 준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/resources/{resource_name}/metadata
- Response 
```javascript
{
    "metadata": {
        "some_key": "some_value",
        "some_other_key": "some_other_value"
    }
}
```

##### Send a signal to a resource : 지정된 리소스에 시그널을 보낸다. 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/resources/{resource_name}/signal
- Response :Response codes

***
### Stacks events
##### Find stack events : 지정된 스택의 이벤트 목록에 대한 표준 URL을 찾는다.
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/events
- Response :Response codes

##### List stack events : 지정된 스택의 이벤트 목록을 보여준다. 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/events
- QueryString : ?resource_action={resource_action}&resource_status={resource_status}&resource_name={resource_name}&resource_type={resource_type}&limit={limit}&marker={marker}&sort_keys={sort_keys}&sort_dir={sort_dir}
- Request Elements
     - resource_action (Optional) :지정된 리소스 동작에 의한 이벤트 목록을 필터링 한다. 다중 리소스 작업에 대해 필터링을 여러번 필터링 할 수 있다.
     - resource_status (Optional) :지정된 리소스 상태에 의한 이벤트 목록을 필터링 한다. 다중 리소스 작업에 대해 필터링을 여러번 필터링 할 수 있다.
     - resource_name (Optional) :지정된 리소스 이름에 의한 이벤트 목록을 필터링 한다. 다중 리소스 작업에 대해 필터링을 여러번 필터링 할 수 있다.
     - resource_type (Optional) :지정된 리소스 타입에 의한 이벤트 목록을 필터링 한다. 다중 리소스 작업에 대해 필터링을 여러번 필터링 할 수 있다.
     - limit (Optional) :쿼리에 응답 항목의 지정된 페이지 크기를 요청한다.  지정된 한계 값까지 항목의 수를 알려준다. 처음 limit 요청 이후 marker 파라미터의 응답으로부터 마지막 항목 ID를 사용하도록 limit 파라미터를 사용한다. 
     - marker (Optional) :마지막 항목 ID를 지정 한다. 
     - sort_keys (Optional) :Sorts the list by the resource_type or created_at key. 
     - sort_dir (Optional) :The sort direction of the list. 
- Response 
```javascript
{
    "events": [
        {
            ...
        },
        {
            ...
        }
    ]
}
```

##### List resource events : 지정된 스택의 리소스에 대한 이벤트 목록을 보여준다. 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/events
- QueryString : ?resource_action={resource_action}&resource_status={resource_status}&resource_name={resource_name}&resource_type={resource_type}&limit={limit}&marker={marker}&sort_keys={sort_keys}&sort_dir={sort_dir}
- Response 
```javascript
{
    "events": [
        {
            ...
        },
        {
            ...
        }
    ]
}
```

##### Show event details: 지정된 이벤트를 자세하게 보여준다. 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/events/​{event_id}​
- Response (누락되어 있음. 확인이 필요.)
- Response :Response codes

***
### Templates
##### Get stack template : 지정된 스택의 탬플릿을 얻어 온다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/template
- Response 
```javascript
{
    "description": "Hello world HOT template that just defines a single server. Contains just base features to verify base HOT support.\n",
    "heat_template_version": "2013-05-23",
    "outputs": {
        ...
    },
    "parameters": {
        ...
    },
    "resources": {
        ...
    }
}
```

##### List template versions : 사용가능한 모든 템플릿 버전 목록을 보여준다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/template_versions 
- Response :Response codes

##### Validate template : 지정한 템플릿을 검증 한다.
- Method : POST
- Request URI : /v1/​{tenant_id}​/validate
- Request
```javascript
{
    "template_url": "/PATH_TO_HEAT_TEMPLATES/WordPress_Single_Instance.template"
}
```
- Request Elements
     - template_url (Optional) :지정된 작업을 수행 할 스택 템플릿을 포함하는 URI 위치 이다. URI에 있는 예상 템플릿 콘텐츠에 대한 자세한 내용은 templete 파라미터에 대한 설명을 참조한다. templete 파라미터를 생략하는 경우 이 파라미터가 필요하다. 만약 두개의 파라미터를 같이 사용하면, 이 파라미터는 무시된다. 
     - template (Optional) :지정된 작업을 수행 할 스택 템플릿이다.
     - environment (Optional) :A JSON environment for the stack. 
- Response 
```javascript
{
    "Description": "A template that provides a single server instance.",
    "Parameters": {
        "server-size": {
            ...
        },
        "key_name": {
            ...
        },
        "server_name": {
            ...
        }
    },
    "ParameterGroups": [
        {
            "label": "Parameter groups",
            "description": "My parameter groups",
            "parameters": [
                "param_name-1",
                "param_name-2"
            ]
        }
    ]
}
```
- Response Elements
     - Parameters : An object that defines all input parameters that are defined in the template. Indexed by parameter name. 
     - ParameterGroups (Optional) : A list of parameter groups. Each group contains a list of parameter names. 

##### Show resource template : 지정된 리소스 타입에 대한 템플릿 representation을 보여줍니다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/resource_types/​{type_name}​/template
- QueryString : ?template_type={template_type}
- Request Elements
     - template_type (Optional) :The resource template type. Default type is cfn. The hot template type is supported. 
- Response 
```javascript
{
    "HeatTemplateFormatVersion": "2012-12-12",
    "Outputs": {
        ...
    },
    "Parameters": {
        ...
    },
    "Resources": {
        ...
    }
}
```

##### List resource types : 제공되는 탬플릿 리소스 타입의 목록을 보여준다. 
- Method : GET
- Request URI : /v1/​{tenant_id}​/resource_types
- Response 
```javascript
{
    "resource_types": [
        "AWS::EC2::Instance",
        "OS::Heat::ScalingPolicy",
        "AWS::CloudFormation::Stack",
        "OS::Keystone::Group",
        "OS::Glance::Image",
        "AWS::EC2::Volume",
        "OS::Heat::SoftwareDeployment",
        "AWS::AutoScaling::ScalingPolicy",
        "AWS::EC2::InternetGateway",
        "OS::Heat::SoftwareDeployments",
        "AWS::EC2::VolumeAttachment",
        "AWS::CloudFormation::WaitConditionHandle",
        "OS::Cinder::VolumeAttachment",
        "OS::Cinder::EncryptedVolumeType",
        "OS::Heat::AutoScalingGroup",
        "OS::Nova::FloatingIP",
        "OS::Heat::HARestarter",
        "OS::Keystone::Project",
        "OS::Keystone::Endpoint",
        "OS::Heat::InstanceGroup",
        "AWS::CloudWatch::Alarm",
        "AWS::AutoScaling::AutoScalingGroup",
        "OS::Heat::CloudConfig",
        "OS::Heat::SoftwareComponent",
        "OS::Cinder::Volume",
        "OS::Keystone::Service",
        "OS::Heat::WaitConditionHandle",
        "OS::Heat::SoftwareConfig",
        "AWS::CloudFormation::WaitCondition",
        "OS::Heat::StructuredDeploymentGroup",
        "OS::Heat::RandomString",
        "OS::Heat::SoftwareDeploymentGroup",
        "OS::Nova::KeyPair",
        "OS::Heat::MultipartMime",
        "OS::Heat::UpdateWaitConditionHandle",
        "OS::Nova::Server",
        "AWS::IAM::AccessKey",
        "AWS::EC2::SecurityGroup",
        "AWS::EC2::EIPAssociation",
        "AWS::EC2::EIP",
        "OS::Heat::AccessPolicy",
        "AWS::IAM::User",
        "OS::Heat::WaitCondition",
        "OS::Heat::StructuredDeployment",
        "AWS::RDS::DBInstance",
        "AWS::AutoScaling::LaunchConfiguration",
        "OS::Heat::Stack",
        "OS::Nova::FloatingIPAssociation",
        "OS::Heat::ResourceGroup",
        "OS::Heat::StructuredConfig",
        "OS::Nova::ServerGroup",
        "OS::Heat::StructuredDeployments",
        "OS::Keystone::Role",
        "OS::Keystone::User",
        "AWS::ElasticLoadBalancing::LoadBalancer",
        "OS::Nova::Flavor",
        "OS::Cinder::VolumeType"
    ]
}
```

***
### Build info
##### Show build information : 오케스트레이션 배포에 대한 빌드 정보를 보여 준다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/build_info
- Response 
```javascript
{
    "api": {
        "revision": "{api_build_revision}"
    },
    "engine": {
        "revision": "{engine_build_revision}"
    }
}
```

***
### Software configuration
##### Create configuration : 소프트웨어 설정을 생성한다. 
- Method : POST
- Request URI : /v1/​{tenant_id}​/software_configs
- Request
```javascript
{
    "inputs": [
        {
            ...
        },
        {
            ...
        }
    ],
    "group": "script",
    "name": "a-config-we5zpvyu7b5o",
    "outputs": [
        {
            ...
        }
    ],
    "config": "#!/bin/sh -x\necho \"Writing to /tmp/$bar\"\necho $foo > /tmp/$bar\necho -n \"The file /tmp/$bar contains `cat /tmp/$bar` for server $deploy_server_id during $deploy_action\" > $heat_outputs_path.result\necho \"Written to /tmp/$bar\"\necho \"Output to stderr\" 1>&2",
    "options": null
}
```
- Request Elements
     - config (Optional) :Configuration script or manifest that defines which configuration is performed. 
     - group (Optional) :Namespace that groups this software configuration by when it is delivered to a server. This setting might simply define which configuration tool performs the configuration. 
     - name (Optional) :The name of the configuration to create. 
     - inputs (Optional) :Schema that represents the inputs that this software configuration expects. 
     - outputs (Optional) :Schema that represents the outputs that this software configuration produces. 
     - options (Optional) :Map that contains options that are specific to the configuration management tool that this resource uses. 
- Response 
```javascript
{
    "software_config": {
        "creation_time": "2015-01-31T15:12:36Z",
        "inputs": [
            {
                ...
            },
            {
                ...
            }
        ],
        "group": "script",
        "name": "a-config-we5zpvyu7b5o",
        "outputs": [
            {
                ...
            }
        ],
        "options": null,
        "config": "#!/bin/sh -x\necho \"Writing to /tmp/$bar\"\necho $foo > /tmp/$bar\necho -n \"The file /tmp/$bar contains `cat /tmp/$bar` for server $deploy_server_id during $deploy_action\" > $heat_outputs_path.result\necho \"Written to /tmp/$bar\"\necho \"Output to stderr\" 1>&2",
        "id": "ddee7aca-aa32-4335-8265-d436b20db4f1"
    }
}
```

##### Show configuration details : 소프트웨어 설정을 자세하게 보여준다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_configs/​{config_id}​
- Response 
```javascript
{
    "software_config": {
        "inputs": [
            {
                ...
            },
            {
                ...
            }
        ],
        "group": "script",
        "name": "a-config-we5zpvyu7b5o",
        "outputs": [
            {
                ...
            }
        ],
        "creation_time": "2015-01-31T15:12:36Z",
        "id": "ddee7aca-aa32-4335-8265-d436b20db4f1",
        "config": "#!/bin/sh -x\necho \"Writing to /tmp/$bar\"\necho $foo > /tmp/$bar\necho -n \"The file /tmp/$bar contains `cat /tmp/$bar` for server $deploy_server_id during $deploy_action\" > $heat_outputs_path.result\necho \"Written to /tmp/$bar\"\necho \"Output to stderr\" 1>&2",
        "options": null
    }
}
```

##### Delete config : 소프트웨어 설정을 삭제 한다.
- Method : DELETE
- Request URI : /v1/​{tenant_id}​/software_configs/​{config_id}​
- Response :Response codes

##### List deployments : 사용가능한 모든 소프트웨어 배포 목록을 보여준다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments
- Response 
```javascript
{
    "software_deployments": [
        {
            "status": "COMPLETE",
            "server_id": "ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5",
            "config_id": "8da95794-2ad9-4979-8ae5-739ce314c5cd",
            "output_values": {
                "deploy_stdout": "Writing to /tmp/barmy\nWritten to /tmp/barmy\n",
                "deploy_stderr": "+ echo Writing to /tmp/barmy\n+ echo fu\n+ cat /tmp/barmy\n+ echo -n The file /tmp/barmy contains fu for server ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5 during CREATE\n+ echo Written to /tmp/barmy\n+ echo Output to stderr\nOutput to stderr\n",
                "deploy_status_code": 0,
                "result": "The file /tmp/barmy contains fu for server ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5 during CREATE"
            },
            "input_values": null,
            "action": "CREATE",
            "status_reason": "Outputs received",
            "id": "ef422fa5-719a-419e-a10c-72e3a367b0b8",
            "creation_time": "2015-01-31T15:12:36Z",
            "updated_time": "2015-01-31T15:18:21Z"
        }
    ]
}
```

##### Create deployment : 소프트웨어 배포를 생성한다.
- Method : POST
- Request URI : /v1/​{tenant_id}​/software_deployments
- Request
```javascript
{
    "status": "IN_PROGRESS",
    "server_id": "ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5",
    "config_id": "8da95794-2ad9-4979-8ae5-739ce314c5cd",
    "stack_user_project_id": "c024bfada67845ddb17d2b0c0be8cd79",
    "action": "CREATE",
    "status_reason": "Deploy data available"
}
```
- Request Elements
     - config_id :The ID of the software configuration resource that runs when applying to the server. 
     - server_id :The ID of the compute server to which the configuration applies. 
     - action :The current stack action that triggers this deployment resource. 
     - stack_user_project_id (Optional) :Authentication project ID, which can also perform operations on this deployment. 
     - status (Optional) :Current status of the deployment. 
     - status_reason (Optional) :Error description for the last status change, which is FAILED status. 
- Response 
```javascript
{
    "software_deployment": {
        "status": "IN_PROGRESS",
        "server_id": "ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5",
        "config_id": "8da95794-2ad9-4979-8ae5-739ce314c5cd",
        "output_values": null,
        "input_values": null,
        "action": "CREATE",
        "status_reason": "Deploy data available",
        "id": "ef422fa5-719a-419e-a10c-72e3a367b0b8",
        "creation_time": "2015-01-31T15:12:36Z",
        "updated_time": "2015-01-31T15:18:21Z"
    }
}
```

##### Show server configuration metadata : 지정된 서버에 대한 배포 구성 메타 데이터를 표시한다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments/metadata/​{server_id}​
- Response 
```javascript
{
    "metadata": [
        {
            "inputs": [
                ...
            ],
            "group": "script",
            "name": "a-config-we5zpvyu7b5o",
            "outputs": [
                ...
            ],
            "options": null,
            "creation_time": "2015-01-31T15:12:36Z",
            "updated_time": "2015-01-31T15:18:21Z",
            "config": "#!/bin/sh -x\necho \"Writing to /tmp/$bar\"\necho $foo > /tmp/$bar\necho -n \"The file /tmp/$bar contains `cat /tmp/$bar` for server $deploy_server_id during $deploy_action\" > $heat_outputs_path.result\necho \"Written to /tmp/$bar\"\necho \"Output to stderr\" 1>&2",
            "id": "3d5ec2a8-7004-43b6-a7f6-542bdbe9d434"
        },
        {
            "inputs": [
                ...
            ],
            "group": "script",
            "name": "a-config-we5zpvyu7b5o",
            "outputs": [
                ...
            ],
            "options": null,
            "creation_time": "2015-01-31T16:14:13Z",
            "updated_time": "2015-01-31T16:18:19Z",
            "config": "#!/bin/sh -x\necho \"Writing to /tmp/$bar\"\necho $foo > /tmp/$bar\necho -n \"The file /tmp/$bar contains `cat /tmp/$bar` for server $deploy_server_id during $deploy_action\" > $heat_outputs_path.result\necho \"Written to /tmp/$bar\"\necho \"Output to stderr\" 1>&2",
            "id": "8da95794-2ad9-4979-8ae5-739ce314c5cd"
        }
    ]
}
```

##### Show deployment details : 지정된 소프트웨어 배포를 자세하게 보여준다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Response 
```javascript
{
    "software_deployment": {
        "status": "IN_PROGRESS",
        "server_id": "ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5",
        "config_id": "3d5ec2a8-7004-43b6-a7f6-542bdbe9d434",
        "output_values": null,
        "input_values": null,
        "action": "CREATE",
        "status_reason": "Deploy data available",
        "id": "06e87bcc-33a2-4bce-aebd-533e698282d3",
        "creation_time": "2015-01-31T15:12:36Z",
        "updated_time": "2015-01-31T15:18:21Z"
    }
}
```

##### Update deployment : 지정된 소프트웨어 배포를 업데이트 한다.
- Method : PUT
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Request
```javascript
{
    "status": "COMPLETE",
    "output_values": {
        "deploy_stdout": "Writing to /tmp/baaaaa\nWritten to /tmp/baaaaa\n",
        "deploy_stderr": "+ echo Writing to /tmp/baaaaa\n+ echo fooooo\n+ cat /tmp/baaaaa\n+ echo -n The file /tmp/baaaaa contains fooooo for server ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5 during CREATE\n+ echo Written to /tmp/baaaaa\n+ echo Output to stderr\nOutput to stderr\n",
        "deploy_status_code": 0,
        "result": "The file /tmp/baaaaa contains fooooo for server ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5 during CREATE"
    },
    "status_reason": "Outputs received"
}
```
- Response 
```javascript
{
    "software_deployment": {
        "status": "COMPLETE",
        "server_id": "ec14c864-096e-4e27-bb8a-2c2b4dc6f3f5",
        "config_id": "3d5ec2a8-7004-43b6-a7f6-542bdbe9d434",
        "output_values": {
            ...
        },
        "input_values": null,
        "action": "CREATE",
        "status_reason": "Outputs received",
        "id": "06e87bcc-33a2-4bce-aebd-533e698282d3",
        "creation_time": "2015-01-31T15:12:36Z",
        "updated_time": "2015-01-31T15:18:21Z"
    }
}
```

##### Delete deployment : 지정된 소프트웨어 배포를 삭제한다.
- Method : DELETE
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Response :Response codes

***
### Manage service
##### Show orchestration engine status : 모든 오케스트레이션 엔진에 대한 세부 정보를 볼 수 관리 사용자를 활성화한다.
- Method : GET
- Request URI : /v1/​{tenant_id}​/services
- Response 
```javascript
{
    "services": [
        {
            "status": "up",
            "binary": "heat-engine",
            "report_interval": 60,
            "engine_id": "9d9242c3-4b9e-45e1-9e74-7615fbf20e5d",
            "created_at": "2015-02-03T05:55:59.000000",
            "hostname": "mrkanag",
            "updated_at": "2015-02-03T05:57:59.000000",
            "topic": "engine",
            "host": "engine-1",
            "deleted_at": null,
            "id": "e1908f44-42f9-483f-b778-bc814072c33d"
        },
        {
            "status": "down",
            "binary": "heat-engine",
            "report_interval": 60,
            "engine_id": "2d2434bf-adb6-4453-9c6b-b22fb8bd2306",
            "created_at": "2015-02-03T06:03:14.000000",
            "hostname": "mrkanag",
            "updated_at": "2015-02-03T06:09:55.000000",
            "topic": "engine",
            "host": "engine",
            "deleted_at": null,
            "id": "582b5657-6db7-48ad-8483-0096350faa21"
        }
    ]
}
```

