(serve-key-concepts)=

# 关键概念

(serve-key-concepts-deployment)=

## 部署

Deployment 是 Ray Serve 的核心概念。
部署包含业务逻辑或 ML 模型来处理传入的请求，并且可以扩展以在 Ray 集群中运行。
在运行时，部署由多个副本组成，这些副本是类或函数的单独副本，在单独的 Ray Actor（进程）中启动。
可以增加或减少副本数量（甚至自动扩展）以匹配传入的请求负载。

要定义部署，请在 Python 类上（或简单用例的函数）使用装饰器 {mod}`@serve.deployment <ray.serve.api.deployment>` 。
然后，将 `bind` 部署与构造函数的可选参数一起使用以定义 [应用](serve-key-concepts-application)。
最后，使用 `serve.run` （或等效的CLI 命令，有关详细信息，请参阅 [Development 工作流](serve-dev-workflow) ）运行应用。

```{literalinclude} ../serve/doc_code/key_concepts.py
:start-after: __start_my_first_deployment__
:end-before: __end_my_first_deployment__
:language: python
```

(serve-key-concepts-application)=

## 应用

应用程序是 Ray Serve 集群中的升级单位。应用程序由一个或多个部署组成。其中一个部署被视为 [“ingress” deployment](serve-key-concepts-ingress-deployment)，它处理所有入站流量。

应用可以通过 HTTP 在指定位置 `route_prefix` 或使用 Python 调用应用程序 `DeploymentHandle` 访问。
 
(serve-key-concepts-deployment-handle)=

## DeploymentHandle (composing deployments)

Ray Serve 通过允许多个独立部署相互调用来实现灵活的模型组合和扩展。
绑定部署时，您可以包含对 _其他绑定部署_ 的引用。
然后，在运行时，这些参数中的每一个都会转换为 {mod}`DeploymentHandle <ray.serve.handle.DeploymentHandle>` 来用于使用 Python 原生 API 查询部署的参数。
下面是一个基本示例，其中部署 `Driver` 可以调用两个下游模型。
有关更全面的指南，请参阅 [模型组合指南](serve-model-composition)。

```{literalinclude} ../serve/doc_code/key_concepts.py
:start-after: __start_deployment_handle__
:end-before: __end_deployment_handle__
:language: python
```

(serve-key-concepts-ingress-deployment)=

## Ingress 部署（HTTP 处理）

Serve 应用程序可以由多个部署组成，这些部署可以组合起来执行模型组合或复杂的业务逻辑。
但是，一个部署始终是传递到 `serve.run` 来部署应用程序的“顶级”部署。
此部署称为“入口部署”，因为它充当应用程序所有流量的入口点。
通常，它会路由到其他部署或使用 `DeploymentHandle`  API 调用它们，并在返回给用户之前组合结果。

入口部署定义了应用程序的 HTTP 处理逻辑。
默认情况下， `__call__` 将调用类的方法并传入 `Starlette` 请求对象。
响应将序列化为 JSON，但 `Starlette` 也可以直接返回其他响应对象。
以下是示例：

```{literalinclude} ../serve/doc_code/key_concepts.py
:start-after: __start_basic_ingress__
:end-before: __end_basic_ingress__
:language: python
```

绑定部署并运行 `serve.run()` 后，它现在由 HTTP 服务器公开并使用指定的类处理请求。
我们可以使用 `requests` 查询模型来验证它是否正常工作。

为了实现更具表现力的 HTTP 处理，Serve 还内置了 `FastAPI`。
 这允许您使用 FastAPI 的完整表现力来定义更复杂的 API：

```{literalinclude} ../serve/doc_code/key_concepts.py
:start-after: __start_fastapi_ingress__
:end-before: __end_fastapi_ingress__
:language: python
```

## 下一步是什么？
现在您已经了解了关键概念，您可以深入了解这些指南：
- [资源分配](serve-resource-allocation)
- [自动扩缩指南](serve-autoscaling)
- [配置 HTTP 逻辑并与 FastAPI 集成](http-guide)
- [Serve 应用程序的开发工作流程](serve-dev-workflow)
- [组合部署以执行模型组合](serve-model-composition)
