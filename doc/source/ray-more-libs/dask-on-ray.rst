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
3. 如果您想使用 Dask 提供的熟悉的 NumPy 和 Pandas API 创建数据分析，并在面向生产的快速、容错分布式任务执行系统「如 Ray」上执行它们。

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

通过 Ray 的 :ref:`对象溢出 <object-spilling>`，可以支持处理大于集群内存的数据集： 如果内存中的对象存储已满，对象将溢出到外部存储「默认情况下为本地磁盘」。此功能可用，但在 Ray 1.2 中默认关闭，在 Ray 1.3+ 中默认开启。请参阅您的 Ray 版本的对象溢出文档，了解启用和/或配置对象溢出的步骤。

持久化
-------

.. _dask-on-ray-persist:

Dask-on-Ray 修补了 `dask.persist()
<https://docs.dask.org/en/latest/api.html#dask.persist>`__  以匹配 `Dask
分布式持久语义
<https://distributed.dask.org/en/latest/manage-computation.html#client-persist>`__；即， 使用 Dask-on-Ray 调度程序进行 `dask.persist()` 将把任务提交给 Ray 集群并返回内联的 Ray 特性的 Dask 集合。 
如果您希望计算一些基础集合「例如 Dask 数组」，然后进行多个不同的下游计算「例如聚合」，那么这很好：
这些下游计算将更快，因为该基础集合计算很早就启动并被所有下游计算引用，通常通过共享内存。

.. literalinclude:: doc_code/dask_on_ray_persist_example.py
    :language: python


注释、资源和任务选项
----------------------------------------

.. _dask-on-ray-annotations:


Dask-on-Ray supports specifying resources or any other Ray task option via `Dask's
annotation API <https://docs.dask.org/en/stable/api.html#dask.annotate>`__. This
annotation context manager can be used to attach resource requests (or any other Ray task
option) to specific Dask operations, with the annotations funneling down to the
underlying Ray tasks. Resource requests and other Ray task options can also be specified
globally via the ``.compute(ray_remote_args={...})`` API, which will
serve as a default for all Ray tasks launched via the Dask workload. Annotations on
individual Dask operations will override this global default.

.. literalinclude:: doc_code/dask_on_ray_annotate_example.py
    :language: python

Note that you may need to disable graph optimizations since it can break annotations,
see `this Dask issue <https://github.com/dask/dask/issues/7036>`__.

Custom optimization for Dask DataFrame shuffling
------------------------------------------------

.. _dask-on-ray-shuffle-optimization:

Dask-on-Ray provides a Dask DataFrame optimizer that leverages Ray's ability to
execute multiple-return tasks in order to speed up shuffling by as much as 4x on Ray.
Simply set the `dataframe_optimize` configuration option to our optimizer function, similar to how you specify the Dask-on-Ray scheduler:

.. literalinclude:: doc_code/dask_on_ray_shuffle_optimization.py
    :language: python

Callbacks
---------

.. _dask-on-ray-callbacks:

Dask's `custom callback abstraction <https://docs.dask.org/en/latest/diagnostics-local.html#custom-callbacks>`__
is extended with Ray-specific callbacks, allowing the user to hook into the
Ray task submission and execution lifecycles.
With these hooks, implementing Dask-level scheduler and task introspection,
such as progress reporting, diagnostics, caching, etc., is simple.

Here's an example that measures and logs the execution time of each task using
the ``ray_pretask`` and ``ray_posttask`` hooks:

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __timer_callback_begin__
    :end-before: __timer_callback_end__

The following Ray-specific callbacks are provided:

   1. :code:`ray_presubmit(task, key, deps)`: Run before submitting a Ray
      task. If this callback returns a non-`None` value, a Ray task will _not_
      be created and this value will be used as the would-be task's result
      value.
   2. :code:`ray_postsubmit(task, key, deps, object_ref)`: Run after submitting
      a Ray task.
   3. :code:`ray_pretask(key, object_refs)`: Run before executing a Dask task
      within a Ray task. This executes after the task has been submitted,
      within a Ray worker. The return value of this task will be passed to the
      ray_posttask callback, if provided.
   4. :code:`ray_posttask(key, result, pre_state)`: Run after executing a Dask
      task within a Ray task. This executes within a Ray worker. This callback
      receives the return value of the ray_pretask callback, if provided.
   5. :code:`ray_postsubmit_all(object_refs, dsk)`: Run after all Ray tasks
      have been submitted.
   6. :code:`ray_finish(result)`: Run after all Ray tasks have finished
      executing and the final result has been returned.

See the docstring for
:meth:`RayDaskCallback.__init__() <ray.util.dask.callbacks.RayDaskCallback>.__init__`
for further details about these callbacks, their arguments, and their return
values.

When creating your own callbacks, you can use
:class:`RayDaskCallback <ray.util.dask.callbacks.RayDaskCallback>`
directly, passing the callback functions as constructor arguments:

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __ray_dask_callback_direct_begin__
    :end-before: __ray_dask_callback_direct_end__

or you can subclass it, implementing the callback methods that you need:

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __ray_dask_callback_subclass_begin__
    :end-before: __ray_dask_callback_subclass_end__

You can also specify multiple callbacks:

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __multiple_callbacks_begin__
    :end-before: __multiple_callbacks_end__

Combining Dask callbacks with an actor yields simple patterns for stateful data
aggregation, such as capturing task execution statistics and caching results.
Here is an example that does both, caching the result of a task if its
execution time exceeds some user-defined threshold:

.. literalinclude:: doc_code/dask_on_ray_callbacks.py
    :language: python
    :start-after: __caching_actor_begin__
    :end-before: __caching_actor_end__

.. note::
  The existing Dask scheduler callbacks (``start``, ``start_state``,
  ``pretask``, ``posttask``, ``finish``) are also available, which can be used to
  introspect the Dask task to Ray task conversion process, but note that the ``pretask``
  and ``posttask`` hooks are executed before and after the Ray task is *submitted*, not
  executed, and that ``finish`` is executed after all Ray tasks have been
  *submitted*, not executed.

This callback API is currently unstable and subject to change.
