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
##### Get stack template : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/template
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### List template versions : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/template_versions 
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Validate template : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/validate
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show resource template : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/resource_types/​{type_name}​/template
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

***
### Build info
##### Show build information : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/build_info
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

***
### Software configuration
##### Create configuration : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/software_configs
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show configuration details : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_configs/​{config_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Delete config : 
- Method : DELETE
- Request URI : /v1/​{tenant_id}​/software_configs/​{config_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### List deployments : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Create deployment : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/software_deployments
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show server configuration metadata : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments/metadata/​{server_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show deployment details : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Update deployment : 
- Method : PUT
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Delete deployment : 
- Method : DELETE
- Request URI : /v1/​{tenant_id}​/software_deployments/​{deployment_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

***
### Manage service
##### Show orchestration engine status : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/services
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
