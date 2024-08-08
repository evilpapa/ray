.. _ref-usage-stats:

使用统计收集
======================

从 Ray 1.13 开始，Ray 默认收集使用统计数据（由选择退出提示保护）。
开源 Ray 工程团队将使用这些数据来更好地了解如何改进我们的库和核心 API，以及如何确定错误修复和增强功能的优先级。

以下是我们收集政策的指导原则：

- **不会有意外** — 我们开始收集数据之前会通知您。如果收集的数据或数据使用方式有任何变化，您都会收到通知。
- **轻松选择退出:** 您可以轻松选择退出数据收集
- **透明度** — 您将能够查看发送给我们的所有数据
- **控制** — 您将控制您的数据，并且我们将尊重您删除数据的请求。
- 我们 **不会** 收集任何个人身份信息或专有代码/数据
- 我们 **不会** 出售或购买您的数据。

您将始终能够 :ref:`禁用使用情况统计信息收集 <usage-disable>`。

有关更多背景信息，请参阅此 `RFC <https://github.com/ray-project/ray/issues/20857>`_ 。

收集哪些数据？
-----------------------

我们收集非敏感数据，以帮助我们了解 Ray 的使用方式（例如，使用了哪些 Ray 库）。
**个人身份数据绝不会收集。** 请查看 UsageStatsToReport 类以查看我们收集的数据。

.. _usage-disable:

如何禁用
-----------------
在启动集群之前，有多种方法可以禁用使用情况统计信息收集：

#. Ad向启动 Ray 集群的命令添加 ``--disable-usage-stats`` 选项（例如 ``ray start --head --disable-usage-stats`` :ref:`命令 <ray-start-doc>`）。

#. 运行 :ref:`ray disable-usage-stats <ray-disable-usage-stats-doc>` 以禁用所有未来集群的收集。这不会影响当前正在运行的集群。在后台，此命令会将 ``{"usage_stats": true}`` 写入全局配置文件 ``~/.ray/config.json`` 。

#. 设置环境变量 ``RAY_USAGE_STATS_ENABLED`` 为 0 （例如， ``RAY_USAGE_STATS_ENABLED=0 ray start --head`` :ref:`命令 <ray-start-doc>`）。

#. 如果你在使用 `KubeRay <https://github.com/ray-project/kuberay/>`_，你可以添加 ``disable-usage-stats: 'true'`` 到 ``.spec.[headGroupSpec|workerGroupSpecs].rayStartParams.``。

目前无法启用或禁用正在运行的集群的收集；您必须停止并重新启动集群。


它是如何工作的？
-----------------

当通过 :ref:`ray start --head <ray-start-doc>`、 :ref:`ray up <ray-up-doc>`、 :ref:`ray submit --start <ray-submit-doc>` 或 :ref:`ray exec --start <ray-exec-doc>` 启动 Ray 集群，
Ray 将根据以下顺序考虑因素来决定是否启用使用情况统计收集：

#. 它检查环境变量 ``RAY_USAGE_STATS_ENABLED`` 是否设置： 1 表示启用，0 表示禁用。

#. 如果未设置环境变量， 它将读取全局配置文件 ``~/.ray/config.json`` 中 ``usage_stats`` 键的值：true 表示启用，false 表示禁用。

#. 如果两者都未设置，且控制台是交互式的，则系统将提示用户启用或禁用收集。 如果控制台是非交互式的，则默认情况下将启用使用情况统计信息收集。 决策将保存到 ``~/.ray/config.json``，因此提示仅显示一次。

注意：使用通过 ``ray.init()`` 启动的本地开发集群时，不会启用使用情况统计信息收集，除非他是一个夜间版的 wheel。这意味着 Ray 不会从未直接使用 Ray 的第三方库用户那里收集数据。

如果启用了使用情况统计信息收集，则头节点上的后台进程将收集使用情况统计信息并
在每个小时将内容报告给 ``https://usage-stats.ray.io/``。 报告的使用情况统计信息也将保存到头节点的
``/tmp/ray/session_xxx/usage_stats.json`` 文件中以供检查。 您可以检查此文件是否存在以查看是否启用了收集功能。

使用情况统计信息收集非常轻量，不会以任何方式影响您的工作量。

请求删除收集的数据
------------------------------------

要请求删除收集的数据，请发送电子邮件至 ``usage_stats@ray.io`` 并附带上 ``session_id`` ，您可以在 ``/tmp/ray/session_xxx/usage_stats.json`` 中找到。

常见问题 (FAQ)
--------------------------------

**session_id 是否映射到个人数据？**

不，uuid 将是一个 Ray 会话/作业特定的随机 ID，不能用于识别特定的人或机器。它不会超出 Ray 会话的生命周期；主要用于捕获以便我们能够尊重删除请求。

session_id 被记录下来以便我们能够尊重删除请求。

**企业是否可以轻松配置额外的端点或替换不同的端点？**

我们确实看到了这种用例，并且很乐意与您交谈以使其发挥作用 -- 请给 ``usage_stats@ray.io`` 发送电子邮件。


联系我们
----------
如果您对使用情况统计收集有任何反馈，请发送电子邮件至 ``usage_stats@ray.io``。
