(rayserve)=

# Ray Serve: 可扩展和可编程的服务

:::{tip}
如果您正在使用或考虑使用 Ray Serve，[请与我们联系](https://docs.google.com/forms/d/1l8HT35jXMPtxVUtQPeGoe09VGp5jcvSv0TqPgyz6lGU) 。
:::

```{image} logo.svg
:align: center
:height: 250px
:width: 400px
```

(rayserve-overview)=

Ray Serve 是一个可扩展的模型服务库，用于构建在线推理 API。
Serve 与框架无关，因此您可以使用单个工具包来提供从使用 PyTorch、TensorFlow 和 Keras 等框架构建的深度学习模型到 Scikit-Learn 模型，再到任意 Python 业务逻辑的所有内容。它具有多种功能和性能优化，可用于提供大型语言模型，例如响应流、动态请求批处理、多节点/多 GPU 服务等。

Ray Serve 特别适合 [模型组合](serve-model-composition) 和多模型服务，使您能够用 Python 代码构建由多个 ML 模型和业务逻辑组成的复杂推理服务。

Ray Serve 建立在 Ray 之上，因此它可以轻松扩展到多台机器，并提供灵活的调度支持「例如部分 GPU」，以便您可以共享资源并以低成本提供许多机器学习模型。

## 快速开始

安装 Ray Serve 和其依赖：

```bash
pip install "ray[serve]"
```
定义一个简单的 “hello world” 应用程序，在本地运行它，并通过 HTTP 查询它。

```{literalinclude} doc_code/quickstart.py
:language: python
```

## 更多示例

::::{tab-set}

:::{tab-item} 模型组合

使用 Serve 的模型组合 API 将多个部署组合成一个应用程序。

```{literalinclude} doc_code/quickstart_composed.py
:language: python
```

:::

:::{tab-item} FastAPI 集成

使用 Serve 的 [FastAPI](https://fastapi.tiangolo.com/) 集成来优雅地处理 HTTP 解析和验证。

```{literalinclude} doc_code/fastapi_example.py
:language: python
```

:::

:::{tab-item} Hugging Face Transformers model

要运行此示例，请安装以下内容： ``pip install transformers``

使用 Ray Serve 提供预先训练的 [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) 模型。
我们将使用的模型是情绪分析模型：它将以文本字符串作为输入，并返回文本是“积极”还是“消极”。

```{literalinclude} doc_code/transformers_example.py
:language: python
```

:::

::::

## 为什么选择 Serve ？

:::{dropdown} 构建端到端 ML 支持的应用程序
:animate: fade-in-slide-down

许多机器学习服务解决方案都侧重于“张量输入、张量输出”服务：也就是说，它们将机器学习模型包装在预定义的结构化端点后面。
然而，机器学习单独使用是没有用的。
将机器学习与业务逻辑和传统的 Web 服务逻辑「例如数据库查询」结合起来通常很重要。

Ray Serve 的独特之处在于，它允许您在单个框架中构建和部署端到端分布式服务应用程序。
您可以使用 Serve 的 FastAPI 集成「请参阅 {ref}`serve-fastapi-http`」组合多个 ML 模型、业务逻辑和富有表现力的 HTTP 处理，以将整个应用程序构建为一个 Python 程序。

:::

:::{dropdown} 使用可编程 API 组合多个模型
:animate: fade-in-slide-down

解决问题通常需要的不仅仅是一个机器学习模型。
例如，图像处理应用程序通常需要一个由预处理、分割和过滤等步骤组成的多阶段管道来实现其最终目标。
在许多情况下，每个模型可能使用不同的架构或框架，并且需要不同的资源「例如 CPU 与 GPU」。

许多其他解决方案支持使用 YAML 或其他配置语言定义静态图。
这可能存在限制并且难以使用。
另一方面，Ray Serve 使用可编程 API 支持多模型组合，其中对不同模型的调用看起来就像函数调用一样。
这些模型可以使用不同的资源并在集群中的不同机器上运行，但您可以像编写常规程序一样编写它。有关更多详细信息，请参阅 {ref}`serve-model-composition` 。

:::

:::{dropdown} 灵活扩展和分配资源
:animate: fade-in-slide-down

机器学习模型是计算密集型的，因此运行起来可能非常昂贵。
任何 ML 服务系统的一个关键要求是能够动态地扩大和缩小规模，并为每个模型分配适当的资源，以处理请求负载，同时节省成本。

Serve 提供了许多内置基元，可帮助您提高 ML 服务应用程序的效率。
它支持通过调整副本数量来动态扩展或缩减模型的资源，批量处理请求以利用高效的矢量化操作「在 GPU 上尤其重要」，以及灵活的资源分配模型，使您能够在有限的硬件资源上服务于许多模型。

:::

:::{dropdown} 避免框架和供应商锁定
:animate: fade-in-slide-down

机器学习发展迅速，新的库和模型架构层出不穷，因此务必要避免将自己锁定在与特定框架相关的解决方案中。
这一点在服务中尤为重要，因为更改基础架构可能耗时、昂贵且风险高。
此外，许多托管解决方案仅限于单个云提供商，这在当今的多云世界中可能是一个问题。

Ray Serve 不依赖于任何特定的机器学习库或框架，而是提供通用的可扩展服务层。
由于它建立在 Ray 之上，因此您可以在 Ray 可以运行的任何地方运行它：在您的笔记本电脑、Kubernetes、任何主要云提供商，甚至是本地。

:::


## Serve 如何帮助我......

:::{dropdown} 数据科学家
:animate: fade-in-slide-down

Serve 可让您轻松地从笔记本电脑转移到集群。您可以在本地机器上测试模型「以及整个部署图」，然后再将其部署到集群上的生产环境中。您无需了解重量级的 Kubernetes 概念或云配置即可使用 Serve。

:::

:::{dropdown} 机器学习工程师
:animate: fade-in-slide-down

Serve 可帮助您扩展部署并可靠高效地运行它们以节省成本。借助 Serve 一流的模型组合 API，您可以将模型与业务逻辑组合在一起并构建端到端面向用户的应用程序。此外，Serve 可在 Kubernetes 上以极低的运营开销本地运行。
:::

:::{dropdown} 机器学习平台工程师
:animate: fade-in-slide-down

Serve 专注于提供可扩展且可靠的 ML 模型服务。因此，它可以成为您的 ML 平台堆栈中重要的即插即用组件。
Serve 支持任意 Python 代码，因此可以与 MLOps 生态系统很好地集成。您可以将其与模型优化器「ONNX、TVM」、模型监控系统「Seldon Alibi、Arize」、模型注册表「MLFlow、Weights and Biases」、机器学习框架「XGBoost、Scikit-learn」、数据应用 UI「Gradio、Streamlit」和 Web API 框架「FastAPI、gRPC」一起使用。

:::

:::{dropdown} LLM 开发人员
:animate: fade-in-slide-down

Serve 可让您快速制作可扩展的 LLM 应用程序原型、开发和部署到生产环境中。许多大型语言模型 (LLM) 应用程序结合了提示预处理、向量数据库查找、LLM API 调用和响应验证。由于 Serve 支持任意 Python 代码，您可以将所有这些步骤编写为单个 Python 模块，从而实现快速开发和轻松测试。然后，您可以快速将 Ray Serve LLM 应用程序部署到生产环境中，并且每个应用程序步骤都可以独立自动扩展以有效容纳用户流量而不会浪费资源。为了提高 LLM 应用程序的性能，Ray Serve 具有批处理功能，并且可以与任何模型优化技术集成。Ray Serve 还支持流式响应，这是类似聊天机器人的应用程序的一项关键功能。

:::


## 与…相比，Serve 如何

:::{dropdown} TFServing, TorchServe, ONNXRuntime
:animate: fade-in-slide-down

Ray Serve 与 *框架无关*，因此您可以将它与任何其他 Python 框架或库一起使用。
我们认为数据科学家不应该被束缚在特定的机器学习框架上。
他们应该能够使用最适合这项工作的工具。

与这些特定于框架的解决方案相比，Ray Serve 不会执行任何特定于模型的优化来让您的 ML 模型运行得更快。 但是，您仍然可以自己优化模型
并在 Ray Serve 中运行它们。例如，您可以运行由
[PyTorch JIT](https://pytorch.org/docs/stable/jit.html) 或 [ONNXRuntime](https://onnxruntime.ai/) 编译的模型。
:::

:::{dropdown} AWS SageMaker, Azure ML, Google Vertex AI
:animate: fade-in-slide-down

作为一个开源项目，Ray Serve 将这些托管产品的可扩展性和可靠性带入您自己的基础设施。
您可以使用 Ray [集群启动器](cluster-index) 将 Ray Serve 部署到所有主要的公共云、K8s 以及裸机和本地机器上。

Ray Serve 不是一个成熟的 ML 平台。
与其他产品相比，Ray Serve 缺乏管理模型生命周期、
可视化其性能等功能。
Ray Serve 主要专注于模型服务，
并为您提供在其上构建自己的 ML 平台所需的原语。

:::

:::{dropdown} Seldon, KServe, Cortex
:animate: fade-in-slide-down

您可以在笔记本电脑上开发 Ray Serve，将其部署到开发箱上，
并将其扩展到多台机器或 Kubernetes 集群，
所有这些都只需很少或根本不需要更改代码。
当您不需要配置和管理 K8s 集群时，入门会容易得多。
部署时，您可以使用我们的 [Kubernetes Operator](kuberay-quickstart) 
将您的 Ray Serve 应用程序透明地部署到 K8s。
:::

:::{dropdown} BentoML, Comet.ml, MLflow
:animate: fade-in-slide-down

许多此类工具专注于独立提供和扩展模型。
相比之下，Ray Serve 与框架无关，专注于模型组合。
因此，Ray Serve 适用于任何模型打包和注册表格式。
Ray Serve 还提供了构建可用于生产的机器学习应用程序的关键功能，包括一流的自动扩展和与业务逻辑的自然集成。
:::

我们坚信 Serve 是独一无二的，因为它让您可以端到端控制您的 ML 应用程序，
同时提供可扩展性和高性能。要使用其他工具实现 Serve 的功能，
您需要将多个框架「如 Tensorflow Serving 和 SageMaker」粘合在一起，
甚至推出自己的微批处理组件来提高吞吐量。

## 了解更多

查看 {ref}`serve-getting-started` 和 {ref}`serve-key-concepts`，
或转到 {doc}`tutorials/index` 开始构建您的 Ray Serve 应用程序。


```{eval-rst}
.. grid:: 1 2 2 2
    :gutter: 1
    :class-container: container pb-3

    .. grid-item-card::
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img
        
        **入门**
        ^^^
        
        从我们的快速入门教程开始，了解如何在 :ref:`本地部署单个模型 <serve-getting-started>` 以及如何 :ref:`将现有模型转换为 Ray Serve 部署 <converting-to-ray-serve-application>` 。
        
        +++
        .. button-ref:: serve-getting-started
            :color: primary
            :outline:
            :expand:
        
            开始使用 Ray Serve    
    
    .. grid-item-card::
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img
        
        **关键概念**
        ^^^
        
        了解 Ray Serve 背后的关键概念。
        了解 :ref:`部署 <serve-key-concepts-deployment>`、 :ref:`如何查询它们 <serve-key-concepts-ingress-deployment>`、 使用 :ref:`DeploymentHandles <serve-key-concepts-deployment-handle>` 将多个模型和业务逻辑组合在一起。
        
        +++
        .. button-ref:: serve-key-concepts
            :color: primary
            :outline:
            :expand:
        
            学习关键概念
        
    .. grid-item-card::
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img
        
        **实例**
        ^^^
        
        按照教程学习如何将 Ray Serve 与 :ref:`TensorFlow <serve-ml-models-tutorial>`、 :ref:`Scikit-Learn <serve-ml-models-tutorial>` 和 :ref:`RLlib <serve-rllib-tutorial>` 集成。
        
        +++
        .. button-ref:: serve-examples
            :color: primary
            :outline:
            :expand:
        
            Serve 示例
        
    .. grid-item-card::
        :class-img-top: pt-2 w-75 d-block mx-auto fixed-height-img
        
        **API 参考**
        ^^^
        
        获取有关 Ray Serve API 的更多深入信息。
        
        +++
        .. button-ref:: serve-api
            :color: primary
            :outline:
            :expand:
        
            阅读 API 参考
        
```

有关更多信息，请参阅以下有关 Ray Serve 的博客文章：

- [生产环境中的 ML 模型服务：常见模式](https://www.anyscale.com/blog/serving-ml-models-in-production-common-patterns) 「作者：Simon Mo、Edward Oakes 和 Michael Galarnyk」
- [使用纯 Python 在生产中提供 NLP 模型的最简单方法](https://medium.com/distributed-computing-with-ray/the-simplest-way-to-serve-your-nlp-model-in-production-with-pure-python-d42b6a97ad55) 「作者：Edward Oakes 和 Bill Chambers」
- [Machine Learning Serving is Broken](https://medium.com/distributed-computing-with-ray/machine-learning-serving-is-broken-f59aff2d607f) 「作者 Simon Mo」
- [如何使用 Ray Serve 扩展您的 FastAPI 应用程序](https://medium.com/distributed-computing-with-ray/how-to-scale-up-your-fastapi-application-using-ray-serve-c9a7b69e786) 「作者 Archit Kulkarni」
