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
- Response :Response codes

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

##### Find stack : 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Find stack resources : 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/resources
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show stack details : 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Update stack : 
- Method : PUT
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Delete stack : 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Abandon stack : 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/abandon
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Snapshot stack : 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### List snapshots : 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Show snapshot : 
- Method : GET
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Delete snapshot : 
- Method : DELETE
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes
 
##### Restore snapshot : 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/snapshots/{snapshot_id}/restore
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

### Stacks actions
##### Suspend stack : 
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

##### Resume stack: 
- Method : POST
- Request URI : /v1/{tenant_id}/stacks/{stack_name}/{stack_id}/actions
- Request
```javascript
{
    "resume": null
}
```
- Request Elements
     - resume :Specify the resume action in the request body. 
- Response :Response codes

##### Cancel stack update : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/actions
- Request
```javascript
{
    "cancel_update": null
}
```
- Request Elements
     - cancel_update :Specify the cancel_update action in the request body. 
- Response :Response codes

##### Check stack resources : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/actions
- Request
```javascript
{
    "check": null
}
```
- Request Elements
     - check :Specify the check action in the request body. 
- Response :Response codes

### Stacks resources
##### List resources : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show resource data : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show resource metadata : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/metadata
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Send a signal to a resource : 
- Method : POST
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/signal
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

### Stacks events
##### Find stack events : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/events
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### List stack events : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/events
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### List resource events : 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/events
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

##### Show event details: 
- Method : GET
- Request URI : /v1/​{tenant_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/events/​{event_id}​
- Request
```javascript
```
- Request Elements
- Response 
```javascript
```
- Response Elements
- Response :Response codes

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
