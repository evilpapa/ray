.. _ray-tracing:

追踪
=======
为了帮助调试和监控 Ray 应用程序，Ray 与 OpenTelemetry 集成，以便于将跟踪导出到 Jaeger 等外部跟踪堆栈。


.. note::

    跟踪是一项实验性功能，正在积极开发中。 API 可能会发生变化。

安装
------------
首先，安装 OpenTelemetry：

.. code-block:: shell

    pip install opentelemetry-api==1.1.0
    pip install opentelemetry-sdk==1.1.0
    pip install opentelemetry-exporter-otlp==1.1.0

启动追踪钩子
--------------------
要启用跟踪，您必须提供一个跟踪启动挂钩，其中包含:ref:`Tracer Provider <tracer-provider>`\ :ref:`Remote Span Processors <remote-span-processors>` 以及 :ref:`Additional Instruments <additional-instruments>` 设置. 跟踪启动挂钩应该是一个不带 args 或 kwargs 调用的函数。该钩子需要在所有工作进程的 Python 环境中可用。

下面是一个示例跟踪启动挂钩，它设置默认跟踪提供程序，将 spans 文件导出到 ``/tmp/spans`` ，并且没有任何其他工具。

.. testcode::

  import ray
  import os
  from opentelemetry import trace
  from opentelemetry.sdk.trace import TracerProvider
  from opentelemetry.sdk.trace.export import (
      ConsoleSpanExporter,
      SimpleSpanProcessor,
  )


  def setup_tracing() -> None:
      # Creates /tmp/spans folder
      os.makedirs("/tmp/spans", exist_ok=True)
      # Sets the tracer_provider. This is only allowed once per execution
      # context and will log a warning if attempted multiple times.
      trace.set_tracer_provider(TracerProvider())
      trace.get_tracer_provider().add_span_processor(
          SimpleSpanProcessor(
              ConsoleSpanExporter(
                  out=open(f"/tmp/spans/{os.getpid()}.json", "a")
                  )
          )
      )


对于想要尝试跟踪的开源用户，Ray 有一个默认的跟踪启动挂钩，可将 span 导出到文件夹/ ``/tmp/spans``。要使用此默认挂钩运行，请运行以下代码示例来设置跟踪并跟踪简单的 Ray 任务。

.. tab-set::

    .. tab-item:: ray start

        .. code-block:: shell

            $ ray start --head --tracing-startup-hook=ray.util.tracing.setup_local_tmp_tracing:setup_tracing
            $ python
                ray.init()
                @ray.remote
                def my_function():
                    return 1

                obj_ref = my_function.remote()

    .. tab-item:: ray.init()

        .. testcode::

            ray.init(_tracing_startup_hook="ray.util.tracing.setup_local_tmp_tracing:setup_tracing")

            @ray.remote
            def my_function():
                return 1

            obj_ref = my_function.remote()

如果您想提供自己的自定义跟踪启动挂钩，请在要运行的 ``setup_tracing`` 函数的 ``module:attribute`` 提供你的设置。

.. _tracer-provider:

Tracer 提供者
~~~~~~~~~~~~~~~
这配置了如何收集跟踪。参考 TracerProvider API `here <https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.html#opentelemetry.sdk.trace.TracerProvider>`__。

.. _remote-span-processors:

Remote span processors
~~~~~~~~~~~~~~~~~~~~~~
这配置了将跟踪导出到的位置。参考 `此处的 <https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.html#opentelemetry.sdk.trace.SpanProcessor>`__  SpanProcessor API。

Users who want to experiment with tracing can configure their remote span processors to export spans to a local JSON file. Serious users developing locally can push their traces to Jaeger containers via the `Jaeger exporter <https://opentelemetry-python.readthedocs.io/en/latest/exporter/jaeger/jaeger.html#module-opentelemetry.exporter.jaeger>`_.

.. _additional-instruments:

Additional instruments
~~~~~~~~~~~~~~~~~~~~~~
If you are using a library that has built-in tracing support, the ``setup_tracing`` function you provide should also patch those libraries. You can find more documentation for the instrumentation of these libraries `here <https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation>`_.

Custom traces
*************
Add custom tracing in your programs. Within your program, get the tracer object with ``trace.get_tracer(__name__)`` and start a new span with ``tracer.start_as_current_span(...)``.

See below for a simple example of adding custom tracing.

.. testcode::

  from opentelemetry import trace

  @ray.remote
  def my_func():
      tracer = trace.get_tracer(__name__)

      with tracer.start_as_current_span("foo"):
          print("Hello world from OpenTelemetry Python!")
