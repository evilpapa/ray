.. _vm-cluster-quick-start:

入门
===============

此快速入门演示了 Ray 集群的功能。使用 Ray 集群，我们将采用一个设计为在笔记本电脑上运行的示例应用程序，并将其扩展到云中。Ray 将仅使用几个命令启动集群并扩展 Python。

要手动启动 Ray 集群，您可以参考 :ref:`本地集群设置 <on-prem>` 指南。

关于演示
--------------

此演示将介绍端到端流程：

1. 创建一个「基本」Python 应用程序。
2. 在云提供商上启动集群。
3. 在云中运行该应用程序。

要求
~~~~~~~~~~~~

要运行此演示，您需要：

* 在你的开发机器「通常是笔记本电脑」上安装 Python，并且
* 具有您首选的云提供商 (AWS、GCP、Azure、阿里云或 vSphere) 的帐户。

设置
~~~~~

在开始之前，您需要安装一些 Python 依赖项，如下所示：

.. tabs::

   .. tab:: Ray 团队支持

      .. tabs::

         .. tab:: AWS

            .. code-block:: shell

                $ pip install -U "ray[default]" boto3

         .. tab:: GCP

            .. code-block:: shell

                $ pip install -U "ray[default]" google-api-python-client

   .. tab:: 社区支持

      .. tabs::

         .. tab:: Azure

            .. code-block:: shell

                $ pip install -U "ray[default]" azure-cli azure-core

         .. tab:: Aliyun

            .. code-block:: shell

                $ pip install -U "ray[default]" aliyun-python-sdk-core aliyun-python-sdk-ecs
            
            阿里云集群启动器维护者「GitHub 账号」：@zhuangzhuang131419、@chenk008

         .. tab:: vSphere

            .. code-block:: shell

                $ pip install -U "ray[default]" "git+https://github.com/vmware/vsphere-automation-sdk-python.git"

            vSphere Cluster Launcher 维护者「GitHub 帐号」：@LaynePeng、@roshankathawate、@JingChen23


接下来，如果您尚未设置从命令行使用云提供商，则必须配置您的凭据：

.. tabs::

   .. tab:: Ray 团队支持

      .. tabs::

         .. tab:: AWS

            Configure your credentials in ``~/.aws/credentials`` as described in `the AWS docs <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html>`_.

         .. tab:: GCP

            Set the ``GOOGLE_APPLICATION_CREDENTIALS`` environment variable as described in `the GCP docs <https://cloud.google.com/docs/authentication/getting-started>`_.

   .. tab:: 社区支持

      .. tabs::

         .. tab:: Azure

            使用 ``az login`` 登录，然后使用 ``az account set -s <subscription_id>`` 配置凭证。

         .. tab:: Aliyun

            按照 `文档 <https://www.alibabacloud.com/help/en/doc-detail/175967.htm>`__ 获取并设置阿里云账户的 AccessKey 对。

            确保向 RAM 用户授予必要的权限并在集群配置文件中设置 AccessKey 对。
            请参阅提供的 `aliyun/example-full.yaml </ray/python/ray/autoscaler/aliyun/example-full.yaml>`__ 以获取示例集群配置。

         .. tab:: vSphere

            .. code-block:: shell

                $ export VSPHERE_SERVER=192.168.0.1 # Enter your vSphere vCenter Address
                $ export VSPHERE_USER=user # Enter your username
                $ export VSPHERE_PASSWORD=password # Enter your password


创建一个「基本」Python 应用
-----------------------------------

我们将编写一个简单的 Python 应用程序来跟踪执行其任务的机器的 IP 地址：

.. code-block:: python

    from collections import Counter
    import socket
    import time

    def f():
        time.sleep(0.001)
        # Return IP address.
        return socket.gethostbyname(socket.gethostname())

    ip_addresses = [f() for _ in range(10000)]
    print(Counter(ip_addresses))

将此应用程序另存为 ``script.py`` 并通过运行 ``python script.py``命令来执行它。该应用程序应需要 10 秒钟才能运行并输出类似于 ``Counter({'127.0.0.1': 10000})`` 的内容。

通过一些小的改动，我们可以让这个应用程序在 Ray 上运行「有关如何执行此操作的更多信息，请参阅 :ref:`the Ray Core Walkthrough <core-walkthrough>`):

.. code-block:: python

    from collections import Counter
    import socket
    import time

    import ray

    ray.init()

    @ray.remote
    def f():
        time.sleep(0.001)
        # Return IP address.
        return socket.gethostbyname(socket.gethostname())

    object_ids = [f.remote() for _ in range(10000)]
    ip_addresses = ray.get(object_ids)
    print(Counter(ip_addresses))

最后，让我们添加一些代码，使输出更有趣：

