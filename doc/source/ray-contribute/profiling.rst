.. _ray-core-internal-profiling:

Ray 开发人员的分析
============================

本指南帮助 Ray 项目的贡献者分析 Ray 的性能。

获取 Ray C++ 进程的堆栈跟踪
------------------------------------------

您可以使用以下 GDB 命令查看任何
正在运行的 Ray 进程「例如 raylet」的当前堆栈跟踪。
这对于调试 100% CPU 利用率或无限循环非常
有用「只需运行该命令几次即可查看进程卡在了哪里」。

.. code-block:: shell

 sudo gdb -batch -ex "thread apply all bt" -p <pid>

请注意，您可以使用 ``pgrep raylet`` 找到 raylet 的 pid 。

安装
------------

这些说明仅适用于 Ubuntu。 
``pprof`` 在 Mac OS 上正确符号化的尝试失败。

.. code-block:: bash

  sudo apt-get install google-perftools libgoogle-perftools-dev

启动 to-profile 二进制文件
-------------------------------

如果您想以分析模式启动 Ray，请定义以下变量：

.. code-block:: bash

  export PERFTOOLS_PATH=/usr/lib/x86_64-linux-gnu/libprofiler.so
  export PERFTOOLS_LOGFILE=/tmp/pprof.out


``/tmp/pprof.out`` 将保持空状态，
直到您让二进制文件运行目标工作负载一段时间，
然后通过 ``ray stop``  ``kill`` 掉它，或者让 driver 使其退出。

内存分析
----------------
如果要在 Ray 核心组件上运行内存分析，可以使用 Jemalloc 「https://github.com/jemalloc/jemalloc」。
Ray 支持环境变量来覆盖核心组件上的 LD_PRELOAD。

您可以从 `ray_constants.py` 中找到组件名称。例如，如果您要分析 gcs_server，
请在 `ray_constants.py` 搜索 `PROCESS_TYPE_GCS_SERVER`。你可以看到 `gcs_server` 的值。

用户应该提供 3 个环境变量来进行内存分析。

- RAY_JEMALLOC_LIB_PATH: jemalloc共享库 `.so` 的路径。
- RAY_JEMALLOC_CONF: jemalloc 的 MALLOC_CONF「以逗号分隔」。
- RAY_JEMALLOC_PROFILE: 以逗号分隔的 Ray 组件，用于运行 Jemalloc `.so`。例如「“raylet,gcs_server”」。请注意，组件应与 `ray_constants.py` 中的进程类型匹配。「这意味着“RAYLET,GCS_SERVER”不起作用」。

.. code-block:: bash

  # 安装 jemalloc
  wget https://github.com/jemalloc/jemalloc/releases/download/5.2.1/jemalloc-5.2.1.tar.bz2 
  tar -xf jemalloc-5.2.1.tar.bz2 
  cd jemalloc-5.2.1 
  ./configure --enable-prof --enable-prof-libunwind 
  make

  # set jemalloc configs through MALLOC_CONF env variable
  # read http://jemalloc.net/jemalloc.3.html#opt.lg_prof_interval
  # for all jemalloc configs
  # Ray start will profile the GCS server component.
  RAY_JEMALLOC_CONF=prof:true,lg_prof_interval:33,lg_prof_sample:17,prof_final:true,prof_leak:true \
  RAY_JEMALLOC_LIB_PATH=~/jemalloc-5.2.1/lib/libjemalloc.so \
  RAY_JEMALLOC_PROFILE=gcs_server \
  ray start --head

  # You should be able to see the following logs.
  2021-10-20 19:45:08,175	INFO services.py:622 -- Jemalloc profiling will be used for gcs_server. env vars: {'LD_PRELOAD': '/Users/sangbincho/jemalloc-5.2.1/lib/libjemalloc.so', 'MALLOC_CONF': 'prof:true,lg_prof_interval:33,lg_prof_sample:17,prof_final:true,prof_leak:true'}

配置可视化 CPU
---------------------------

``pprof`` 的输出可以通过多种方式进行可视化。在这里，我们将其输出为
可缩放的 ``.svg`` 图像，显​​示带有热路径注释的调用图。

.. code-block:: bash

  # Use the appropriate path.
  RAYLET=ray/python/ray/core/src/ray/raylet/raylet

  google-pprof -svg $RAYLET /tmp/pprof.out > /tmp/pprof.svg
  # Then open the .svg file with Chrome.

  # If you realize the call graph is too large, use -focus=<some function> to zoom
  # into subtrees.
  google-pprof -focus=epoll_wait -svg $RAYLET /tmp/pprof.out > /tmp/pprof.svg

以下是取自官方文档的示例 svg 输出的快照：

.. image:: http://goog-perftools.sourceforge.net/doc/pprof-test-big.gif

运行微基准测试
-----------------------

要运行一组单节点 Ray 微基准测试，请使用：

.. code-block:: bash

  ray microbenchmark

您可以在 `GitHub 发布日志中 <https://github.com/ray-project/ray/tree/master/release/release_logs>`__ 找到 Ray 版本的微基准测试结果。

参考
----------

- `pprof 文档 <http://goog-perftools.sourceforge.net/doc/cpu_profiler.html>`_.
- `pprof 的 Go 版本 <https://github.com/google/pprof>`_.
- `gperftools <https://github.com/gperftools/gperftools>`_ ，包括 libprofiler、tcmalloc 和其他好东西。
