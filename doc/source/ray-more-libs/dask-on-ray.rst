.. _dask-on-ray:

在 Ray 上使用 Dask
=================


`Dask <https://dask.org/>`__ 是一个 Python 并行计算库，旨在扩展分析和科学计算工作负载。
他提供了 `大数据集合
<https://docs.dask.org/en/latest/user-interfaces.html>`__ 模仿熟悉的
 `NumPy <https://numpy.org/>`__ 和 `Pandas <https://pandas.pydata.org/>`__ 库，
允许这些抽象表示大于内存的数据和/或允许在多机集群上运行对该数据的操作，
同时还提供自动数据并行、智能调度和优化操作。
对这些集合的操作会创建一个任务图，该任务图由调度程序执行。

Ray 为 Dask 提供了一个调度程序 (`dask_on_ray`) ，允许您使用 Dask 的集合构建数据分析
并在 Ray 集群上执行底层任务。

`dask_on_ray` 使用 Dask 的调度程序 API，
它允许您指定任何可调用函数作为您希望 Dask 用来执行工作负载的调度程序。
使用 Dask-on-Ray 调度程序，整个 Dask 生态系统都可以在 Ray 之上执行。

.. note::
   我们始终确保最新的 Dask 版本与 Ray Nightly 兼容。
   下表显示了与 Ray 版本一起测试的最新 Dask 版本。

  .. list-table:: 每个 Ray 版本的最新 Dask 版本。
     :header-rows: 1

     * - Ray 版本
       - Dask 版本
     * - ``2.7.0``
       - | ``2022.2.0 (Python version < 3.8)``
         | ``2022.10.1 (Python version >= 3.8)``
     * - ``2.6.0``
       - | ``2022.2.0 (Python version < 3.8)``
         | ``2022.10.1 (Python version >= 3.8)``
     * - ``2.5.0``
       - | ``2022.2.0 (Python version < 3.8)``
         | ``2022.10.1 (Python version >= 3.8)``
     * - ``2.4.0``
       - ``2022.10.1``
     * - ``2.3.0``
       - ``2022.10.1``
     * - ``2.2.0``
       - ``2022.10.1``
     * - ``2.1.0``
       - ``2022.2.0``
     * - ``2.0.0``
       - ``2022.2.0``
     * - ``1.13.0``
       - ``2022.2.0``
     * - ``1.12.0``
       - ``2022.2.0``
     * - ``1.11.0``
       - ``2022.1.0``
     * - ``1.10.0``
       - ``2021.12.0``
     * - ``1.9.2``
       - ``2021.11.0``
     * - ``1.9.1``
       - ``2021.11.0``
     * - ``1.9.0``
       - ``2021.11.0``
     * - ``1.8.0``
       - ``2021.9.1``
     * - ``1.7.0``
       - ``2021.9.1``
     * - ``1.6.0``
       - ``2021.8.1``
     * - ``1.5.0``
       - ``2021.7.0``
     * - ``1.4.1``
       - ``2021.6.1``
     * - ``1.4.0``
       - ``2021.5.0``

Scheduler
---------

.. _dask-on-ray-scheduler:

Dask-on-Ray 调度程序可以执行任何有效的 Dask 图，并且可以与任何 Dask `.compute() <https://docs.dask.org/en/latest/api.html#dask.compute>`__
调用一起使用。
这是一个例子：

.. literalinclude:: doc_code/dask_on_ray_scheduler_example.py
    :language: python

.. note::
  要在 Ray 集群上执行，您 *不应* 使用
  `Dask.distributed <https://distributed.dask.org/en/latest/quickstart.html>`__
  客户端； 只需使用普通的 Dask 及其集合，并传递 ``ray_dask_get``
  到 ``.compute()`` 调用，在 `此处 <https://docs.dask.org/en/latest/scheduling.html#configuration>`__ 以其他详述的方式之一设置调度程序，或使用我们的 ``enable_dask_on_ray`` 配置助手。按照
  :ref:`在集群上使用 Ray <cluster-index>` 来修改
  ``ray.init()`` 调用。

