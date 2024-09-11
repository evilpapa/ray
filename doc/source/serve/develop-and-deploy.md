(serve-develop-and-deploy)=

# 开发并部署 ML 应用

在本地开发 Ray Serve 应用程序并将其部署到生产中的流程包括以下步骤：

* 将机器学习模型转换为 Ray Serve 应用程序
* 本地测试应用程序
* 为生产部署构建服务配置文件
* 使用配置文件部署应用程序

## 将模型转换为 Ray Serve 应用

此示例使用文本翻译模型：

```{literalinclude} ../serve/doc_code/getting_started/models.py
:start-after: __start_translation_model__
:end-before: __end_translation_model__
:language: python
```

这个名为 `model.py` 的 Python 文件，使用类 `Translator` 将英文文本翻译成法语。

- 在 `Translator` 的 `__init__` 方法的 `self.model` 变量
  存储了一个使用 [t5-small](https://huggingface.co/t5-small)
  模型的方法来翻译文本。
- 当 `self.model` 对英文文本调用时，它会返回格式
  为 `[{"translation_text": "..."}]` 字典的法语翻译文本。
- `Translator` 的 `translate` 方法通过索引字典来提取翻译的文本。

复制并粘贴脚本并在本地运行。它会翻译 `"Hello world!"`
成 `"Bonjour Monde!"`。

```console
$ python model.py

Bonjour Monde!
```

将此模型转换为具有 FastAPI 的 Ray Serve 应用程序需要进行三处更改：
1. 导入 Ray Serve 和 Fast API 依赖项
2. 使用 FastAPI 的装饰器 `@serve.deployment` 和 `@serve.ingress(app)` 添加用于 Serve 部署
3. `bind` `Translator` deployment 到其构造函数中传递的参数

对于其他 HTTP 选项，请参阅 [设置 FastAPI 和 HTTP](serve-set-up-fastapi-http)。

```{literalinclude} ../serve/doc_code/develop_and_deploy/model_deployment_with_fastapi.py
:start-after: __deployment_start__
:end-before: __deployment_end__
:language: python
```

请注意，代码配置了部署的参数，例如 `num_replicas` 和 `ray_actor_options`.。这些参数有助于配置部署的副本数以及每个副本的资源要求。在本例中，我们设置了 2 个模型副本，每个副本占用 0.2 个 CPU 和 0 个 GPU。有关部署上可配置参数的完整指南，请参阅 [配置 Serve 部署](serve-configure-deployment)。

## 本地测试 Ray Serve 应用程序

要在本地测试，请使用 CLI 命令 `serve run` 运行脚本。此命令接受格式为 `module:application`的导入路径。从包含保存为 `model.py` 脚本本地副本的目录运行该命令，以便它可以导入应用程序：

```console
$ serve run model:translator_app
```

此命令运行 `translator_app` 应用程序，然后阻止将日志流式传输到控制台。您可以使用 `Ctrl-C` 来终止它，这将关闭应用程序。

现在通过 HTTP 测试模型。通过以下默认 URL 访问：

```
http://127.0.0.1:8000/
```

发送包含英文文本的 JSON 数据的 POST 请求。此客户端脚本请求“Hello world!”的翻译：

```{literalinclude} ../serve/doc_code/develop_and_deploy/model_deployment_with_fastapi.py
:start-after: __client_function_start__
:end-before: __client_function_end__
:language: python
```

部署 Ray Serve 应用程序时，使用CLI 命令 `serve status` 检查应用程序和部署的状态。有关 `serve status` 输出格式的更多详细信息，请参阅 [检查生产中的 Serve](serve-in-production-inspecting)。

```console
$ serve status
proxies:
  a85af35da5fcea04e13375bdc7d2c83c7d3915e290f1b25643c55f3a: HEALTHY
applications:
  default:
    status: RUNNING
    message: ''
    last_deployed_time_s: 1693428451.894696
    deployments:
      Translator:
        status: HEALTHY
        replica_states:
          RUNNING: 2
        message: ''
```

## 为生产部署构建服务配置文件


```console
$ serve build model:translator_app -o config.yaml
```

该 `serve build` 命令添加了一个可以修改的默认应用程序名称。生成的 Serve 配置文件为：

```
proxy_location: EveryNode

http_options:
  host: 0.0.0.0
  port: 8000

grpc_options:
  port: 9000
  grpc_servicer_functions: []

applications:

- name: app1
  route_prefix: /
  import_path: model:translator_app
  runtime_env: {}
  deployments:
  - name: Translator
    num_replicas: 2
    ray_actor_options:
      num_cpus: 0.2
      num_gpus: 0.0
```

您还可以使用 Serve 配置文件运行 `serve run` 进行本地测试。例如：

```console
$ serve run config.yaml
```

```console
$ serve status
proxies:
  1894261b372d34854163ac5ec88405328302eb4e46ac3a2bdcaf8d18: HEALTHY
applications:
  app1:
    status: RUNNING
    message: ''
    last_deployed_time_s: 1693430474.873806
    deployments:
      Translator:
        status: HEALTHY
        replica_states:
          RUNNING: 2
        message: ''
```

有关更多详细信息，请参阅 [Serve 配置文件](serve-in-production-config-file)。

## 在生产中部署 Ray Serve

使用 [KubeRay] 操作器在 Kubernetes 上将 Ray Serve 应用程序部署到生产环境中。将上一步生成的 YAML 文件直接复制到 Kubernetes 配置中。KubeRay 支持零停机升级、状态报告和容错，让您的生产应用程序更具弹性。有关更多信息，请参阅 [在 Kubernetes 上部署](serve-in-production-kubernetes) 。对于生产用途，请考虑实施设置 [头节点容错](serve-e2e-ft-guide-gcs) 的推荐用法。

## 监控 Ray Serve

使用 Ray Dashboard 可以概览 Ray Cluster 和 Ray Serve 应用程序的状态。Ray Dashboard 既可以在本地测试期间使用，也可以在生产中的远程集群上使用。Ray Serve 提供了一些内置指标和日志记录，以及用于在应用程序中添加自定义指标和日志的实用程序。对于生产部署，建议将日志和指标导出到可观察性平台。有关更多详细信息，请参阅 [监控](serve-monitoring) 。

[KubeRay]: kuberay-index
