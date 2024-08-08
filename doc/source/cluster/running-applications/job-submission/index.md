(jobs-overview)=

# Ray Job 概述

一旦部署了 Ray 集群（在 [VMs](vm-cluster-quick-start) 或 [Kubernetes](kuberay-quickstart)），您就可以运行 Ray 应用程序了！
![A diagram that shows three ways of running a job on a Ray cluster.](../../images/ray-job-diagram.svg "Three ways of running a job on a Ray cluster.")

## Ray Jobs API

在 Ray 集群上运行作业的推荐方法是使用 *Ray Jobs API*，它由 CLI 工具、Python SDK 和 REST API 组成。

Ray Jobs API 允许您将本地开发的应用程序提交到远程 Ray 集群执行。
它简化了打包、部署和管理 Ray 应用程序的体验。

Ray Jobs API 的提交包括：

1. 入口点命令，例如 `python my_script.py`，以及
2. 一个 [运行时环境](runtime-environments)，指定应用程序的文件和包依赖项。

作业可以由 Ray Cluster 之外的远程客户端提交。
我们将在以下用户指南中展示此工作流程。

作业提交后，无论原始提交者的连通性如何，它都会运行一次，直到完成或失败。
重试或使用不同参数的不同运行应由提交者处理。
作业与 Ray 集群的生命周期绑定，因此如果集群发生故障，该集群上所有正在运行的作业都将终止。

要开始使用 Ray Jobs API，请查看 [快速入门](jobs-quickstart) 指南，其中将引导您了解用于提交 Ray Job 和与 Ray Job 交互的 CLI 工具。
这适用于任何可以通过 HTTP 与 Ray Cluster 通信的客户端。
如果需要，Ray Jobs API 还提供用于 [程序化 job 提交](ray-job-sdk) 及 [使用 REST 接口提交 job](ray-job-rest-api)。

## 以交互方式运行 Job

如果您想以 *交互方式* 运行应用程序并实时查看输出（例如，在开发或调试期间），您可以：

- （推荐） 直接在集群节点上运行脚本（例如，使用 [`ray attach`](ray-attach-doc) SSH 进入节点后），或者
- （仅限专家）使用 [Ray Client](ray-client-ref) 从本地机器运行脚本，同时保持与集群的连接。

请注意，以这些方式启动的作业不受 Ray Jobs API 管理，因此 Ray Jobs API 将无法看到它们或与它们交互 （ `ray job list` 和 `JobSubmissionClient.list_jobs()` 除外）。

## 内容

```{toctree}
:maxdepth: '1'

quickstart
sdk
jobs-package-ref
cli
rest
ray-client
```
