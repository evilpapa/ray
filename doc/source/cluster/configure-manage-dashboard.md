(observability-configure-manage-dashboard)=
# 配置管理 Ray 仪表盘
{ref}`Ray 仪表盘<observability-getting-started>` 是监控和调试 Ray 应用程序和集群的最重要工具之一。本页介绍如何在集群上配置 Ray 仪表盘。

仪表板配置可能因您启动 Ray 集群的方式而异「例如，本地 Ray 集群与 KubeRay」。与 Prometheus 和 Grafana 的集成是可选的，以增强仪表板体验。

:::{note}
Ray Dashboard 仅适用于交互式开发和调试，因为集群终止后，仪表板 UI 和底层数据将无法访问。对于生产监控和调试，用户应依赖 [日志持久化](../cluster/kubernetes/user-guides/logging.md)， [指标持久化](./metrics.md)， [Ray 状态持久化](../ray-observability/user-guides/cli-sdk.rst)，和其他可观察性工具。
:::

## 更改 Ray Dashboard 端口
Ray Dashboard 运行在头节点的 `8265` 端口。请按照以下说明自定义端口「如果需要」。

::::{tab-set}

:::{tab-item} 单节点本地集群
**通过 CLI 明确启动集群** <br/>
在命令行为 ``ray start`` 传递 ``--dashboard-port`` 参数。

**通过 `ray.init` 明确启动集群** <br/>
在调用 ``ray.init()`` 传递关键参数 ``dashboard_port``。
:::

