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
它来处理请求。 You can scale and configure each of your deployments independently using
parameters in the `@serve.deployment` decorator. The example configures a few common parameters:

* `num_replicas`: an integer that determines how many copies of our deployment process run in Ray. Requests are load balanced across these replicas, allowing you to scale your deployments horizontally.
* `ray_actor_options`: a dictionary containing configuration options for each replica.
    * `num_cpus`: a float representing the logical number of CPUs each replica should reserve. You can make this a fraction to pack multiple replicas together on a machine with fewer CPUs than replicas.
    * `num_gpus`: a float representing the logical number of GPUs each replica should reserve. You can make this a fraction to pack multiple replicas together on a machine with fewer GPUs than replicas.

All these parameters are optional, so feel free to omit them:

```python
...
@serve.deployment
class Translator:
  ...
```

Deployments receive Starlette HTTP `request` objects [^f1]. By default, the deployment class's `__call__` method is called on this `request` object. The return value is sent back in the HTTP response body.

This is why `Translator` needs a new `__call__` method. The method processes the incoming HTTP request by reading its JSON data and forwarding it to the `translate` method. The translated text is returned and sent back through the HTTP response. You can also use Ray Serve's FastAPI integration to avoid working with raw HTTP requests. Check out {ref}`serve-fastapi-http` for more info about FastAPI with Serve.

Next, we need to `bind` our `Translator` deployment to arguments that will be passed into its constructor. This defines a Ray Serve application that we can run locally or deploy to production (you'll see later that applications can consist of multiple deployments). Since `Translator`'s constructor doesn't take in any arguments, we can call the deployment's `bind` method without passing anything in:

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __model_deploy_start__
:end-before: __model_deploy_end__
:language: python
```

With that, we are ready to test the application locally.

## Running a Ray Serve Application

Here's the full Ray Serve script that we built above:

```{literalinclude} ../serve/doc_code/getting_started/model_deployment_full.py
:start-after: __deployment_full_start__
:end-before: __deployment_full_end__
:language: python
```

To test locally, we run the script with the `serve run` CLI command. This command takes in an import path
to our deployment formatted as `module:application`. Make sure to run the command from a directory containing a local copy of this script saved as `serve_quickstart.py`, so it can import the application:

```console
$ serve run serve_quickstart:translator_app
```

This command will run the `translator_app` application and then block, streaming logs to the console. It can be killed with `Ctrl-C`, which will tear down the application.

We can now test our model over HTTP. It can be reached at the following URL by default:

```
http://127.0.0.1:8000/
```

We'll send a POST request with JSON data containing our English text.
`Translator`'s `__call__` method will unpack this text and forward it to the
`translate` method. Here's a client script that requests a translation for "Hello world!":

```{literalinclude} ../serve/doc_code/getting_started/model_deployment.py
:start-after: __client_function_start__
:end-before: __client_function_end__
:language: python
```

To test our deployment, first make sure `Translator` is running:

```
$ serve run serve_deployment:translator_app
```

While `Translator` is running, we can open a separate terminal window and run the client script. This will get a response over HTTP:

```console
$ python model_client.py

Bonjour monde!
```

## Composing Multiple Models

Ray Serve allows you to compose multiple deployments into a single Ray Serve application. This makes it easy to combine multiple machine learning models along with business logic to serve a single request.
We can use parameters like `autoscaling_config`, `num_replicas`, `num_cpus`, and `num_gpus` to independently configure and scale each deployment in the application.

For example, let's deploy a machine learning pipeline with two steps:

1. Summarize English text
2. Translate the summary into French

`Translator` already performs step 2. We can use [HuggingFace's SummarizationPipeline](https://huggingface.co/docs/transformers/v4.21.0/en/main_classes/pipelines#transformers.SummarizationPipeline) to accomplish step 1. Here's an example of the `SummarizationPipeline` that runs locally:

```{literalinclude} ../serve/doc_code/getting_started/models.py
:start-after: __start_summarization_model__
:end-before: __end_summarization_model__
:language: python
```

You can copy-paste this script and run it locally. It summarizes the snippet from _A Tale of Two Cities_ to `it was the best of times, it was worst of times .`

```console
$ python summary_model.py

it was the best of times, it was worst of times .
```

Here's an application that chains the two models together. The graph takes English text, summarizes it, and then translates it:

```{literalinclude} ../serve/doc_code/getting_started/translator.py
:start-after: __start_graph__
:end-before: __end_graph__
:language: python
```

This script contains our `Summarizer` class converted to a deployment and our `Translator` class with some modifications. In this script, the `Summarizer` class contains the `__call__` method since requests are sent to it first. It also takes in a handle to the `Translator` as one of its constructor arguments, so it can forward summarized texts to the `Translator` deployment. The `__call__` method also contains some new code:

```python
translation = await self.translator.translate.remote(summary)
```

`self.translator.translate.remote(summary)` issues an asynchronous call to the `Translator`'s `translate` method and returns a `DeploymentResponse` object immediately. Calling `await` on the response waits for the remote method call to execute and returns its return value. The response could also be passed directly to another `DeploymentHandle` call.

We define the full application as follows:

```python
app = Summarizer.bind(Translator.bind())
```

Here, we bind `Translator` to its (empty) constructor arguments, and then we pass in the bound `Translator` as the constructor argument for the `Summarizer`. We can run this deployment graph using the `serve run` CLI command. Make sure to run this command from a directory containing a local copy of the `serve_quickstart_composed.py` code:

```console
$ serve run serve_quickstart_composed:app
```

We can use this client script to make requests to the graph:

```{literalinclude} ../serve/doc_code/getting_started/translator.py
:start-after: __start_client__
:end-before: __end_client__
:language: python
```

While the application is running, we can open a separate terminal window and query it:

```console
$ python composed_client.py

c'était le meilleur des temps, c'était le pire des temps .
```

Composed Ray Serve applications let you deploy each part of your machine learning pipeline, such as inference and business logic steps, in separate deployments. Each of these deployments can be individually configured and scaled, ensuring you get maximal performance from your resources. See the guide on [model composition](serve-model-composition) to learn more.

## Next Steps

- Dive into the {doc}`key-concepts` to get a deeper understanding of Ray Serve.
- View details about your Serve application in the Ray Dashboard: {ref}`dash-serve-view`.
- Learn more about how to deploy your Ray Serve application to production: {ref}`serve-in-production`.
- Check more in-depth tutorials for popular machine learning frameworks: {doc}`tutorials/index`.

```{rubric} Footnotes
```

[^f1]: [Starlette](https://www.starlette.io/) is a web server framework used by Ray Serve.
