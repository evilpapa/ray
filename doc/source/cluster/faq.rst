.. _cluster-FAQ:

===
常问问题
===

这些是我们在使用 Ray 集群时遇到的一些常见问题。
如果您在阅读此常见问题解答后仍有疑问，请联系
`我们的 Discourse <https://discuss.ray.io/>`__！

Ray 集群是否支持多租户？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

是的，您可以在 Ray 集群中同时运行来自不同用户的多个 :ref:`jobs <jobs-overview>` ，
但不建议在生产中这样做。
原因是 Ray 目前仍然缺少生产中多租户的一些功能：

* Ray 不提供强大的资源隔离：
  Ray :ref:`资源 <core-resources>` 是合乎逻辑的，它们不会限制任务或 actor 在运行时可以使用的物理资源。
  这意味着同时进行的作业可能会相互干扰，从而降低它们在生产环境中运行的可靠性。

* Ray 不支持优先级：所有作业、任务和 actor 都有相同的优先级，因此无法在负载下对重要作业进行优先排序。

* Ray 不支持访问控制：job 对 Ray 集群及其内的所有资源具有完全访问权。

另一方面，您可以使用同一个集群多次运行同一个作业，以节省集群启动时间。

.. note::
    Ray :ref:`命名空间 <namespaces-guide>` 是作业和命名 actor 的逻辑分组。与 Kubernetes 命名空间不同，它不提供任何其他多租户功能，例如资源配额。


我有多个 Ray 用户。为他们部署 Ray 的正确方法是什么？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

建议为每个用户启动一个 Ray 集群，以便隔离他们的工作负载。

``--node-ip-address`` 和 ``--address`` 之间有什么区别？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在具有多个网络地址的计算机上启动头节点时，可能需要指定外部可用的地址，
以便工作节点可以连接。
这是通过以下方式完成的：

.. code:: bash

    ray start --head --node-ip-address xx.xx.xx.xx --port nnnn``

然后在启动工作节点时，使用此命令连接到头节点：

.. code:: bash

    ray start --address xx.xx.xx.xx:nnnn

工作节点连接失败是什么样的？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

如果工作节点无法连接到头节点，您应该会看到此错误

    Unable to connect to GCS at xx.xx.xx.xx:nnnn. Check that (1) Ray GCS with
    matching version started successfully at the specified address, and (2)
    there is no firewall setting preventing access.

最可能的原因是工作节点无法访问给定的 IP 地址。您可以在
工作节点上使用 ``ip route get xx.xx.xx.xx`` 以开始
调试路由问题。

您可能还会在日志中看到类似的失败信息

    This node has an IP address of xx.xx.xx.xx, while we can not found the
    matched Raylet address. This maybe come from when you connect the Ray
    cluster with a different IP address or connect a container.

这可能是由于过多同时连接导致头节点过载所致。
解决方案是更慢地启动工作节点。

我在运行 SLURM 集群时遇到了问题
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 SLURM 集群上，似乎存在一类问题。
虽然我们无法确定确切原因（截至 2023 年 6 月），
但已采取措施缓解部分资源争用问题。
报告的一些问题如下：

* 使用具有大量 CPU 的机器，并为每个 CPU 启动一个工作器以及 OpenBLAS（如 NumPy 中使用的）
  可能会分配过多的线程。 
  这是 `已知的 OpenBLAS 限制`_ ，可以通过将 OpenBLAS 限制为
  每个进程一个线程来缓解，如链接中所述。

* 资源分配不符合预期：通常每个节点分配了过多的 CPU。
  最佳做法是在不启动 ray 的情况下验证您的 SLURM 配置，
  以验证分配是否符合预期。
  有关更多详细信息，请参阅 :ref:`ray-slurm-deploy`。

.. _`已知的 OpenBLAS 限制`: https://github.com/xianyi/OpenBLAS/wiki/faq#how-can-i-use-openblas-in-multi-threaded-applications  
