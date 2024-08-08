.. _cluster-commands:

集群启动器命令
=========================

本文档概述了使用 Ray 集群启动器的常用命令。
参考 :ref:`集群配置 <cluster-config>` 文档，了解如何自定义配置文件。

启动集群 (``ray up``)
--------------------------------

这将启动云中的机器，安装依赖项并运行您拥有的任何设置命令，
自动配置 Ray 集群，并为您扩展分布式系统做好准备。 参考 ``ray up`` :ref:`文档
<ray-up-doc>`。示例配置文件可在 `这里 <https://github.com/ray-project/ray/tree/master/python/ray/autoscaler>`_ 访问。

.. tip:: 工作节点仅在头节点启动完成后才会启动。
         要监控集群设置的进度，您可以运行
         `ray monitor <cluster yaml>`。

.. code-block:: shell

    # Replace '<your_backend>' with one of: 'aws', 'gcp', 'kubernetes', or 'local'.
    $ BACKEND=<your_backend>

    # Create or update the cluster.
    $ ray up ray/python/ray/autoscaler/$BACKEND/example-full.yaml

    # Tear down the cluster.
    $ ray down ray/python/ray/autoscaler/$BACKEND/example-full.yaml

更新现有集群 (``ray up``)
-----------------------------------------

如果您想更新集群配置（添加更多文件、更改依赖项），请在现有集群上再次运行 ``ray up`` 。

此命令检查本地配置是否与集群的应用配置不同。
这包括对配置文件中 ``file_mounts`` 部分中指定的同步文件的任何更改。
如果是，则新文件和配置将上传到集群。之后，Ray 服务/进程将重新启动。

.. tip:: 不要针对云提供商规范（例如，在运行中的集群上
         从 AWS 更改为 GCP）或更改集群名称（因为
         这将启动一个新集群并使原始集群变为孤立）。


如果集群看起来处于不良状态，您还可以运行 ``ray up`` 以重新启动
集群（即使没有配置更改，这也将重新启动所有 Ray 服务）。

在现有集群上运行 ``ray up`` 将执行以下所有操作：

* 如果头节点与集群规范匹配，则将重新应用文件挂载
  并运行 ``setup_commands`` 和 ``ray start`` 命令。
  此处可能存在一些缓存行为以跳过设置/文件挂载。
* 如果头节点与指定的 YAML 不符（例如，
  ``head_node_type`` 在 YAML 上已发生更改），则将终止过期的节点，
  并配置新节点来替换它。 设置/文件
  挂载/``ray start`` 会应用。
* 当头节点达到一致状态后（ ``ray start`` 命令
  完成后），上述相同过程将应用于所有工作
  节点。``ray start`` 命令倾向于运行 ``ray stop`` + ``ray start``，
  因此这将终止当前正在运行的作业。

如果您不希望更新重新启动服务（例如因为更改
不需要重新启动），请传递 ``--no-restart`` 到更新调用。

如果您想强制重新生成配置以获取云环境中
可能的变化，请传递 ``--no-config-cache`` 到更新调用。

如果您想跳过设置命令并仅在所有节点上运行 ``ray stop``/ ``ray start``
请传递 ``--restart-only`` 到更新调用。

请参阅的 ``ray up`` :ref:`文档 <ray-up-doc>` 。

.. code-block:: shell

    # Reconfigure autoscaling behavior without interrupting running jobs.
    $ ray up ray/python/ray/autoscaler/$BACKEND/example-full.yaml \
        --max-workers=N --no-restart

在集群上运行 shell 命令 (``ray exec``)
----------------------------------------------------

您可以使用 ``ray exec`` 来方便地在集群上运行命令。请参阅 ``ray exec`` :ref:`文档 <ray-exec-doc>` 。


.. code-block:: shell

    # Run a command on the cluster
    $ ray exec cluster.yaml 'echo "hello world"'

    # Run a command on the cluster, starting it if needed
    $ ray exec cluster.yaml 'echo "hello world"' --start

    # Run a command on the cluster, stopping the cluster after it finishes
    $ ray exec cluster.yaml 'echo "hello world"' --stop

    # Run a command on a new cluster called 'experiment-1', stopping it after
    $ ray exec cluster.yaml 'echo "hello world"' \
        --start --stop --cluster-name experiment-1

    # Run a command in a detached tmux session
    $ ray exec cluster.yaml 'echo "hello world"' --tmux

    # Run a command in a screen (experimental)
    $ ray exec cluster.yaml 'echo "hello world"' --screen

如果要在集群上运行可以通过 Web 浏览器访问的
应用程序（例如 Jupyter Notebook），则可以使用 ``--port-forward``。打开的本地端口
与远程端口相同。

