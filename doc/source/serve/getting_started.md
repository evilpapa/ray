(serve-getting-started)=

# 入门

本教程将引导您完成编写和测试 Ray Serve 应用程序的过程。它将向您展示如何

* 将机器学习模型转换为 Ray Serve 部署
* 通过 HTTP 在本地测试 Ray Serve 应用程序
* 将多模型机器学习模型组合成一个应用程序

在本教程中我们将使用两个模型：

* [HuggingFace 的 TranslationPipeline](https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.TranslationPipeline) 作为文本翻译模型
* [HuggingFace 的 SummarizationPipeline](https://huggingface.co/docs/transformers/v4.21.0/en/main_classes/pipelines#transformers.SummarizationPipeline) 作为文本摘要模型

您还可以使用任何 Python 框架中的自己的模型来进行操作。

部署这两个模型后，我们将使用 HTTP 请求对它们进行测试。

:::{tip}
如果您对如何改进本教程有任何建议，
    请 [告诉我们](https://github.com/ray-project/ray/issues/new/choose)！
:::

要运行此示例，您需要安装以下内容：

```bash
pip install "ray[serve]" transformers requests torch
```


## 文本翻译模型「Ray Serve 之前」

首先，我们来看看我们的文本翻译模型。以下是它的代码：

```{literalinclude} ../serve/doc_code/getting_started/models.py
:start-after: __start_translation_model__
:end-before: __end_translation_model__
:language: python
```

这个名为 `model.py`的 Python 文件，使用 `Translator` 类将英文文本翻译成法语。

- `Translator` 中 `__init__` 方法的 `self.model` 变量
  存储了一个使用 [t5-small](https://huggingface.co/t5-small)
  模型翻译文本的函数。
- 当 `self.model` 对英文文本调用时，它会返回格式
  为 `[{"translation_text": "..."}]` 字典的法语翻译文本。
- `Translator` 的 `translate` 方法通过索引字典来提取翻译的文本。

您可以复制粘贴此脚本并在本地运行。它会转换 `"Hello world!"`
为 `"Bonjour Monde!"`。

```console
$ python model.py

Bonjour Monde!
```

请记住，`TranslationPipeline` 是本教程的一个示例 ML 模型。
您可以使用任何 Python 框架中的任意模型进行操作。
查看我们关于 scikit-learn、PyTorch 和 Tensorflow 的教程以获取更多信息和示例：

- {ref}`serve-ml-models-tutorial`

(converting-to-ray-serve-application)=
## 转换为 Ray Serve 应用

在本节中，我们将使用 Ray Serve 部署文本翻译模型，
以便可以对其进行扩展并通过 HTTP 进行查询。 我们将首先转换
`Translator` 为 Ray Serve 部署。

首先，我们打开一个新的 Python 文件并导入 `ray` 和 `ray.serve`：

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __import_start__
:end-before: __import_end__
:language: python
```

导入这些之后，我们可以从上面包含我们的模型代码：

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __model_start__
:end-before: __model_end__
:language: python
```

`Translator` 类有两处修改：
1. 它有一个装饰器， `@serve.deployment`。
2. 它有一种新方法， `__call__`。

装饰器将 `Translator` Python 类转换成 Ray Serve `Deployment` 对象。

每个部署都会存储您编写的单个 Python 函数或类，并使用
它来处理请求。 您可以使用 `@serve.deployment` 装饰器中的参数
单独扩展和配置每个部署。该示例配置了一些常用参数：

* `num_replicas`: 整数，决定我们的部署流程在 Ray 中运行的副本数。请求在这些副本之间进行负载平衡，允许您水平扩展部署。
* `ray_actor_options`: 包含每个副本的配置选项的字典。
    * `num_cpus`: 示每个副本应保留的逻辑 CPU 数量的浮点数。您可以将其设为分数，以便将多个副本打包到 CPU 数量少于副本数量的机器上。
    * `num_gpus`: 示每个副本应保留的逻辑 GPU 数量的浮点数。您可以将其设为分数，以便将多个副本打包到 GPU 数量少于副本数量的机器上。

所有这些参数都是可选的，因此可以随意省略它们：

```python
...
@serve.deployment
class Translator:
  ...
```

部署接收 Starlette HTTP `request` 对象 [^f1]。 默认，部署类的 `__call__` 方法在 `request` 对象上被调用。返回值在 HTTP 响应主体中发回。

这是为什么 `Translator` 需要一个新的 `__call__` 方法。该方法处理传入的 HTTP 请求读取 JSON 数据并转发到 `translate` 方法。翻译后的文本将返回并通过 HTTP 响应发送回去。您还可以使用 Ray Serve 的 FastAPI 集成来避免使用原始 HTTP 请求。查看 {ref}`serve-fastapi-http` 以获取有关带有 Serve 的 FastAPI 的更多信息。

接下来我们需要将我们的 `Translator` deployment  `bind` 传递给其构造函数的参数。这定义了一个 Ray Serve 应用程序，我们可以在本地运行它或将其部署到生产环境（稍后您将看到应用程序可以由多个部署组成）。 犹豫 `Translator` 的构造函数不接受任何参数，因此我们可以调用 deployment 的 `bind` 方法而无需传入任何内容：

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __model_deploy_start__
:end-before: __model_deploy_end__
:language: python
```

这样，我们就可以准备在本地测试该应用程序了。

## 运行 Ray Serve 应用

以下是我们上面构建的完整 Ray Serve 脚本：

```{literalinclude} ../serve/doc_code/getting_started/model_deployment_full.py
:start-after: __deployment_full_start__
:end-before: __deployment_full_end__
:language: python
```

为了在本地进行测试，我们使用 CLI 命令 `serve run` 运行脚本。此命令接受
格式为 `module:application` 的部署导入路径。确保从包含此脚本的本地副本（保存为 `serve_quickstart.py` ）的目录运行命令，以便它可以导入应用程序：

```console
$ serve run serve_quickstart:translator_app
```

该命令将会运行 `translator_app` 应用程序，然后阻止将日志流式传输到控制台。可以使用 `Ctrl-C`，这将关闭应用程序。

我们现在可以通过 HTTP 测试我们的模型。默认情况下，可以通过以下 URL 访问：

```
http://127.0.0.1:8000/
```

我们将发送一个包含英文文本的 JSON 数据的 POST 请求。
`Translator` 的 `__call__` 方法将解压此文本并将其转发给
`translate` 方法。以下是请求翻译“Hello world!”的客户端脚本：

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __client_function_start__
:end-before: __client_function_end__
:language: python
```

为了测试我们的部署，首先确保 `Translator` 运行：

```
$ serve run serve_deployment:translator_app
```

当 `Translator` 在运行，我们可以打开一个单独的终端窗口并运行客户端脚本。这将通过 HTTP 获得响应：

```console
$ python model_client.py

Bonjour monde!
```

## 组合多模型

Ray Serve 允许您将多个部署组合成一个 Ray Serve 应用程序。这样可以轻松地将多个机器学习模型与业务逻辑结合起来以满足单个请求。
我们可以使用 `autoscaling_config`、`num_replicas`、`num_cpus` 以及 `num_gpus` 等参数来独立配置和扩展应用程序中的每个部署。

例如，让我们部署一个包含两个步骤的机器学习管道：

1. 总结英文文本
2. 将摘要翻译成法语

`Translator` 已经执行了步骤2。我们可以使用 [HuggingFace 的 SummarizationPipeline](https://huggingface.co/docs/transformers/v4.21.0/en/main_classes/pipelines#transformers.SummarizationPipeline) 来完成步骤1。以下是 `SummarizationPipeline` 在本地运行的一个例子：

```{literalinclude} ../serve/doc_code/getting_started/models.py
:start-after: __start_summarization_model__
:end-before: __end_summarization_model__
:language: python
```

您可以复制粘贴此脚本并在本地运行。它将《双城记》中的片段总结为 `it was the best of times, it was worst of times .`

```console
$ python summary_model.py

it was the best of times, it was worst of times .
```

下面是将两个模型连接在一起的应用程序。该图采用英文文本，对其进行总结，然后进行翻译：

```{literalinclude} ../serve/doc_code/getting_started/translator.py
:start-after: __start_graph__
:end-before: __end_graph__
:language: python
```

此脚本包含已转换为部署的类 `Summarizer` 和经过一些修改的类 `Translator`。在此脚本中， `Summarizer` 类包含 `__call__` 方法，因为请求首先发送给它。它还将作为 `Translator` 构造函数的参数之一，因此它可以将摘要文本转发到部署 `Translator` 部署。该 `__call__` 方法还包含一些新代码：

```python
translation = await self.translator.translate.remote(summary)
```

`self.translator.translate.remote(summary)` 对 `Translator` 的 `translate` 方法发起异步调用，并立即返回一个 `DeploymentResponse` 对象。 调用 `await` 应等待远程方法调用执行并返回其返回值。响应也可以直接传递给另一个 `DeploymentHandle` 调用。

我们对完整应用程序的定义如下：

```python
app = Summarizer.bind(Translator.bind())
```

在这里，我们绑定 `Translator` 到它的（空）构造函数参数，然后将绑定的 `Translator` 作为 `Summarizer` 的构造函数参数传入。我们可以使用 CLI 命令 `serve run` 运行此部署图。确保从包含代码本地副本 `serve_quickstart_composed.py` 的目录运行此命令： 

```console
$ serve run serve_quickstart_composed:app
```

我们可以使用此客户端脚本向图表发出请求：

```{literalinclude} ../serve/doc_code/getting_started/translator.py
:start-after: __start_client__
:end-before: __end_client__
:language: python
```

在应用程序运行时，我们可以打开一个单独的终端窗口并查询它：

```console
$ python composed_client.py

c'était le meilleur des temps, c'était le pire des temps .
```

组合式 Ray Serve 应用程序可让您在单独的部署中部署机器学习管道的每个部分，例如推理和业务逻辑步骤。这些部署中的每一个都可以单独配置和扩展，确保您从资源中获得最大性能。请参阅 [模型组合](serve-model-composition) 指南以了解更多信息。

## 下一步

- 深入 {doc}`key-concepts` 以更深入地了解 Ray Serve。
- 在 Ray Dashboard:  {ref}`dash-serve-view` 中查看有关 Serve 应用程序的详细信息。
- 了解有关如何将 Ray Serve 应用程序部署到生产环境的更多信息： {ref}`serve-in-production`。
- 查看有关流行机器学习框架的更多深入教程： {doc}`tutorials/index`。

```{rubric} Footnotes
```

[^f1]: [Starlette](https://www.starlette.io/) 是 Ray Serve 使用的 Web 服务器框架。
