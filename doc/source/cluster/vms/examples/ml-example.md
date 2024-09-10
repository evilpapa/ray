(clusters-vm-ml-example)=

# 虚拟机上的 Ray Train XGBoostTrainer

:::{note}
要了解虚拟机上 Ray 的基础知识，我们建议先查看
{ref}`入门指南 <vm-cluster-quick-start>` 。
:::


在本指南中，我们将向您展示如何在 AWS 上运行示例 Ray 机器学习
工作负载。类似的步骤也可用于在 GCP 或 Azure 上部署。

我们将使用 100 GB 的训练集运行 Ray 的 {ref}`XGBoost 基准训练 <xgboost-benchmark>` 。
要了解有关使用 Ray 的 XGBoostTrainer 的更多信息，请查看 {ref}`the XGBoostTrainer 文档 <train-gbdt-guide>`。

## VM 集群设置

对于本指南中的工作负载，建议使用以下设置：
- 总计 10 节点
- 每个节点容量为 16 个 CPU 和 64 Gi 内存。对于主要的云提供商，合适的实例类型包括
    * m5.4xlarge 「亚马逊网络服务」
    * Standard_D5_v2 「Azure」
    * e2-standard-16 「谷歌云」
- 每个节点应配置1000 GB的磁盘空间「用于存储训练集」。

对应集群配置文件如下：

```{literalinclude} ../configs/xgboost-benchmark.yaml
:language: yaml
```

```{admonition} 可选：设置自动缩放集群
**如果您想尝试在启用自动缩放的情况下运行工作负载**，
请将 ``min_workers`` 工作节点数设置为 0 。
提交工作负载后，9 个工作节点
将扩展以适应工作负载。工作负载完成后，这些节点将缩减。
```

## 部署 Ray 集群

现在我们准备使用上面定义的配置部署 Ray 集群。
在运行命令之前，请确保您的 aws 凭据配置正确。

```shell
ray up -y cluster.yaml
```

将创建一个 Ray 头节点和 9 个 Ray 工作节点。

## 运行工作负载

我们使用 {ref}`Ray Job Submission <jobs-overview>` 来启动工作负载。

### 连接到集群

首先，我们连接到作业服务器。在单独的 shell 中运行
以下阻塞命令。
```shell
ray dashboard cluster.yaml
```
这会将远程端口 8265 转发到本地主机的端口 8265。

### 提交工作负载

我们将使用 {ref}`Ray Job Python SDK <ray-job-sdk>` 提交 XGBoost 工作负载。

```{literalinclude} /cluster/doc_code/xgboost_submit.py
:language: python
```

要提交工作负载，请运行上述 Python 脚本。
该脚本可 [Ray 存储库][XGBSubmit] 中找到。

```shell
# Download the above script.
curl https://raw.githubusercontent.com/ray-project/ray/releases/2.0.0/doc/source/cluster/doc_code/xgboost_submit.py -o xgboost_submit.py
# Run the script.
python xgboost_submit.py
```

### 观察进度

基准测试可能需要长达 30 分钟才能运行。
使用以下工具观察其进度。

#### Job 日志

要跟踪作业的日志，请使用上述提交脚本打印的命令。
```shell
# Subsitute the Ray Job's submission id.
ray job logs 'raysubmit_xxxxxxxxxxxxxxxx' --address="http://localhost:8265" --follow
```

#### Ray Dashboard

浏览器访问 `localhost:8265` 查看 Ray 仪表盘。

#### Ray 状态

使用以下工具观察自动缩放状态和 Ray 资源使用情况
```shell
ray exec cluster.yaml 'ray status'
```

### Job 完成

#### 基准测试结果

基准测试完成后，作业日志将显示结果：

```
Results: {'training_time': 1338.488839321999, 'prediction_time': 403.36653568099973}
```

基准测试的性能对底层云基础设施很敏感——
您可能无法匹配 {ref}`基准测试文档中引用的数字 <xgboost-benchmark>`.

#### 模型参数
Ray 头节点中的文件 `model.json` 包含训练模型的参数。
其他结果数据将在头节点的 `ray_results` 目录提供。
参考 {ref}`XGBoostTrainer 文档 <train-gbdt-guide>` 获取详细信息。

```{admonition} Scale-down
如果启用了自动缩放，Ray 工作节点将在指定的空闲超时后缩小规模。
```

#### 清理
使用以下命令删除您的 Ray 集群：
```shell
ray down -y cluster.yaml
```

[XGBSubmit]: https://github.com/ray-project/ray/blob/releases/2.0.0/doc/source/cluster/doc_code/xgboost_submit.py