.. code-block:: shell

    $ ray exec cluster.yaml --port-forward=8899 'source ~/anaconda3/bin/activate tensorflow_p36 && jupyter notebook --port=8899'

.. note:: 对于 Kubernetes 集群， ``port-forward`` 选项在
          命令执行时无法使用。 要进行端口转发并运行命令，您需要
          分别调用两次 ``ray exec`` 命令。

在集群上运行 Ray 脚本 (``ray submit``)
---------------------------------------------------

您还可以使用 ``ray submit`` 在集群上执行 Python 脚本。 这会
将 ``rsync`` 指定的文件放到头节点集群上并使用
给定的参数执行它。参考 ``ray submit`` :ref:`文档 <ray-submit-doc>` 。

.. code-block:: shell

    # Run a Python script in a detached tmux session
    $ ray submit cluster.yaml --tmux --start --stop tune_experiment.py

    # Run a Python script with arguments.
    # This executes script.py on the head node of the cluster, using
    # the command: python ~/script.py --arg1 --arg2 --arg3
    $ ray submit cluster.yaml script.py -- --arg1 --arg2 --arg3


连接到正在运行的集群 (``ray attach``)
-----------------------------------------------

你可以使用 ``ray attach`` 连接到集群上的交互式屏幕会话。
请参阅 ``ray attach`` :ref:`文档 <ray-attach-doc>` 或
运行 ``ray attach --help``。

.. code-block:: shell

    # Open a screen on the cluster
    $ ray attach cluster.yaml

    # Open a screen on a new cluster called 'session-1'
    $ ray attach cluster.yaml --start --cluster-name=session-1

    # Attach to tmux session on cluster (creates a new one if none available)
    $ ray attach cluster.yaml --tmux

.. _ray-rsync:

从集群同步文件 (``ray rsync-up/down``)
------------------------------------------------------------

要下载或上传文件到簇头节点，请使用 ``ray rsync_down`` 或
``ray rsync_up``：

.. code-block:: shell

    $ ray rsync_down cluster.yaml '/path/on/cluster' '/local/path'
    $ ray rsync_up cluster.yaml '/local/path' '/path/on/cluster'

.. _monitor-cluster:

监视群集状态 (``ray dashboard/status``)
-----------------------------------------------------

Ray 还带有一个在线仪表板。仪表板可通过头节点上
的 HTTP 访问（默认情况下，它监听 ``localhost:8265``）。您还可以使用
内置功能  ``ray dashboard``  自动设置端口转发，
使远程仪表板可在本地浏览器中查看
``localhost:8265``。

.. code-block:: shell

    $ ray dashboard cluster.yaml

您可以通过运行（在头节点上）来监视集群使用情况和自动扩展状态：

.. code-block:: shell

    $ ray status

要查看状态的实时更新：

.. code-block:: shell

    $ watch -n 1 ray status

Ray 自动缩放器还以实例标签的形式报告每个节点的状态。
在云提供商控制台中，您可以单击某个节点，转到“标签”窗格，
然后将标签 ``ray-node-status`` 添加为一列。 这样
您就可以一目了然地查看每个节点的状态：

.. image:: /images/autoscaler-status.png

常见工作流程：同步 git 分支
-------------------------------------

一个常见的用例是将特定的本地 git 分支同步到集群的所有
工作器。但是，如果您只是在设置命令中输入 `git checkout <branch>` ，
自动缩放器将不知道何时重新运行命令以提取更新。
有一个很好的解决方法，即在输入中
包含 git SHA（如果分支更新，文件的哈希值将发生变化）：

.. code-block:: yaml

    file_mounts: {
        "/tmp/current_branch_sha": "/path/to/local/repo/.git/refs/heads/<YOUR_BRANCH_NAME>",
    }

    setup_commands:
        - test -e <REPO_NAME> || git clone https://github.com/<REPO_ORG>/<REPO_NAME>.git
        - cd <REPO_NAME> && git fetch && git checkout `cat /tmp/current_branch_sha`

这告诉 ``ray up`` 将当前 git 分支 SHA 从您的个人计算机同步到
集群上的临时文件（假设您已经推送了分支头）。
然后，设置命令读取该文件以确定节点上应该检出哪个 SHA。
请注意，每个命令都在自己的会话中运行。
然后更新集群的最终工作流程就变成了这样：

1. 对 git 分支进行本地更改
2. 使用 ``git commit`` 和 ``git push`` 提交更改
3. 在你的 Ray 集群使用 ``ray up`` 更新文件
