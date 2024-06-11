Ray 开发者调试
============================

本调试指引是专为 Ray 项目的贡献者准备的。

开始进程调试
--------------------------------
当进程崩溃时，通常有必要在调试器中启动它们。
Ray 目前允许在以下调试器中启动进程：

- valgrind
- valgrind 分析器
- perftools 分析器
- gdb
- tmux

要使用以上工具，请确保您的机器上已经安装了这些
工具（已知 MacOS 上的 gdb 和 valgrind 存在问题）。
之后，您可以通过添加以下环境
变量 ``RAY_{PROCESS_NAME}_{DEBUGGER}=1`` 启动 ray 进程：
例如，如果你想在 ``valgrind`` 中启动 raylet，
你只需要设置环境变量 ``RAY_RAYLET_VALGRIND=1``。

要在 ``gdb`` 中启动进程，进程也必须在 ``tmux`` 中启动。
所以你想在 ``gdb`` 中启动 raylet，你需要
在你的 Python 脚本中添加以下内容：

.. code-block:: bash

 RAY_RAYLET_GDB=1 RAY_RAYLET_TMUX=1 python

你可以使用 ``tmux ls`` 列出 ``tmux`` 会话，然后附加到适当的会话。

You can also get a core dump of the ``raylet`` process, which is especially
useful when filing `issues`_. The process to obtain a core dump is OS-specific,
but usually involves running ``ulimit -c unlimited`` before starting Ray to
allow core dump files to be written. 

.. _backend-logging:

后端日志
---------------
The ``raylet`` process logs detailed information about events like task
execution and object transfers between nodes. To set the logging level at
runtime, you can set the ``RAY_BACKEND_LOG_LEVEL`` environment variable before
starting Ray. For example, you can do:

.. code-block:: shell

 export RAY_BACKEND_LOG_LEVEL=debug
 ray start

This will print any ``RAY_LOG(DEBUG)`` lines in the source code to the
``raylet.err`` file, which you can find in :ref:`temp-dir-log-files`.
If it worked, you should see as the first line in ``raylet.err``:

.. code-block:: shell

  logging.cc:270: Set ray log level from environment variable RAY_BACKEND_LOG_LEVEL to -1

(-1 is defined as RayLogLevel::DEBUG in logging.h.)

.. literalinclude:: /../../src/ray/util/logging.h
  :language: C
  :lines: 52,54

Backend event stats
-------------------
The ``raylet`` process also periodically dumps event stats to the ``debug_state.txt`` log
file if the ``RAY_event_stats=1`` environment variable is set. To also enable regular
printing of the stats to log files, you can additional set ``RAY_event_stats_print_interval_ms=1000``.

Event stats include ASIO event handlers, periodic timers, and RPC handlers. Here is a sample
of what the event stats look like:

.. code-block:: shell

  Event stats:
  Global stats: 739128 total (27 active)
  Queueing time: mean = 47.402 ms, max = 1372.219 s, min = -0.000 s, total = 35035.892 s
  Execution time:  mean = 36.943 us, total = 27.306 s
  Handler stats:
    ClientConnection.async_read.ReadBufferAsync - 241173 total (19 active), CPU time: mean = 9.999 us, total = 2.411 s
    ObjectManager.ObjectAdded - 61215 total (0 active), CPU time: mean = 43.953 us, total = 2.691 s
    CoreWorkerService.grpc_client.AddObjectLocationOwner - 61204 total (0 active), CPU time: mean = 3.860 us, total = 236.231 ms
    CoreWorkerService.grpc_client.GetObjectLocationsOwner - 51333 total (0 active), CPU time: mean = 25.166 us, total = 1.292 s
    ObjectManager.ObjectDeleted - 43188 total (0 active), CPU time: mean = 26.017 us, total = 1.124 s
    CoreWorkerService.grpc_client.RemoveObjectLocationOwner - 43177 total (0 active), CPU time: mean = 2.368 us, total = 102.252 ms
    NodeManagerService.grpc_server.PinObjectIDs - 40000 total (0 active), CPU time: mean = 194.860 us, total = 7.794 s

Callback latency injection
--------------------------
Sometimes, bugs are caused by RPC issues, for example, due to the delay of some requests, the system goes to a deadlock.
To debug and reproduce this kind of issue, we need to have a way to inject latency for the RPC request. To enable this,
``RAY_testing_asio_delay_us`` is introduced. If you'd like to make the callback of some RPC requests be executed after some time,
you can do it with this variable. For example:

.. code-block:: shell

  RAY_testing_asio_delay_us="NodeManagerService.grpc_client.PrepareBundleResources=2000000:2000000" ray start --head


The syntax for this is ``RAY_testing_asio_delay_us="method1=min_us:max_us,method2=min_us:max_us"``. Entries are comma separated.
There is a special method ``*`` which means all methods. It has a lower priority compared with other entries.

.. _`issues`: https://github.com/ray-project/ray/issues
