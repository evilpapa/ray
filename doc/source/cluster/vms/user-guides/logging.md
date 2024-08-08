(vm-logging)=
# 日志持久化

日志对于排除 Ray 应用程序和集群故障非常有用。例如，如果节点意外终止，您可能希望访问系统日志。

Ray 不提供日志数据的原生存储解决方案。用户需要自行管理日志的生命周期。以下部分提供了有关如何从运行在虚拟机上的 Ray 集群收集日志的说明。

## Ray 日志目录
默认情况下，Ray 将日志写入每个 Ray 节点文件系统上的 `/tmp/ray/session_*/logs` 目录中的文件中，包括应用程序日志和系统日志。 在开始收集日志之前，详细了解 {ref}`日志目录和日志文件 <logging-directory>` and the {ref}`日志轮换配置 <log-rotation>` 。


## Log processing tools

有许多开源日志处理工具可用，例如 [Vector][Vector]、 [FluentBit][FluentBit]、 [Fluentd][Fluentd]、 [Filebeat][Filebeat] 及 [Promtail][Promtail]。

[Vector]: https://vector.dev/
[FluentBit]: https://docs.fluentbit.io/manual
[Filebeat]: https://www.elastic.co/guide/en/beats/filebeat/7.17/index.html
[Fluentd]: https://docs.fluentd.org/
[Promtail]: https://grafana.com/docs/loki/latest/clients/promtail/

## 日志收集

根据您的需求选择日志处理工具后，您可能需要执行以下步骤：

1. 将 Ray Cluster 中每个节点上的日志文件作为源进行提取。
2. 解析并转换日志。您可能希望使用 {ref}`Ray 结构化日志 <structured-logging>` 来简化此步骤。
3. 将转换后的日志运送至日志存储或管理系统。
