.. highlight: yaml
   :linenothreshold: 5

..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

.. _composition:

====================
Template composition
====================

When writing complex templates you are encouraged to break up your
template into separate smaller templates. These can then be brought
together using template resources. This is a mechanism to define a resource
using a template, thus composing one logical stack with multiple templates.

Template resources provide a feature similar to the
:ref:`AWS::CloudFormation::Stack` resource, but also provide a way to:

* Define new resource types and build your own resource library.
* Override the default behavior of existing resource types.

To achieve this:

* The Orchestration client gets the associated template files and passes them
  along in the ``files`` section of the ``POST stacks/`` API request.
* The environment in the Orchestration engine manages the mapping of resource
  type to template creation.
* The Orchestration engine translates template parameters into resource
  properties.

The following examples illustrate how you can use a custom template to define
new types of resources. These examples use a custom template stored in a
:file:`my_nova.yaml` file::

  heat_template_version: 2014-10-16

  parameters:
    key_name:
      type: string
      description: Name of a KeyPair

  resources:
    server:
      type: OS::Nova::Server
      properties:
        key_name: {get_param: key_name}
        flavor: m1.small
        image: ubuntu-trusty-x86_64

Use the template filename as type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following template defines the :file:`my_nova.yaml` file as value for the
``type`` property of a resource::

  heat_template_version: 2014-10-16

  resources:
    my_server:
      type: my_nova.yaml
      properties:
        key_name: my_key

The ``key_name`` argument of the ``my_nova.yaml`` template gets its value from
the ``key_name`` property of the new template.

.. note::

  The above reference to :file:`my_nova.yaml` assumes it is in the same directory.
  You can use any of the following forms:

  * Relative path (:file:`my_nova.yaml`)
  * Absolute path (:file:`file:///home/user/templates/my_nova.yaml`)
  * Http URL (``http://example.com/templates/my_nova.yaml``)
  * Https URL (``https://example.com/templates/my_nova.yaml``)

To create the stack run::

  $ heat stack-create -f main.yaml stack1


Define a new resource type
~~~~~~~~~~~~~~~~~~~~~~~~~~
You can associate a name to the :file:`my_nova.yaml` template in an environment
file. If the name is already known by the Orchestration module then your new
resource will override the default one.

In the following example a new ``OS::Nova::Server`` resource overrides the
default resource of the same name.

An :file:`env.yaml` environment file holds the definition of the new resource::

  resource_registry:
    "OS::Nova::Server": my_nova.yaml

.. note::

   See :ref:`environments` for more detail about environment files.

You can now use the new ``OS::Nova::Server`` in your new template::

  heat_template_version: 2014-10-16

  resources:
    my_server:
      type: OS::Nova::Server
      properties:
        key_name: my_key

To create the stack run::

  $ heat stack-create -f main.yaml -e env.yaml example-two

Get access to nested attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are implicit attributes of a template resource. Accessing nested
attributes requires ``heat_template_version`` 2014-10-16 or higher. These are
accessible as follows::

  heat_template_version: 2014-10-16

  resources:
    my_server:
      type: my_nova.yaml

  outputs:
    test_out:
      value: {get_attr: my_server, resource.server, first_address}

Making your template resource more "transparent"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. note::

   Available since 2015.1 (Kilo).

If you wish to be able to return the ID of one of the inner resources
instead of the nested stack's identifier, you can add the special reserved
output ``OS::stack_id`` to your template resource::

  heat_template_version: 2014-10-16

  resources:
    server:
      type: OS::Nova::Server

  outputs:
    OS::stack_id:
      value: {get_resource: server}

Now when you use ``get_resource`` from the outer template heat
will use the nova server id and not the template resource identifier.