.. code-block:: python

    from collections import Counter
    import socket
    import time

    import ray

    ray.init()

    print('''This cluster consists of
        {} nodes in total
        {} CPU resources in total
    '''.format(len(ray.nodes()), ray.cluster_resources()['CPU']))

    @ray.remote
    def f():
        time.sleep(0.001)
        # Return IP address.
        return socket.gethostbyname(socket.gethostname())

    object_ids = [f.remote() for _ in range(10000)]
    ip_addresses = ray.get(object_ids)

    print('Tasks executed')
    for ip_address, num_tasks in Counter(ip_addresses).items():
        print('    {} tasks on {}'.format(num_tasks, ip_address))

运行 ``python script.py`` 应该输出类似的内容：

.. parsed-literal::

    This cluster consists of
        1 nodes in total
        4.0 CPU resources in total

    Tasks executed
        10000 tasks on 127.0.0.1

在云服务上启动集群
------------------------------------

要启动 Ray 集群，首先我们需要定义集群配置。集群配置在 YAML 文件中定义，Cluster Launcher 将使用该文件启动头节点，Autoscaler 将使用该文件启动工作节点。

最小示例集群配置文件如下所示：

.. tabs::

   .. tab:: Ray 团队支持

      .. tabs::

         .. tab:: AWS

            .. literalinclude:: ../../../../python/ray/autoscaler/aws/example-minimal.yaml
               :language: yaml

         .. tab:: GCP

            .. code-block:: yaml

                # A unique identifier for the head node and workers of this cluster.
                cluster_name: minimal

                # Cloud-provider specific configuration.
                provider:
                    type: gcp
                    region: us-west1

   .. tab:: 社区支持

      .. tabs::

         .. tab:: Azure

            .. code-block:: yaml

                # An unique identifier for the head node and workers of this cluster.
                cluster_name: minimal

                # Cloud-provider specific configuration.
                provider:
                    type: azure
                    location: westus2
                    resource_group: ray-cluster

                # How Ray will authenticate with newly launched nodes.
                auth:
                    ssh_user: ubuntu
                    # you must specify paths to matching private and public key pair files
                    # use `ssh-keygen -t rsa -b 4096` to generate a new ssh key pair
                    ssh_private_key: ~/.ssh/id_rsa
                    # changes to this should match what is specified in file_mounts
                    ssh_public_key: ~/.ssh/id_rsa.pub

         .. tab:: Aliyun

            参考 `example-full.yaml </ray/python/ray/autoscaler/aliyun/example-full.yaml>`__。

            确保账户余额不少于 100 人民币，否则会收到 `InvalidAccountStatus.NotEnoughBalance` 错误。

         .. tab:: vSphere

            .. literalinclude:: ../../../../python/ray/autoscaler/vsphere/example-minimal.yaml
               :language: yaml


将此配置文件另存为 ``config.yaml``。您可以在配置文件中指定更多详细信息：要使用的实例类型、要启动的最小和最大工作程序数量、自动扩展策略、要同步的文件等。有关可用配置属性的完整参考，请参阅 :ref:`集群 YAML 配置项参考 <cluster-config>`。

定义配置后，我们将使用 Ray 集群启动器在云上启动集群，创建指定的“头节点”和工作节点。要启动 Ray 集群，我们将使用:ref:`Ray CLI <ray-cluster-cli>`。运行以下命令：

.. code-block:: shell

    $ ray up -y config.yaml

在 Ray Cluster 上运行应用
-------------------------------------

我们现在准备在 Ray Cluster 上执行应用程序。
``ray.init()`` 现在将自动连接到新创建的集群。

作为一个简单的例子，我们在连接到 Ray 并退出的 Ray Cluster 上执行一个 Python 命令：

.. code-block:: shell

    $ ray exec config.yaml 'python -c "import ray; ray.init()"'
    2022-08-10 11:23:17,093 INFO worker.py:1312 -- Connecting to existing Ray cluster at address: <remote IP address>:6379...
    2022-08-10 11:23:17,097 INFO worker.py:1490 -- Connected to Ray cluster.

您还可以  ``ray attach``  选择使用远程 shell 并直接在集群上运行命令。 此命令将创建与 Ray 集群头节点的 SSH 连接。

.. code-block:: shell

    # From a remote client:
    $ ray attach config.yaml

    # Now on the head node...
    $ python -c "import ray; ray.init()"

有关 Ray Cluster CLI 工具的完整参考，请参阅 :ref:`集群命令参考 <cluster-commands>`。

虽然这些工具对于在 Ray Cluster 上临时执行很有用，但在 Ray Cluster 上执行应用程序的推荐方法是使用 :ref:`Ray Jobs <jobs-quickstart>`。查看 :ref:`快速入门指南 <jobs-quickstart>` 以开始使用！

删除 Ray 集群
----------------------

要关闭集群，请运行以下命令：

.. code-block:: shell

    $ ray down -y config.yaml
