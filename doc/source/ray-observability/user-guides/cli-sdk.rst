.. _observability-programmatic:

使用 CLI 或 SDK 进行监控
===============================

Ray 中的监控和调试功能可通过 CLI 或 SDK 获得。


CLI 命令 ``ray status`` 
----------------------------
您可以通过在头节点上运行 CLI 命令 ``ray status``来监控节点状态和资源使用情况。它显示了

- **节点状态**: 正在运行并自动向上或向下扩展的节点。运行节点的地址。有关待处理节点和失败节点的信息。
- **资源使用情况**: Ray 集群的资源使用情况。例如，从所有 Ray 任务和 Actor 请求的 CPU。使用的 GPU 数量。

以下是示例输出：

.. code-block:: shell

   $ ray status
   ======== Autoscaler status: 2021-10-12 13:10:21.035674 ========
   Node status
   ---------------------------------------------------------------
   Healthy:
    1 ray.head.default
    2 ray.worker.cpu
   Pending:
    (no pending nodes)
   Recent failures:
    (no failures)

   Resources
   ---------------------------------------------------------------
   Usage:
    0.0/10.0 CPU
    0.00/70.437 GiB memory
    0.00/10.306 GiB object_store_memory

   Demands:
    (no resource demands)

当您需要有关每个节点的更多详细信息时，请运行 ``ray status -v``。 当您需要调查为什么特定节点不自动缩小规模时，这非常有用。


.. _state-api-overview-ref:

Ray 状态 CLI 和 SDK
----------------------------

.. tip:: 提供有关使用 Ray state API 的反馈 - `反馈表 <https://forms.gle/gh77mwjEskjhN8G46>`_!

使用 Ray State API 通过 CLI 或 Python SDK（开发人员 API）访问 Ray 的当前状态（快照）。

