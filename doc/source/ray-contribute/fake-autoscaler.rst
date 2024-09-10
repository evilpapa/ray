.. _fake-multinode:

本地测试自动缩放
===========================

测试自动扩缩行为对于自动扩缩器开发和依赖于自动扩缩器行为的
应用程序的调试非常重要。您可以使用以下方法之一
在本地运行自动扩缩器，而无需启动真实集群：

使用 ``RAY_FAKE_CLUSTER=1 ray start``
--------------------------------------

说明：

1. 导航到您在本地克隆的 Ray repo 的根目录。

2. 找到 `fake_multi_node/example.yaml <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/_private/fake_multi_node/example.yaml>`__ 示例文件并填写本地计算机的 CPU 和 GPU 数量作为头节点类型配置。YAML 遵循与集群自动扩缩器配置相同的格式，但某些字段不受支持。

3. 根据需要在 YAML 文件中配置 worker 类型和其他自动缩放配置。

4. 本地启动虚假集群：

.. code-block:: shell

    $ ray stop --force
    $ RAY_FAKE_CLUSTER=1 ray start \
        --autoscaling-config=./python/ray/autoscaler/_private/fake_multi_node/example.yaml \
        --head --block

5. 使用 ``ray.init("auto")`` 将您的应用程序连接到虚假本地集群。

6. 运行 ``ray status`` 以查看集群的状态，或使用 ``cat /tmp/ray/session_latest/logs/monitor.*`` 查看自动缩放器监视日志：

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

使用 ``ray.cluster_utils.AutoscalingCluster``
----------------------------------------------

要以编程方式创建一个虚假的多节点自动缩放集群并连接到它，可以使用 `cluster_utils.AutoscalingCluster <https://github.com/ray-project/ray/blob/master/python/ray/cluster_utils.py>`__。 以下是启动触发自动缩放的任务的基本自动缩放测试的示例：

.. literalinclude:: /../../python/ray/tests/test_autoscaler_fake_multinode.py
   :language: python
   :dedent: 4
   :start-after: __example_begin__
   :end-before: __example_end__

Python 文档：

.. autoclass:: ray.cluster_utils.AutoscalingCluster
    :members:

``fake_multinode`` 的功能和限制
----------------------------------------------

自动扩缩器的大部分功能在模拟多节点模式下均受支持。例如，如果您更新 YAML 文件的内容，自动扩缩器将获取新配置并应用更改，就像在真实集群中一样。节点选择、启动和终止由与真实集群相同的装箱和空闲超时算法控制。

然而，也存在一些限制：

1. 所有节点 raylet 都在本地机器上以非容器化方式运行，因此它们共享相同的 IP 地址。请参阅 :ref:`fake_multinode_docker <fake-multinode-docker>` 部分，了解替代的本地多节点设置。

2. 不支持身份验证、设置、初始化、Ray 启动、文件同步以及任何特定于云的配置。

3. 有必要限制节点/节点 CPU/对象存储内存的数量，以避免本地机器过载。

.. _fake-multinode-docker:

使用 Docker Compose 在本地测试容器化的多节点
=============================================================
为了更进一步并在本地测试多节点设置，其中每个节点
使用自己的容器「因此具有单独的文件系统、IP 地址和 Ray 进程」，您可以使用 ``fake_multinode_docker`` 节点提供程序。

该设置与 :ref:`fake_multinode <fake-multinode>` 提供程序非常类似。但是，您需要启动一个监控进程
「``docker_monitor.py``」来负责运行 ``docker compose`` 命令。 

先决条件：

1. 确保安装 `docker <https://docs.docker.com/get-docker/>`_ 。

2. 确保您已安装 `docker compose V2 插件 <https://docs.docker.com/compose/cli-command/#installing-compose-v2>`_ 。

使用 ``RAY_FAKE_CLUSTER=1 ray up``
-----------------------------------
指示：

1. 导航到您在本地克隆的 Ray repo 的根目录。

2. 找到 `fake_multi_node/example_docker.yaml <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/_private/fake_multi_node/example_docker.yaml>`__ 示例文件，并填写本地计算机的 CPU 和 GPU 数量作为头节点类型配置。YAML 遵循与集群自动扩缩器配置相同的格式，但某些字段不受支持。

3. 根据需要在 YAML 文件中配置 worker 类型和其他自动缩放配置。

4. 确保 ``shared_volume_dir`` 在主机上为空

5. 启动监控进程：

.. code-block:: shell

    $ python ./python/ray/autoscaler/_private/fake_multi_node/docker_monitor.py \
        ./python/ray/autoscaler/_private/fake_multi_node/example_docker.yaml

6. 使用 ``ray up`` 命令启动 Ray 集群：

.. code-block:: shell

    $ RAY_FAKE_CLUSTER=1 ray up -y ./python/ray/autoscaler/_private/fake_multi_node/example_docker.yaml

7. 使用 ``ray.init("ray://localhost:10002")`` 将您的应用程序连接到虚假本地集群。

8. 或者，在头节点上获取 shell：

.. code-block:: shell

    $ docker exec -it fake_docker_fffffffffffffffffffffffffffffffffffffffffffffffffff00000_1 bash

