(collect-metrics)=
# 指标收集和监控
指标对于监控和排除 Ray 应用程序和集群故障非常有用。例如，如果节点意外终止，您可能想要访问该节点的指标。

Ray 使用 [Prometheus 格式](https://prometheus.io/docs/instrumenting/exposition_formats/) 记录和发出时间序列指标。Ray 不提供指标的原生存储解决方案。用户需要自行管理指标的生命周期。本页面提供了有关如何从 Ray 集群收集和监控指标的说明。


## 系统和应用程序指标
如果您使用 `ray[default]` 或 {ref}`其他安装命令 <installation>` 包含了仪表盘组件，Ray 会导出指标。表板代理进程负责汇总指标并将其报告给端点，以供 Prometheus 抓取。

**系统指标**: Ray 导出许多系统指标。 查看 {ref}`系统指标 <system-metrics>` 以获取有关所发出指标的更多详细信息。

**应用程序指标**: 特定于应用程序的指标对于监控应用程序状态非常有用。 查看 {ref}`添加应用指标 <application-level-metrics>` 以了解如何记录指标。

(prometheus-setup)=
## 设置 Prometheus server
使用 Prometheus 从 Ray 集群中抓取指标。Ray 不会为用户启动 Prometheus 服务器。用户需要决定托管位置并进行配置以从集群中抓取指标。

```{admonition} Tip
:class: tip
以下说明介绍了在本地机器上设置 Prometheus 的一种方法。查看 [Prometheus 文档](https://prometheus.io/docs/introduction/overview/) ，了解设置 Prometheus 服务器的最佳策略。

对于 KubeRay 用户，请按照 [以下说明](kuberay-prometheus-grafana) 设置 Prometheus。
```

首先， [下载 Prometheus](https://prometheus.io/download/)。确保下载适合您操作系统的正确二进制文件。（例如，适用于 macOS X 的 Darwin。）

然后，使用以下命令将档案解压到本地目录中：

```bash
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```

Ray 提供了开箱即用的 Prometheus 配置。运行 Ray 后，您可以在 `/tmp/ray/session_latest/metrics/prometheus/prometheus.yml` 找到该配置。

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
# Scrape from each Ray node as defined in the service_discovery.json provided by Ray.
- job_name: 'ray'
  file_sd_configs:
  - files:
    - '/tmp/ray/prom_metrics_service_discovery.json'
```

接下来启动 Prometheus：

```shell
./prometheus --config.file=/tmp/ray/session_latest/metrics/prometheus/prometheus.yml
```
```{admonition} Note
:class: note
如果您使用的是 macOS，此时您可能会收到有关尝试启动开发人员尚未验证的应用程序的错误。请参阅下面的“故障排除”指南以修复此问题。
```

现在，您可以从默认的 Prometheus URL `http://localhost:9090` 访问 Ray 指标。


### Troubles故障排除hooting
#### 在 macOS X 上通过 Homebrew 在 Prometheus 中使用 Ray 配置
Homebrew 将 Prometheus 安装为自动启动的服务。
要配置这些服务，您不能简单地将配置文件作为命令行参数传入。

相反，将 --config-file 行修改为 `/usr/local/etc/prometheus.args` 来读取 `--config.file /tmp/ray/session_latest/metrics/prometheus/prometheus.yml`。

然后您可以使用 `brew services start prometheus` 启动或重启服务。


#### macOS 不信任开发人员安装 Prometheus
您可能会收到以下错误：

![trust error](https://raw.githubusercontent.com/ray-project/Images/master/docs/troubleshooting/prometheus-trusted-developer.png)

从互联网下载二进制文件时，macOS 要求二进制文件由受信任的开发人员 ID 签名。
许多开发人员不在 macOS 的受信任列表中。用户可以手动覆盖此要求。

请参阅 [这些说明](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac) 以了解如何覆盖限制并安装或运行应用程序。

#### 使用 Docker Compose 加载 Ray Prometheus 配置
在 Ray 容器中，软链 "/tmp/ray/session_latest/metrics" 指向最新的活跃 Ray 会话。但是，Docker 不支持在共享卷上挂载符号链接，并且您可能无法加载 Prometheus 配置文件。

要解决此问题，请使用自动化 shell 脚本将 Prometheus 配置从 Ray 容器无缝传输到共享卷。为确保正确设置，请将共享卷挂载到容器的相应路径上，其中包含启动 Prometheus 服务器的推荐配置。

(scrape-metrics)=
## 抓取指标
Ray 在每个节点上运行一个指标代理来导出系统和应用程序指标。每个指标代理从本地节点
收集指标并以 Prometheus 格式公开它们。然后，您可以抓取每个端点以访问指标。

为了抓取端点，我们需要确保服务发现，这允许 Prometheus 在每个节点上找到指标代理的端点。

### 自动发现指标端点。

您可以允许 Prometheus 使用 Prometheus 的 [基于文件的服务发现](https://prometheus.io/docs/guides/file-sd/#installing-configuring-and-running-prometheus) 功能动态查找要抓取的端点。
使用 Ray {ref}`cluster launcher <vm-cluster-quick-start>`时，请使用自动发现功能导出 Prometheus 指标，因为节点 IP 地址通常会随着集群的扩大和缩小而发生变化。

Ray 在头节点上自动生成 Prometheus [服务发现文件](https://prometheus.io/docs/guides/file-sd/#installing-configuring-and-running-prometheus) ，以方便指标代理的服务发现。 此功能允许您抓取集群中的所有指标，而无需知道它们的 IP。以下信息将指导您进行设置。

服务发现文件在 {ref}`头节点 <cluster-head-node>`。 在此节点上，查找 ``/tmp/ray/prom_metrics_service_discovery.json`` （或如果使用自定义 Ray ``temp_dir``，则查找等效文件）。 Ray 会定期使用集群中所有指标代理的地址更新此文件。

Ray 会自动生成一个 Prometheus 配置，它会抓取在 `/tmp/ray/session_latest/metrics/prometheus/prometheus.yml`处找到的文件以进行服务发现。 您可以选择使用此配置或修改自己的配置以启用此行为。 请参阅下面的配置详细。完整的文档可以在 [这里](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) 找到。

通过此配置，Prometheus 会根据 Ray 的服务发现文件的内容自动更新其抓取的地址。

```yaml
# Prometheus config file

# my global config
global:
  scrape_interval:     2s
  evaluation_interval: 2s

# Scrape from Ray.
scrape_configs:
- job_name: 'ray'
  file_sd_configs:
  - files:
    - '/tmp/ray/prom_metrics_service_discovery.json'
```

### 手动发现指标端点

如果您知道 Ray 集群中节点的 IP 地址，则可以将 Prometheus 配置为从静态端点列表中读取指标。
设置 Ray 应该用来导出指标的固定端口。如果您使用的是 VM Cluster Launcher，请传递 ``--metrics-export-port=<port>`` 给 ``ray start``。 如果您使用的是 KubeRay，请在 RayCluster 配置文件中指定 ``rayStartParams.metrics-export-port``。 您必须在集群中的所有节点上指定端口。

如果您不知道 Ray Cluster 中节点的 IP 地址，也可以通过读取 Ray Cluster 信息以编程方式发现端点。 以下示例使用 Python 脚本和 {py:obj}`ray.nodes` API 通过结合 ``NodeManagerAddress`` 和 ``MetricsExportPort`` 来查找指标代理的 URL。

```python
# On a cluster node:
import ray
ray.init()
from pprint import pprint
pprint(ray.nodes())

"""
Pass the <NodeManagerAddress>:<MetricsExportPort> from each of these entries
to Prometheus.
[{'Alive': True,
  'MetricsExportPort': 8080,
  'NodeID': '2f480984702a22556b90566bdac818a4a771e69a',
  'NodeManagerAddress': '192.168.1.82',
  'NodeManagerHostname': 'host2.attlocal.net',
  'NodeManagerPort': 61760,
  'ObjectManagerPort': 61454,
  'ObjectStoreSocketName': '/tmp/ray/session_2020-08-04_18-18-16_481195_34255/sockets/plasma_store',
  'RayletSocketName': '/tmp/ray/session_2020-08-04_18-18-16_481195_34255/sockets/raylet',
  'Resources': {'CPU': 1.0,
                'memory': 123.0,
                'node:192.168.1.82': 1.0,
                'object_store_memory': 2.0},
  'alive': True},
{'Alive': True,
  'MetricsExportPort': 8080,
  'NodeID': 'ce6f30a7e2ef58c8a6893b3df171bcd464b33c77',
  'NodeManagerAddress': '192.168.1.82',
  'NodeManagerHostname': 'host1.attlocal.net',
  'NodeManagerPort': 62052,
  'ObjectManagerPort': 61468,
  'ObjectStoreSocketName': '/tmp/ray/session_2020-08-04_18-18-16_481195_34255/sockets/plasma_store.1',
  'RayletSocketName': '/tmp/ray/session_2020-08-04_18-18-16_481195_34255/sockets/raylet.1',
  'Resources': {'CPU': 1.0,
                'memory': 134.0,
                'node:192.168.1.82': 1.0,
                'object_store_memory': 2.0},
  'alive': True}]
"""
```

## 处理和导出指标
如果您需要处理并将指标导出到其他存储或管理系统，请查看 [Vector][Vector] 等开源指标处理工具。

[Vector]: https://vector.dev/


## 监控指标
要可视化和监控收集到的指标，有 3 种常见途径：

1. **Simplist**: 将 Grafana 与 Ray 提供的配置一起使用，其中包括默认的 Grafana 仪表板，显示一些用于调试 Ray 应用程序的最有价值的指标。
2. **推荐**: 使用嵌入 Grafana 可视化功能的 Ray Dashboard，并在单一窗口内查看指标以及日志、作业信息等。
3. **手动**: 从头开始设置 Grafana 或其他工具，如 CloudWatch、Cloud Monitoring 和 Datadog。

以下是针对每条路径的一些说明：

(grafana)=
### Simplist: 使用 Ray 提供的配置设置 Grafana
Grafana 是一种支持 Prometheus 指标高级可视化的工具，允许您使用自己喜欢的指标创建自定义仪表板。

::::{tab-set}

:::{tab-item} 创建一个新的 Granafa 服务器

```{admonition} Note
:class: note
以下说明介绍了在 macOS 计算机上启动 Grafana 服务器的一种方法。请参阅 [Grafana 文档](https://grafana.com/docs/grafana/latest/setup-grafana/start-restart-grafana/#start-the-grafana-server) ，了解如何在不同系统中启动 Grafana 服务器。

针对 KubeRay 用户，请按照 [以下说明](kuberay-prometheus-grafana) 设置 Grafana。
```

首先， [下载 Grafana](https://grafana.com/grafana/download). 。按照下载页面上的说明下载适合您操作系统的二进制文件。

转到二进制文件的位置 `/tmp/ray/session_latest/metrics/grafana` 并使用文件夹中的内置配置运行 Granafa。

```shell
./bin/grafana-server --config /tmp/ray/session_latest/metrics/grafana/grafana.ini web
```

访问 Grafana 默认的 grafana URL `http://localhost:3000`。
转到仪表板 -> 管理 -> Ray -> 默认仪表板查看默认仪表板。将 Grafana 与 Ray Dashboard 集成后，可以在 {ref}`Ray Dashboard <observability-getting-started>` 访问相同的 {ref}`指标图表 <system-metrics>`。

```{admonition} Note
:class: note
如果这是您第一次使用 Grafana，请使用用户名 `admin` 和密码 `admin` 登录。
```


![grafana login](images/graphs.png)

**故障排查**
***在 macOS X 上通过 Homebrew 在 Grafana 中使用 Ray 配置进行故障排除***

Homebrew 将 Grafana 安装为自动启动的服务。
因此，要配置这些服务，您不能简单地将配置文件作为命令行参数传入。

相反，更新 `/usr/local/etc/grafana/grafana.ini` 文件以便它与 `/tmp/ray/session_latest/metrics/grafana/grafana.ini` 的内容相匹配。

然后您可以使用 `brew services start grafana` 和 `brew services start prometheus` 启动或重启服务。

***使用 Docker Compose 加载 Ray Grafana 配置***
在 Ray 容器中，符号链接 "/tmp/ray/session_latest/metrics" 指向最新的活动 Ray 会话。但是，Docker 不支持在共享卷上安装符号链接，因此您可能无法加载 Grafana 配置文件和默认仪表板。

要解决此问题，请使用自动化 shell 脚本将必要的 Grafana 配置和仪表板从 Ray 容器无缝传输到共享卷。为确保正确设置，请将共享卷挂载到容器的相应路径上，其中包含用于启动 Grafana 服务器的推荐配置和默认仪表板。

:::

:::{tab-item} 使用现有的 Grafana 服务器

在您的 Grafana 服务器运行后，启动 Ray 集群并在 `/tmp/ray/session_latest/metrics/grafana/dashboards` 处找到 Ray 提供的默认 Grafana 仪表板 JSON。[复制 JSON 并将 Grafana 仪表板导入](https://grafana.com/docs/grafana/latest/dashboards/manage-dashboards/#import-a-dashboard) 到您的 Granafa。

如果 Grafana 报告未找到数据源， [请添加数据源变量](https://grafana.com/docs/grafana/latest/dashboards/variables/add-template-variables/?pg=graf&plcmt=data-sources-prometheus-btn-1#add-a-data-source-variable)。数据源的名称必须与环境中 `RAY_PROMETHEUS_NAME` 的值相同。默认情况下 `RAY_PROMETHEUS_NAME` 为 `Prometheus`。
:::

::::



### 推荐：使用带有嵌入式 Grafana 可视化的 Ray Dashboard
1. 按照上述说明使用 Ray 提供的可视化功能设置 Grafana
2. 查看 {ref}`配置和管理 Ray Dashboard <embed-grafana-in-dashboard>` 以了解如何将 Grafana 可视化嵌入到 Dashboard 中
3. 查看 {ref}`Dashboard 的指标视图 <dash-metrics-view>` ，了解如何检查 Ray Dashboard 中的指标。


### 手动：设置 Grafana 或其他工具，如 CloudWatch、Cloud Monitoring 和 Datadog
请参阅这些工具的文档以了解如何查询和可视化指标。

```{admonition} Tip
:class: tip
如果您需要手动编写 Prometheus 查询，请查看 Ray 提供的 Grafana 仪表板 JSON 中的 Prometheus 查询，从 `/tmp/ray/session_latest/metrics/grafana/dashboards/default_grafana_dashboard.json` 获取灵感。
```
