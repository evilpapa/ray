.. _modin-on-ray:

Ray 上使用 Pandas 「Modin」
===========================

Modin_「前身为 Pandas on Ray」是一个数据框操作库，
它允许用户通过充当替代品来加快他们的 pandas 工作负载。
Modin 还支持其他 API「例如电子表格」和库，例如 xgboost。

.. code-block:: python

   import modin.pandas as pd
   import ray

   ray.init()
   df = pd.read_parquet("s3://my-bucket/big.parquet")

您可以在笔记本电脑或集群上使用 Ray 上的 Modin。
在本文档中，我们将介绍如何设置兼容 Modin 的 Ray 集群
以及如何将 Modin 连接到 Ray。

.. note:: 在之前的 Modin 版本中，您必须在导入 Modin 之前初始化 Ray。从 Modin 0.9.0 开始，这种情况不再存在。

将 Modin 与 Ray 的自动缩放器结合
---------------------------------

为了将 Modin 与 :ref:`Ray 自动缩放 <cluster-index>`一起使用，您需要确保在启动时安装了正确的依赖项。
Modin 的存储库有一个示例 `yaml 文件和一组 notebook 教程`_ t，以确保 Ray 集群具有正确的依赖项。
集群启动后，只需导入即可连接 Modin。

.. code-block:: python

   import modin.pandas as pd
   import ray

   ray.init(address="auto")
   df = pd.read_parquet("s3://my-bucket/big.parquet")

只要在创建任何数据帧之前初始化 Ray，
Modin 就能够连接并使用 Ray 集群。

Modin 如何使用 Ray
------------------

Modin 具有分层架构，数据操作的核心抽象是 Modin Dataframe，
它实现了一种新颖的代数，
使 Modin 能够处理所有 pandas 有关架构的更多信息，请参阅 Modin 的 `文档`_ 」。
Modin 的内部数据框对象有一个调度层，可以使用 Ray 对数据进行分区和操作。

Dataframe 操作
''''''''''''''''''''

Modin Dataframe 使用 Ray 任务来执行数据操作。与 Actor 模型相比，
Ray 任务在数据操作方面具有许多优势：

- 多个任务可能同时操作同一对象
- Ray 的对象存储中的对象是不可变的，这使得来源和血统更容易追踪
- 随着新 worker 上线，数据将随着新节点上的任务安排而发生变动
- 相同的分区不需要复制，这对于选择性改变数据的操作特别有益「例如 ``fillna``」。
- 更细粒度的并行性和更细粒度的布局控制

机器学习
''''''''''''''''

Modin 使用 Ray Actors 来提供其当前提供的机器学习支持。
Modin 的 XGBoost 实现能够为每个节点启动一个 Actor，
并将该节点上的所有分区聚合到 XGBoost Actor。
Modin 能够在创建时精确指定每个 Actor 的节点 IP，
从而对布局进行细粒度控制 - 这是分布式训练性能的必备条件。

.. _Modin: https://github.com/modin-project/modin
.. _文档: https://modin.readthedocs.io/en/latest/development/architecture.html
.. _yaml 文件和一组 notebook 教程: https://github.com/modin-project/modin/tree/master/examples/tutorial/jupyter/execution/pandas_on_ray/cluster