使用 ``ray.autoscaler._private.fake_multi_node.test_utils.DockerCluster``
--------------------------------------------------------------------------
此实用程序用于编写使用多节点行为的测试。 ``DockerCluster`` 类
可用于在临时目录中设置 Docker-compose 集群、
启动监控过程、等待集群启动、连接到集群并更新配置。

请参阅 API 文档和示例测试用例以了解如何使用此实用程序。

.. autoclass:: ray.autoscaler._private.fake_multi_node.test_utils.DockerCluster
    :members:


``fake_multinode_docker`` 功能及限制
-----------------------------------------------------

伪多节点 docker 节点提供程序在自己的容器中提供功能齐全的节点。但是，
仍然存在一些限制：

1. 不支持身份验证、设置、初始化、Ray 启动、文件同步以及任何特定于云的配置
  「但将来可能会支持」。

2. 有必要限制节点/节点 CPU/对象存储内存的数量，以避免本地机器过载。

3. 在 docker-in-docker 设置中，必须遵循仔细的设置才能使虚假的多节点 docker 提供程序工作「见下文」。

Docker 环境内的共享目录
------------------------------------------------
容器将在两个位置安装主机存储：

- ``/cluster/node``: 此位置「在容器中」将指向 ``cluster_dir/nodes/<node_id>``「在主机上」。
  此位置每个节点都是单独的，但可以使用它来让主机检查存储在此目录中的内容。
- ``/cluster/shared``: 此位置「在容器中」将指向 ``cluster_dir/shared`` 「在主机上」。此位置
  在节点之间共享，并有效地充当共享文件系统「与 NFS 类似」。


在 Docker-in-Docker「dind」环境中进行设置
---------------------------------------------------
在 Docker-in-Docker (dind) 环境「例如 Ray OSS Buildkite 环境」中进行设置时，必须
牢记一些事项。为了清楚起见，请考虑以下概念：

* **host** 是执行代码的非容器化机器「例如 Buildkite 运行器」
* **outer container** 是直接在 **host** 上运行的容器。在 Ray OSS Buildkite 环境中，
  启动了两个容器 —— 一个 *dind *网络主机和一个里面装有 Ray 源代码和 wheel 的容器。
* **inner container** 是由伪造的多节点docker节点提供商启动的容器。

多节点 docker 节点提供程序的控制平面位于外部容器中。但是 ``docker compose`` 命令 
是从连接的 docker-in-docker 网络执行的。在 Ray OSS Buildkite 环境中，这是在主机 docker 中 ``dind-daemon`` 容器运行的。
如果您从主机挂载  ``/var/run/docker.sock`` ，它将是主机 docker 守护程序。
从现在开始，我们将两者都称为 **主机守护** 程序。

外部容器修改必须挂载在内部容器中的文件「并从那里进行修改」。
这意味着主机守护进程也必须有权访问这些文件。

类似地，内部容器暴露端口 - 但由于容器实际上是由主机守护进程启动的，
因此端口也只能在主机「或 dind 容器」上访问。

对于 Ray OSS Buildkite 环境，我们设置了一些环境变量：

* ``RAY_TEMPDIR="/ray-mount"``。此环境变量定义应在何处创建集群文件的临时目录。
  此目录必须可由主机、外部容器和内部容器访问。
  在内部容器中，我们可以控制目录名称。

* ``RAY_HOSTDIR="/ray"``。如果共享目录在主机上的名称不同，我们可以动态重写挂载点。
  在此示例中，外部容器以 ``-v /ray:/ray-mount`` 或类似名称启动，
  因此主机上的目录为  ``/ray`` ，而外部容器中的目录为 ``/ray-mount``「请参阅 ``RAY_TEMPDIR`` 」。

* ``RAY_TESTHOST="dind-daemon"`` 由于容器是由主机守护程序启动的，因此我们不能直接连接到
  ``localhost``，因为端口不会暴露给外部容器。因此，我们可以使用此环境变量设置 Ray 主机。

最后，docker-compose 显然需要一个 docker 镜像。默认的 docker 镜像是 ``rayproject/ray:nightly``。
docker 镜像 ``openssh-server`` 的安装和启用。在 Buildkite 中，我们从
``rayproject/ray:nightly-py37-cpu`` 构建一个新镜像，以避免为每个节点动态安装它「这是默认方式」。
此基础镜像是在前面的构建步骤之一中构建的。

因此，我们设定

* ``RAY_DOCKER_IMAGE="rayproject/ray:multinode-py37"``

* ``RAY_HAS_SSH=1``

使用这个docker镜像并告知我们的多节点基础设施 SSH 已经安装。

本地开发
-----------------

如果你在伪多节点 docker 模块上进行本地开发，你可以设置

* ``FAKE_CLUSTER_DEV="auto"``

这会将 ``ray/python/ray/autoscaler`` 目录挂载到已启动的节点。请注意，
这可能无法在您的 docker-in-docker 设置中工作。

如果你想指定要挂载哪些顶级 Ray 目录，你可以使用例如

* ``FAKE_CLUSTER_DEV_MODULES="autoscaler,tune"``

这将在节点容器内挂载 ``ray/python/ray/autoscaler`` 和 ``ray/python/ray/tune`` 。
模块列表应以逗号分隔，且不带空格。