.. note::

    此功能需要使用 ``pip install "ray[default]"``. 完整安装 Ray 。此功能还要求仪表板组件可用。启动 Ray Cluster 时需要包含仪表板组件，这是 `ray start`` 和 ``ray.init()`` 的默认行为。

.. note::

    State API CLI 命令是 :ref:`stable <api-stability-stable>`，而 Python SDK 是 :ref:`DeveloperAPI <developer-api-def>`。建议使用 CLI 而不是 Python SDK。


开始
~~~~~~~~~~~

此示例使用以下脚本运行两个任务并创建两个 Actor。

.. testcode::
    :hide:

    import ray

    ray.shutdown()

.. testcode::

    import ray
    import time

    ray.init(num_cpus=4)

    @ray.remote
    def task_running_300_seconds():
        time.sleep(300)

    @ray.remote
    class Actor:
        def __init__(self):
            pass

    # Create 2 tasks
    tasks = [task_running_300_seconds.remote() for _ in range(2)]

    # Create 2 actors
    actors = [Actor.remote() for _ in range(2)]

.. testcode::
    :hide:

    # Wait for the tasks to be submitted.
    time.sleep(2)

查看任务的汇总状态。如果它没有立即返回输出，请重试该命令。

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray summary tasks

        .. code-block:: text

            ======== Tasks Summary: 2022-07-22 08:54:38.332537 ========
            Stats:
            ------------------------------------
            total_actor_scheduled: 2
            total_actor_tasks: 0
            total_tasks: 2


            Table (group by func_name):
            ------------------------------------
                FUNC_OR_CLASS_NAME        STATE_COUNTS    TYPE
            0   task_running_300_seconds  RUNNING: 2      NORMAL_TASK
            1   Actor.__init__            FINISHED: 2     ACTOR_CREATION_TASK

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import summarize_tasks
            print(summarize_tasks())

        .. testoutput::

            {'cluster': {'summary': {'task_running_300_seconds': {'func_or_class_name': 'task_running_300_seconds', 'type': 'NORMAL_TASK', 'state_counts': {'RUNNING': 2}}, 'Actor.__init__': {'func_or_class_name': 'Actor.__init__', 'type': 'ACTOR_CREATION_TASK', 'state_counts': {'FINISHED': 2}}}, 'total_tasks': 2, 'total_actor_tasks': 0, 'total_actor_scheduled': 2, 'summary_by': 'func_name'}}

列出所有 Actors。

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list actors

        .. code-block:: text

            ======== List: 2022-07-23 21:29:39.323925 ========
            Stats:
            ------------------------------
            Total: 2

            Table:
            ------------------------------
                ACTOR_ID                          CLASS_NAME    NAME      PID  STATE
            0  31405554844820381c2f0f8501000000  Actor                 96956  ALIVE
            1  f36758a9f8871a9ca993b1d201000000  Actor                 96955  ALIVE

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_actors
            print(list_actors())

        .. testoutput::

            [ActorState(actor_id='...', class_name='Actor', state='ALIVE', job_id='01000000', name='', node_id='...', pid=..., ray_namespace='...', serialized_runtime_env=None, required_resources=None, death_cause=None, is_detached=None, placement_group_id=None, repr_name=None), ActorState(actor_id='...', class_name='Actor', state='ALIVE', job_id='01000000', name='', node_id='...', pid=..., ray_namespace='...', serialized_runtime_env=None, required_resources=None, death_cause=None, is_detached=None, placement_group_id=None, repr_name=None)]


使用 get API 获取单个任务的状态。

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            # In this case, 31405554844820381c2f0f8501000000
            ray get actors <ACTOR_ID>

        .. code-block:: text

            ---
            actor_id: 31405554844820381c2f0f8501000000
            class_name: Actor
            death_cause: null
            is_detached: false
            name: ''
            pid: 96956
            resource_mapping: []
            serialized_runtime_env: '{}'
            state: ALIVE

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_actor
            # In this case, 31405554844820381c2f0f8501000000
            print(get_actor(id=<ACTOR_ID>))

通过 ``ray logs``  API 访问日志。

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list actors
            # In this case, ACTOR_ID is 31405554844820381c2f0f8501000000
            ray logs actor --id <ACTOR_ID>

        .. code-block:: text

            --- Log has been truncated to last 1000 lines. Use `--tail` flag to toggle. ---

            :actor_name:Actor
            Actor created

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_log

            # In this case, ACTOR_ID is 31405554844820381c2f0f8501000000
            for line in get_log(actor_id=<ACTOR_ID>):
                print(line)

关键概念
~~~~~~~~~~~~~
Ray State API 允许您通过 **summary**、 **list** 和 **get** API访问 **资源** 的 **状态**。 它还支持 **logs** API 来访问日志。

- **states**: 对应资源的集群状态。状态由不可变元数据（例如，Actor 的名称）和可变状态（例如，Actor 的调度状态或 pid）组成。
- **resources**: Ray 创建的资源。例如，actor、任务、对象、占位组等。
- **summary**: 返回资源汇总视图的 API。
- **list**: 返回每个资源实体的 API。
- **get**: 返回单个资源实体详细信息的 API。
- **logs**: 用于访问 Actor、任务、Workers 日志或系统日志文件的 API。



用户指南
~~~~~~~~~~~~~

按类型获取实体状态的摘要
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
返回给定 Ray 实体（对象、Actor、任务）的汇总信息。
建议首先通过摘要 API 开始监控状态。
当您发现异常情况时（例如，长时间运行的Actor、长时间未调度的任务），
您可以使用 ``list`` 或 ``get`` API 来获取单个异常实体的更多详细信息。

**汇总所有 actor**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray summary actors

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import summarize_actors
            print(summarize_actors())

        .. testoutput::

            {'cluster': {'summary': {'Actor': {'class_name': 'Actor', 'state_counts': {'ALIVE': 2}}}, 'total_actors': 2, 'summary_by': 'class'}}

**汇总所有 task**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray summary tasks

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import summarize_tasks
            print(summarize_tasks())

        .. testoutput::

            {'cluster': {'summary': {'task_running_300_seconds': {'func_or_class_name': 'task_running_300_seconds', 'type': 'NORMAL_TASK', 'state_counts': {'RUNNING': 2}}, 'Actor.__init__': {'func_or_class_name': 'Actor.__init__', 'type': 'ACTOR_CREATION_TASK', 'state_counts': {'FINISHED': 2}}}, 'total_tasks': 2, 'total_actor_tasks': 0, 'total_actor_scheduled': 2, 'summary_by': 'func_name'}}

**汇总所有对象**

.. note::

    默认情况下，对象按调用点进行汇总。但是，Ray 默认情况下不记录调用点。要获取调用点信息，请在启动 Ray 集群时设置环境变量 `RAY_record_ref_creation_sites=1` 
    RAY_record_ref_creation_sites=1 ray start --head

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray summary objects

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import summarize_objects
            print(summarize_objects())

        .. testoutput::

            {'cluster': {'summary': {'disabled': {'total_objects': 6, 'total_size_mb': 0.0, 'total_num_workers': 3, 'total_num_nodes': 1, 'task_state_counts': {'SUBMITTED_TO_WORKER': 2, 'FINISHED': 2, 'NIL': 2}, 'ref_type_counts': {'LOCAL_REFERENCE': 2, 'ACTOR_HANDLE': 4}}}, 'total_objects': 6, 'total_size_mb': 0.0, 'callsite_enabled': False, 'summary_by': 'callsite'}}

有关命令的更多详细信息，请参阅 :ref:`state CLI 参考 <state-api-cli-ref>` 关于 ``ray summary`` 命令。


列出某种类型的所有实体的状态
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

获取资源列表。可能的资源包括：

- :ref:`Actors <actor-guide>` 例如 Actor ID、状态、PID、death_cause ( :class:`output schema <ray.util.state.common.ActorState>`）
- :ref:`Tasks <ray-remote-functions>` 例如名称、调度状态、类型、运行时环境信息 (:class:`output schema <ray.util.state.common.TaskState>`)
- :ref:`Objects <objects-in-ray>`, 例如对象 ID、调用点、引用类型 ( (:class:`output schema <ray.util.state.common.ObjectState>`)
- :ref:`Jobs <jobs-overview>`,例如开始/结束时间、入口点、状态 (:class:`output schema <ray.util.state.common.JobState>`)
- :ref:`Placement Groups <ray-placement-group-doc-ref>`, 例如名称、捆绑包、统计信息 (:class:`output schema <ray.util.state.common.PlacementGroupState>`)
- 节点（Ray 工作节点），例如节点 ID、节点 IP、节点状态 (:class:`output schema <ray.util.state.common.NodeState>`)
- Workers（Ray 工作进程），例如工作 ID、类型、退出类型和详细信息 (:class:`output schema <ray.util.state.common.WorkerState>`)
- :ref:`运行时环境 <runtime-environments>`, 例如运行时环境、创建时间、节点 (:class:`output schema <ray.util.state.common.RuntimeEnvState>`)

**列出所有节点**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list nodes

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_nodes
            list_nodes()

**列出所有归置组**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list placement-groups

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_placement_groups
            list_placement_groups()


**列出进程创建的本地引用对象**

.. tip:: 您可以使用一个或多个过滤器列出资源：使用 `--filter` 或 `-f`

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list objects -f pid=<PID> -f reference_type=LOCAL_REFERENCE

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_objects
            list_objects(filters=[("pid", "=", 1234), ("reference_type", "=", "LOCAL_REFERENCE")])

**列出存活的 actor**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list actors -f state=ALIVE

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_actors
            list_actors(filters=[("state", "=", "ALIVE")])

**列出运行中的 task**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list tasks -f state=RUNNING

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_tasks
            list_tasks(filters=[("state", "=", "RUNNING")])

**列出非运行 task**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list tasks -f state!=RUNNING

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_tasks
            list_tasks(filters=[("state", "!=", "RUNNING")])

**列出具有名称的正在运行的任务**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list tasks -f state=RUNNING -f name="task_running_300_seconds()"

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_tasks
            list_tasks(filters=[("state", "=", "RUNNING"), ("name", "=", "task_running_300_seconds()")])

**列出包含更多详细信息的任务**

.. tip:: 当指定 ``--detail``时，API可以查询更多数据源以获取详细的状态信息。

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray list tasks --detail

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::

            from ray.util.state import list_tasks
            list_tasks(detail=True)

有关命令的更多详细信息，请参阅 :ref:`state CLI 参考 <state-api-cli-ref>` 的 ``ray list`` 命令。


获取特定实体（任务、actor 等）的状态
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Get a task's states**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray get tasks <TASK_ID>

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_task
            get_task(id=<TASK_ID>)

**Get a node's states**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray get nodes <NODE_ID>

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_node
            get_node(id=<NODE_ID>)

See :ref:`state CLI reference <state-api-cli-ref>` for more details about ``ray get`` command.


Fetch the logs of a particular entity (task, actor, etc.)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _state-api-log-doc:

State API also allows you to access Ray logs. Note that you cannot access the logs from a dead node.
By default, the API prints logs from a head node.

**Get all retrievable log file names from a head node in a cluster**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray logs cluster

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            # You could get the node ID / node IP from `ray list nodes`
            from ray.util.state import list_logs
            # `ray logs` by default print logs from a head node.
            # To list the same logs, you should provide the head node ID.
            # Get the node ID / node IP from `ray list nodes`
            list_logs(node_id=<HEAD_NODE_ID>)

**Get a particular log file from a node**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            # Get the node ID / node IP from `ray list nodes`
            ray logs cluster gcs_server.out --node-id <NODE_ID>
            # `ray logs cluster` is alias to `ray logs` when querying with globs.
            ray logs gcs_server.out --node-id <NODE_ID>

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_log

            # Node IP can be retrieved from list_nodes() or ray.nodes()
            for line in get_log(filename="gcs_server.out", node_id=<NODE_ID>):
                print(line)

**Stream a log file from a node**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            # Get the node ID / node IP from `ray list nodes`
            ray logs raylet.out --node-ip <NODE_IP> --follow
            # Or,
            ray logs cluster raylet.out --node-ip <NODE_IP> --follow


    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_log

            # Retrieve the Node IP from list_nodes() or ray.nodes()
            # The loop blocks with `follow=True`
            for line in get_log(filename="raylet.out", node_ip=<NODE_IP>, follow=True):
                print(line)

**Stream log from an actor with actor id**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray logs actor --id=<ACTOR_ID> --follow

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_log

            # Get the Actor's ID from the output of `ray list actors`.
            # The loop blocks with `follow=True`
            for line in get_log(actor_id=<ACTOR_ID>, follow=True):
                print(line)

**Stream log from a pid**

.. tabs::

    .. group-tab:: CLI (Recommended)

        .. code-block:: bash

            ray logs worker --pid=<PID> --follow

    .. group-tab:: Python SDK (Internal Developer API)

        .. testcode::
            :skipif: True

            from ray.util.state import get_log

            # Retrieve the node IP from list_nodes() or ray.nodes()
            # get the PID of the worker running the Actor easily when output
            # of worker is directed to the driver (default)
            # The loop blocks with `follow=True`
            for line in get_log(pid=<PID>, node_ip=<NODE_IP>, follow=True):
                print(line)

See :ref:`state CLI reference<state-api-cli-ref>` for more details about ``ray logs`` command.


Failure Semantics
^^^^^^^^^^^^^^^^^^^^^^^^^

The State APIs don't guarantee to return a consistent or complete snapshot of the cluster all the time. By default,
all Python SDKs raise an exception when output is missing from the API. The CLI returns a partial result
and provides warning messages. Here are cases where there can be missing output from the API.

**Query Failures**

State APIs query "data sources" (e.g., GCS, raylets, etc.) to obtain and build the snapshot of the Cluster.
However, data sources are sometimes unavailable (e.g., the source is down or overloaded). In this case, APIs
return a partial (incomplete) snapshot of the Cluster, and users are informed that the output is incomplete through a warning message.
All warnings are printed through Python's ``warnings`` library, and they can be suppressed.

**Data Truncation**

When the returned number of entities (number of rows) is too large (> 100K), state APIs truncate the output data to ensure system stability
(when this happens, there's no way to choose truncated data). When truncation happens it is informed through Python's
``warnings`` module.

**Garbage Collected Resources**

Depending on the lifecycle of the resources, some "finished" resources are not accessible
through the APIs because they are already garbage collected.

.. note::

    Do not to rely on this API to obtain correct information on finished resources.
    For example, Ray periodically garbage collects DEAD state Actor data to reduce memory usage.
    Or it cleans up the FINISHED state of Tasks when its lineage goes out of scope.

API Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~

- For the CLI Reference, see :ref:`State CLI Refernece <state-api-cli-ref>`.
- For the SDK Reference, see :ref:`State API Reference <state-api-ref>`.
- For the Log CLI Reference, see :ref:`Log CLI Reference <ray-logs-api-cli-ref>`.




Using Ray CLI tools from outside the cluster
--------------------------------------------------------
These CLI commands have to be run on a node in the Ray Cluster. Examples for
executing these commands from a machine outside the Ray Cluster are provided
below.

.. tab-set::

    .. tab-item:: VM Cluster Launcher

        Execute a command on the cluster using ``ray exec``:

        .. code-block:: shell

            $ ray exec <cluster config file> "ray status"

    .. tab-item:: KubeRay

        Execute a command on the cluster using ``kubectl exec`` and the configured
        RayCluster name. Ray uses the Service targeting the Ray head pod to
        execute a CLI command on the cluster.

        .. code-block:: shell

            # First, find the name of the Ray head service.
            $ kubectl get pod | grep <RayCluster name>-head
            # NAME                                             READY   STATUS    RESTARTS   AGE
            # <RayCluster name>-head-xxxxx                     2/2     Running   0          XXs

            # Then, use the name of the Ray head service to run `ray status`.
            $ kubectl exec <RayCluster name>-head-xxxxx -- ray status
