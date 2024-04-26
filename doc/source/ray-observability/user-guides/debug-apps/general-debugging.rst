.. _observability-general-debugging:

一般调试
=======================

分布式应用程序比非分布式应用程序更强大但更复杂。 Ray 的某些行为可能会让用户措手不及，而这些设计选择可能有合理的论据。

此页面列出了用户可能遇到的一些常见问题。特别是，用户认为 Ray 在本地计算机上运行，​​虽然有时确实如此，但这会导致很多问题。

环境变量不会从Driver进程传递到Worker进程
---------------------------------------------------------------------------------

**问题**: 如果您在命令行（运行驱动程序的位置）设置环境变量，并且集群之前已启动，则该环境变量不会传递给集群中运行的所有工作线程。

**示例**: 如果运行 Ray 的目录中有一个文件 ``baz.py`` ，则运行以下命令：

.. literalinclude:: /ray-observability/doc_code/gotchas.py
  :language: python
  :start-after: __env_var_start__
  :end-before: __env_var_end__

**预期行为**: 大多数人会期望（就好像它是一台机器上的单个进程一样）所有 Worker 中的环境变量都是相同的。不会是这样的。

**修复**: 使用运行时环境显式传递环境变量。
如果您调用 ``ray.init(runtime_env=...)``，
那么 Workers 将设置环境变量。


.. literalinclude:: /ray-observability/doc_code/gotchas.py
  :language: python
  :start-after: __env_var_fix_start__
  :end-before: __env_var_fix_end__


文件名有时有效，有时无效
-----------------------------------------------

**问题**: 如果您在任务或参与者中按名称引用文件，它有时会起作用，有时会失败。
这是因为如果任务或 actor 运行在集群的头节点上，它就会工作，
但如果任务或 actor 运行在另一台机器上，它就不会工作。

**示例**: 假设我们执行以下命令：

.. code-block:: bash

	% touch /tmp/foo.txt

我有这个代码：

.. testcode::

  import os
  import ray

  @ray.remote
  def check_file():
    foo_exists = os.path.exists("/tmp/foo.txt")
    return foo_exists

  futures = []
  for _ in range(1000):
    futures.append(check_file.remote())

  print(ray.get(futures))


那么你会得到 True 和 False 的混合结果。 如果
``check_file()`` 在头节点上运行，或者我们在本地运行，它就可以工作。
但如果它在工作节点上运行，则会返回 ``False``。

**预期行为**: M大多数人会期望这要么失败要么成功。毕竟是相同的代码。

**修复**

- 仅对此类应用程序使用共享路径 - 例如，如果您使用网络文件系统，则可以使用该系统，或者文件可以位于 S3 上。
- 不要依赖文件路径一致性。



占位组不可组合
-----------------------------------

**问题**: If you have a task that is called from something that runs in a Placement
Group, the resources are never allocated and it hangs.

**Example**: You are using Ray Tune which creates Placement Groups, and you want to
apply it to an objective function, but that objective function makes use
of Ray Tasks itself, e.g.

.. testcode::

  import ray
  from ray import tune

  def create_task_that_uses_resources():
    @ray.remote(num_cpus=10)
    def sample_task():
      print("Hello")
      return

    return ray.get([sample_task.remote() for i in range(10)])

  def objective(config):
    create_task_that_uses_resources()

  tuner = tune.Tuner(objective, param_space={"a": 1})
  tuner.fit()

This will error with message:

.. testoutput::
  :options: +MOCK

    ValueError: Cannot schedule create_task_that_uses_resources.<locals>.sample_task with the placement group
    because the resource request {'CPU': 10} cannot fit into any bundles for the placement group, [{'CPU': 1.0}].

**Expected behavior**: The above executes.

**Fix**: In the ``@ray.remote`` declaration of Tasks
called by ``create_task_that_uses_resources()`` , include a
``scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=None)``.

.. code-block:: diff

  def create_task_that_uses_resources():
  +     @ray.remote(num_cpus=10, scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=None))
  -     @ray.remote(num_cpus=10)

Outdated Function Definitions
-----------------------------

Due to subtleties of Python, if you redefine a remote function, you may not
always get the expected behavior. In this case, it may be that Ray is not
running the newest version of the function.

Suppose you define a remote function ``f`` and then redefine it. Ray should use
the newest version.

.. testcode::

  import ray

  @ray.remote
  def f():
      return 1

  @ray.remote
  def f():
      return 2

  print(ray.get(f.remote()))  # This should be 2.

.. testoutput::

  2

However, the following are cases where modifying the remote function will
not update Ray to the new version (at least without stopping and restarting
Ray).

- **The function is imported from an external file:** In this case,
  ``f`` is defined in some external file ``file.py``. If you ``import file``,
  change the definition of ``f`` in ``file.py``, then re-``import file``,
  the function ``f`` will not be updated.

  This is because the second import gets ignored as a no-op, so ``f`` is
  still defined by the first import.

  A solution to this problem is to use ``reload(file)`` instead of a second
  ``import file``. Reloading causes the new definition of ``f`` to be
  re-executed, and exports it to the other machines. Note that in Python 3, you
  need to do ``from importlib import reload``.

- **The function relies on a helper function from an external file:**
  In this case, ``f`` can be defined within your Ray application, but relies
  on a helper function ``h`` defined in some external file ``file.py``. If the
  definition of ``h`` gets changed in ``file.py``, redefining ``f`` will not
  update Ray to use the new version of ``h``.

  This is because when ``f`` first gets defined, its definition is shipped to
  all of the Worker processes, and is unpickled. During unpickling, ``file.py`` gets
  imported in the Workers. Then when ``f`` gets redefined, its definition is
  again shipped and unpickled in all of the Workers. But since ``file.py``
  has been imported in the Workers already, it is treated as a second import
  and is ignored as a no-op.

  Unfortunately, reloading on the Driver does not update ``h``, as the reload
  needs to happen on the worker.

  A solution to this problem is to redefine ``f`` to reload ``file.py`` before
  it calls ``h``. For example, if inside ``file.py`` you have

  .. testcode::

    def h():
        return 1

  And you define remote function ``f`` as

  .. testcode::

    @ray.remote
    def f():
        return file.h()

  You can redefine ``f`` as follows.

  .. testcode::

    @ray.remote
    def f():
        reload(file)
        return file.h()

  This forces the reload to happen on the Workers as needed. Note that in
  Python 3, you need to do ``from importlib import reload``.

This document discusses some common problems that people run into when using Ray
as well as some known problems. If you encounter other problems, `let us know`_.

.. _`let us know`: https://github.com/ray-project/ray/issues