:::{tab-item} VM 集群启动器
在 [集群启动 YAML 文件](https://github.com/ray-project/ray/blob/0574620d454952556fa1befc7694353d68c72049/python/ray/autoscaler/aws/example-full.yaml#L172) 的 `head_start_ray_commands` 节点包含  ``--dashboard-port``  参数。
```yaml
head_start_ray_commands: 
  - ray stop 
  # Replace ${YOUR_PORT} with the port number you need.
  - ulimit -n 65536; ray start --head --dashboard-port=${YOUR_PORT} --port=6379 --object-manager-port=8076 --autoscaling-config=~/ray_bootstrap_config.yaml 

```
:::

:::{tab-item} KubeRay
参考 [指定非默认端口](https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/config.html#specifying-non-default-ports) 页获取详细信息。
:::

::::

(dashboard-in-browser)=
## 在浏览器查看 Ray Dashboard
当你在笔记本电脑上启动单节点 Ray 集群时，你可以通过 Ray 初始化时打印的 URL 访问仪表板「默认 URL 为 `http://localhost:8265`」。


当你通过 {ref}`VM cluster launcher <vm-cluster-quick-start>`，{ref}`KubeRay operator <kuberay-quickstart>`，或手动配置启动一个远程 Ray 集群，Ray 仪表盘会在头节点启动，端口可能是非公开的。你需要额外的设置以从头节点之外进行访问。

:::{danger}
为了安全目的，在没有适当的身份验证的情况下，请勿公开 Ray Dashboard。
:::

::::{tab-set}

:::{tab-item} VM 集群启动器
**端口转发** <br/>
您可以使用 ``ray dashboard`` 命令 安全地将本地流量端口转发到仪表板。

```shell
$ ray dashboard [-p <port, 8265 by default>] <cluster config file>
```

仪表板现在可在 ``http://localhost:8265`` 查看。
:::

:::{tab-item} KubeRay

KubeRay 控制器通过指定 Ray 头 pod 名为 ``<RayCluster name>-head-svc`` 的 service 是仪表盘可用。
在 Kubernetes 集群内通过 ``http://<RayCluster name>-head-svc:8265`` 访问。

有两种方法可以在集群外部公开仪表板：

**1. 设置 ingress** <br/>
按照 [说明](kuberay-ingress) 设置入口以访问 Ray Dashboard。 **入口必须仅允许来自受信任来源的访问。**

**2. 端口转发** <br/>
您还可以使用端口转发从 Kubernetes 集群外部查看仪表板：

```shell
$ kubectl port-forward --address 0.0.0.0 service/${RAYCLUSTER_NAME}-head-svc 8265:8265 
# Visit ${YOUR_IP}:8265 for the Dashboard (e.g. 127.0.0.1:8265 or ${YOUR_VM_IP}:8265)
```

```{admonition} Note
:class: note
不要在生产环境中使用端口转发。按照上述说明使用 Ingress 公开仪表板。
```

有关在 Kubernetes 上配置 Ray 集群网络访问的更多信息，请参阅 {ref}`网络说明 <kuberay-networking>`。

:::

::::

## 在反向代理后运行

通过反向代理访问时，Ray Dashboard 应该可以立即使用。API 请求不需要单独代理。

始终在 URL 末尾以 ``/`` 结束访问仪表盘。
例如，如果您的代理设置为处理对 ``/ray/dashboard`` 的请求，则通过 ``www.my-website.com/ray/dashboard/`` 进行查看。

仪表板发送带有相对 URL 路径的 HTTP 请求。当 ``window.location.href`` 以反斜线 ``/`` 结束，浏览器会按预期处理这些请求。

尽管 [MDN](https://developer.mozilla.org/en-US/docs/Learn/Common_questions/What_is_a_URL#examples_of_relative_urls) 定义了预期行为，但这是许多浏览器处理具有相对 URL 的请求的特性。

通过在反向代理中包含一条规则将用户的浏览器重定向到 ``/``，比如 ``/ray/dashboard`` --> ``/ray/dashboard/`` 来使仪表盘不以 ``/`` 结尾的方式可见。

下面是一个使用 [traefik](https://doc.traefik.io/traefik/getting-started/quick-start/) TOML 文件实现此目的的示例：

```yaml
[http]
  [http.routers]
    [http.routers.to-dashboard]
      rule = "PathPrefix(`/ray/dashboard`)"
      middlewares = ["test-redirectregex", "strip"]
      service = "dashboard"
  [http.middlewares]
    [http.middlewares.test-redirectregex.redirectRegex]
      regex = "^(.*)/ray/dashboard$"
      replacement = "${1}/ray/dashboard/"
    [http.middlewares.strip.stripPrefix]
      prefixes = ["/ray/dashboard"]
  [http.services]
    [http.services.dashboard.loadBalancer]
      [[http.services.dashboard.loadBalancer.servers]]
        url = "http://localhost:8265"
```

```{admonition} Warning
:class: warning
Ray Dashboard 提供对 Ray Cluster 的 **读写** 访问权限。反向代理必须提供身份验证或网络入口控制，以防止未经授权访问 Cluster。
```

## 禁用 Dashboard

如果您使用或 `ray[default]` 或 {ref}`其他安装命令 <installation>` 仪表盘会自动包含并启动。

要禁用仪表盘，适应以下参数 `--include-dashboard`。

::::{tab-set}

:::{tab-item} 单节点本地集群

**明确以 CLI 方式启动** <br/>

```bash
ray start --include-dashboard=False
```

**明确以 `ray.init` 方式启动集群** <br/>

```{testcode}
:hide:

import ray
ray.shutdown()
```

```{testcode}
import ray
ray.init(include_dashboard=False)
```

:::

:::{tab-item} VM 集群启动器
在 [集群启动器 YAML 文件](https://github.com/ray-project/ray/blob/0574620d454952556fa1befc7694353d68c72049/python/ray/autoscaler/aws/example-full.yaml#L172) 的 `head_start_ray_commands` 节点
包含 `ray start --head --include-dashboard=False` 参数。
:::

:::{tab-item} KubeRay

```{admonition} Warning
:class: warning
不建议禁用 Dashboard，因为 KubeRay 的一些特性如 `RayJob` 和 `RayService` 依赖它。
```

设置 `spec.headGroupSpec.rayStartParams.include-dashboard` 为 `False`。查看这个 [YAML 示例文件](https://gist.github.com/kevin85421/0e6a8dd02c056704327d949b9ec96ef9)。

:::
::::


(observability-visualization-setup)=
## 将 Grafana 可视化嵌入到 Ray 仪表盘

为了增强 Ray Dashboard 体验，例如 {ref}`查看时间序列指标<dash-metrics-view>` 以及日志、作业信息等，请设置 Prometheus 和 Grafana 并将它们与 Ray Dashboard 集成。

### 设置 Prometheus
要呈现 Grafana 可视化效果，您需要 Prometheus 从 Ray 集群中抓取指标。按照 {ref}`说明 <prometheus-setup>` 设置您的 Prometheus 服务器并开始从 Ray 集群中抓取系统和应用程序指标。


### 设置 Grafana
Grafana 是一款支持 Prometheus 指标高级可视化的工具，可让您使用自己喜欢的指标创建自定义仪表板。按照 {ref}`说明 <grafana>` 设置 Grafana。


(embed-grafana-in-dashboard)=
### 将 Grafana 可视化嵌入到 Ray 仪表盘
要在 Ray Dashboard 中查看嵌入的时间序列可视化，必须进行以下设置：

1. 集群的头节点能够访问 Prometheus 和 Grafana。
2. 仪表板用户的浏览器能够访问 Grafana。

启动 Ray Clusters 时，使用 `RAY_GRAFANA_HOST`、 `RAY_PROMETHEUS_HOST`、 `RAY_PROMETHEUS_NAME` 及 `RAY_GRAFANA_IFRAME_HOST` 环境变量进行配置。

* 设置 `RAY_GRAFANA_HOST` 为头节点可用于访问 Grafana 的地址。头节点在后端对 Grafana 进行健康检查。
* 设置 `RAY_PROMETHEUS_HOST` 头节点可以用来访问 Prometheus 的地址。
* 设置 `RAY_PROMETHEUS_NAME` 选择 Grafana 仪表板面板使用的其他数据源。默认为“Prometheus”。
* 设置 `RAY_GRAFANA_IFRAME_HOST` 为用户浏览器可用于访问 Grafana 并嵌入可视化的地址。如果 `RAY_GRAFANA_IFRAME_HOST` 未设置，Ray Dashboard 将使用 `RAY_GRAFANA_HOST` 的值。

例如，如果头节点的 IP 是 55.66.77.88 并且 Grafana 托管在端口 3000 上。将值设置为 `RAY_GRAFANA_HOST=http://55.66.77.88:3000`。
* 如果手动启动单节点 Ray 集群，请确保这些环境变量在启动集群之前或作为命令 `ray start ...` 前缀前进行设置并可访问，例如 `RAY_GRAFANA_HOST=http://55.66.77.88:3000 ray start ...`
* 如果使用 VM Cluster Launcher {ref}`VM Cluster Launcher <cloud-vm-index>` 启动 Ray Cluster，则应将环境变量设置在 `head_start_ray_commands` 之下，作为 `ray start ...` 命令的前缀。
* 如果通过 {ref}`KubeRay <kuberay-index>` 启动集群，参考 {ref}`教程 <kuberay-prometheus-grafana>`。

如果所有环境变量都设置正确，您应该在 {ref}`Ray Dashboard <observability-getting-started>` 中看到时间序列指标。

:::{note}
如果您为每个 Ray 集群使用不同的 Prometheus 服务器，并对所有集群使用相同的 Grafana 服务器，需为每个 Ray 集群设置不同的 `RAY_PROMETHEUS_NAME` 环境变量值，并添加这些数据源到 Grafana。按照 {ref}`这些说明 <grafana>` 设置 Grafana。
:::

#### 备用 Prometheus 主机
默认情况下，Ray Dashboard 假定 Prometheus 托管在 `localhost:9090`。您可以选择在非默认端口或其他机器上运行 Prometheus。 这种情况下，请确保 Prometheus 可以按照 {ref}`此处的 <scrape-metrics>` 说明从您的 Ray 节点抓取指标。

然后，按照上述步骤正确配置 `RAY_PROMETHEUS_HOST` 环境变量。 例如，如果 Prometheus 托管在 IP 为 55.66.77.88 的节点的端口 9000 上，则设置 `RAY_PROMETHEUS_HOST=http://55.66.77.88:9000`。


#### 备用 Grafana 主机
默认情况下，Ray Dashboard 假定 Grafana 托管在 `localhost:3000` 您可以选择在非默认端口或其他机器上运行 Grafana，只要头节点和仪表板用户的浏览器可以访问它。

如果 Grafana 在 Kubernetes 集群上使用 NGINX 入口公开，则 Grafana 入口注释中应该存在以下行：

```yaml
nginx.ingress.kubernetes.io/configuration-snippet: |
    add_header X-Frame-Options SAMEORIGIN always;
```

当 Grafana 和 Ray Cluster 都在同一个 Kubernetes 集群上时，设置`RAY_GRAFANA_HOST` 为 Grafana ingress 的外部 URL。



#### Grafana 的用户身份认证
当 Grafana 实例需要用户身份验证时，其配置文件 [配置文件](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) 必须包含以下设置才能正确嵌入 Ray Dashboard：

```ini
  [security]
  allow_embedding = true
  cookie_secure = true
  cookie_samesite = none
```

#### 故障排除

##### 仪表板消息：未检测到 Prometheus 或 Grafana 服务器
如果您已按照上述说明设置所有设置，请在浏览器中运行以下连接检查：
* 检查 Head Node 是否连接到 Prometheus：添加 `api/prometheus_health` 到 Ray Dashboard URL (例如： http://127.0.0.1:8265/api/prometheus_health) 末尾并访问它。
* 检查头节点与 Grafana 服务器的连接：添加 `api/grafana_health` 到 Ray Dashboard URL (例如： http://127.0.0.1:8265/api/grafana_health) 末尾并访问它。
* 检查浏览器与 Grafana 服务器的连接：访问 `RAY_GRAFANA_IFRAME_HOST` 中使用的 URL。


##### 收到 `RAY_GRAFANA_HOST` 未设置错误提示
如果您已设置 Grafana，请检查：
* 您已在 URL 协议中包含了「例如，`http://your-grafana-url.com` 而不是 `your-grafana-url.com`」。
* URL 没有反斜杠「例如， `http://your-grafana-url.com` 而不是 `http://your-grafana-url.com/`」。

##### 证书颁发机构「CA 错误」
如果您的 Grafana 实例托管在 HTTPS 后面，您可能会看到 CA 错误。请联系 Grafana 服务所有者以正确启用 HTTPS 流量。


## 查看内置 Dashboard API 指标

Dashboard 由一个服务器提供支持，该服务器通过 API 端点提供 UI 代码和有关集群的数据。
Ray 为每个 API 端点发出基本的 Prometheus 指标：

`ray_dashboard_api_requests_count_requests_total`: 收集请求总数。按端点、方法和 http_status 标记。

`ray_dashboard_api_requests_duration_seconds_bucket`: 收集请求的持续时间。这是按端点和方法标记的。

例如，您可以使用以下查询查看所有请求的 p95 持续时间：

```text

histogram_quantile(0.95, sum(rate(ray_dashboard_api_requests_duration_seconds_bucket[5m])) by (le))
```

您可以从 Prometheus 或 Grafana UI 查询这些指标。请参阅上文以了解如何设置这些工具。