为什么在 Ray 上使用 Dask ？

1. 要利用 Ray 特有的功能，例如
      :ref:`启动云集群 <cluster-index>` 和
      :ref:`共享内存存储 <memory>`。
2. 如果您想在同一个应用程序中使用 Dask 和 Ray 库，而无需两个不同的集群。
3. 如果您想使用 Dask 提供的熟悉的 NumPy 和 Pandas API 创建数据分析，并在面向生产的快速、容错分布式任务执行系统（如 Ray）上执行它们。

Dask-on-Ray 是一个正在进行的项目，预计不会达到与直接使用 Ray 相同的性能。 所有 `Dask 抽象 <https://docs.dask.org/en/latest/user-interfaces.html>`__ 都应该使用此调度程序在 Ray 上无缝运行，因此如果您发现其中一个抽象无法在 Ray 上运行，请 `打开一个问题 <https://github.com/ray-project/ray/issues/new/choose>`__。

大规模工作负载的最佳实践
---------------------------------------
对于 Ray 1.3，默认调度策略是尽可能将任务打包到同一节点。
如果您在 Ray 工作负载上运行大规模/内存密集型 Dask，则更希望分散任务。

在这种情况下，有两种推荐的设置。
- 减少配置 `scheduler_spread_threshold` 标志以告诉调度程序优先在集群中分散任务而不是打包。
- 将头节点设置 `num-cpus` 为 0，以便不在头节点上安排任务。

.. code-block:: bash

  # Head node. Set `num_cpus=0` to avoid tasks are being scheduled on a head node.
  RAY_scheduler_spread_threshold=0.0 ray start --head --num-cpus=0

  # Worker node.
  RAY_scheduler_spread_threshold=0.0 ray start --address=[head-node-address]

核心外数据处理
---------------------------

.. _dask-on-ray-out-of-core:

通过 Ray 的 :ref:`对象溢出 <object-spilling>`，可以支持处理大于集群内存的数据集： 如果内存中的对象存储已满，对象将溢出到外部存储（默认情况下为本地磁盘）。此功能可用，但在 Ray 1.2 中默认关闭，在 Ray 1.3+ 中默认开启。请参阅您的 Ray 版本的对象溢出文档，了解启用和/或配置对象溢出的步骤。

持久化
-------

.. _dask-on-ray-persist:

Dask-on-Ray 修补了 `dask.persist()
<https://docs.dask.org/en/latest/api.html#dask.persist>`__  以匹配 `Dask
分布式持久语义
<https://distributed.dask.org/en/latest/manage-computation.html#client-persist>`__；即， 使用 Dask-on-Ray 调度程序进行 `dask.persist()` 将把任务提交给 Ray 集群并返回内联的 Ray 特性的 Dask 集合。 
如果您希望计算一些基础集合（例如 Dask 数组），然后进行多个不同的下游计算（例如聚合），那么这很好：
这些下游计算将更快，因为该基础集合计算很早就启动并被所有下游计算引用，通常通过共享内存。

.. literalinclude:: doc_code/dask_on_ray_persist_example.py
    :language: python


注释、资源和任务选项
----------------------------------------

.. _dask-on-ray-annotations:


Dask-on-Ray 支持通过 `Dask 注解
 API <https://docs.dask.org/en/stable/api.html#dask.annotate>`__ 指定资源或任何其他 Ray 任务选项 。
This此注释上下文管理器可用于将资源请求（或任何其他 Ray 任务选项）附加到特定的 Dask 操作，注释将汇集到底层 Ray 任务。
资源请求和其他 Ray 任务选项也可以通过 ``.compute(ray_remote_args={...})`` API 全局指定，
这将作为通过 Dask 工作负载启动的所有 Ray 任务的默认值。
单个 Dask 操作上的注释将覆盖此全局默认值。

.. literalinclude:: doc_code/dask_on_ray_annotate_example.py
    :language: python

请注意，您可能需要禁用图形优化，因为它可能会破坏注释，
请参阅 `此 Dask 问题 <https://github.com/dask/dask/issues/7036>`__。

Dask DataFrame shuffle 的自定义优化
------------------------------------------------

.. _dask-on-ray-shuffle-optimization:

Dask-on-Ray 提供了一个 Dask DataFrame 优化器，它利用 Ray 执行多返回任务的能力，
从而将 Ray 上的 shuffling 速度提高 4 倍。
只需将配置选项 `dataframe_optimize` 设置为我们的优化器函数，类似于指定 Dask-on-Ray 调度程序的方式：

.. literalinclude:: doc_code/dask_on_ray_shuffle_optimization.py
    :language: python

回调
---------

.. _dask-on-ray-callbacks:

Dask 的 `自定义毁掉抽象 <https://docs.dask.org/en/latest/diagnostics-local.html#custom-callbacks>`__
通过 Ray 特定的回调进行了扩展，允许用户 hook 到 Ray 任务提交和执行生命周期。
借助这些 hook ，实现 Dask 级调度程序和
任务自省（例如进度报告、诊断、缓存等）非常简单。

下面是使用  ``ray_pretask``  和 ``ray_posttask`` 钩子测量和记录每个任务执行时间的示例：

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __timer_callback_begin__
    :end-before: __timer_callback_end__

提供了以下特定于 Ray 的回调：

   1. :code:`ray_presubmit(task, key, deps)`: 在提交 Ray 任务之前运行。
      如果此回调返回非 `None` 值，Ray 任务将 _不会_，并且该值将用作即将执行的任务的结果值。
   2. :code:`ray_postsubmit(task, key, deps, object_ref)`: 提交 Ray 任务后运行。
   3. :code:`ray_pretask(key, object_refs)`: 在 Ray 任务中执行 Dask 任务之前运行。
      这将在任务提交后在 Ray 工作器中执行。
      此任务的返回值将传递给 ray_posttask 回调（如果提供）。
   4. :code:`ray_posttask(key, result, pre_state)`: 在 Ray 任务中执行 Dask 任务后运行。
      这将在 Ray 工作器中执行。
      此回调接收 ray_pretask 回调的返回值（如果提供）。
   5. :code:`ray_postsubmit_all(object_refs, dsk)`: 所有 Ray 任务均已提交后运行。
   6. :code:`ray_finish(result)`: 所有 Ray 任务均执行完毕并返回最终结果后运行。

有关这些回调、它们的参数和返回值的更多详细信息，请参阅文档字符串
:meth:`RayDaskCallback.__init__() <ray.util.dask.callbacks.RayDaskCallback>.__init__`。

创建自己的回调时，您可以直接使用
:class:`RayDaskCallback <ray.util.dask.callbacks.RayDaskCallback>`
，将回调函数作为构造函数参数传递：

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __ray_dask_callback_direct_begin__
    :end-before: __ray_dask_callback_direct_end__

或者你可以将其子类化，实现你需要的回调方法：

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __ray_dask_callback_subclass_begin__
    :end-before: __ray_dask_callback_subclass_end__

您还可以指定多个回调：

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __multiple_callbacks_begin__
    :end-before: __multiple_callbacks_end__

将 Dask 回调与 Actor 结合起来，可以产生简单的状态数据聚合模式，
例如捕获任务执行统计信息和缓存结果。
下面是一个同时执行这两个操作的示例，
如果任务的执行时间超过某个用户定义的阈值，则缓存任务的结果：

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __caching_actor_begin__
    :end-before: __caching_actor_end__

.. note::
  现有的 Dask 调度程序回调 (``start``、 ``start_state``、
  ``pretask``、 ``posttask``、 ``finish``) 同样可用，可用于
  自省 Dask 任务到 Ray 任务的转换过程， 但请注意， ``pretask``
  和 ``posttask`` 钩子是在 Ray 任务 *提交* 之前和之后执行的，而不是
  运行中执行， ``finish`` 是在所有 Ray 任务
  *提交* 之后执行，而不是执行时执行。

此回调 API 目前不稳定，可能会发生变化。
