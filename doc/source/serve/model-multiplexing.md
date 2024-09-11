(serve-model-multiplexing)=

# 模型多路复用

本节帮助您了解如何使用 `serve.multiplexed` 和 `serve.get_multiplexed_model_id` API 编写多路复用部署。

这是一个实验性功能，API 将来可能会发生变化。欢迎您试用并向我们提供反馈！

## 为什么要进行模型多路复用？

模型多路复用是一种用于从副本池中高效地为具有相似输入类型的多个模型提供服务的技术。流量根据请求标头路由到相应的模型。 为了使用副本池为多个模型提供服务，
模型多路复用可以优化成本并对流量进行负载平衡。这在您可能拥有许多具有相同形状但不同权重且调用稀疏的模型的情况下非常有用。如果部署的任何副本都已加载模型，则该模型的传入流量（基于请求标头）将自动路由到该副本，从而避免不必要的加载时间。

## 编写多路复用部署

要编写多路复用部署，请使用 `serve.multiplexed` 和 `serve.get_multiplexed_model_id` API。

假设您在 aws s3 存储桶内有多个 Torch 模型，其结构如下：
```
s3://my_bucket/1/model.pt
s3://my_bucket/2/model.pt
s3://my_bucket/3/model.pt
s3://my_bucket/4/model.pt
...
```

定义多路复用部署：
```{literalinclude} doc_code/multiplexed.py
:language: python
:start-after: __serve_deployment_example_begin__
:end-before: __serve_deployment_example_end__
```

:::{note}
该 `serve.multiplexed` API 还有一个 `max_num_models_per_replica` 参数。用它来配置单个副本中要加载多少个模型。如果模型数量大于 `max_num_models_per_replica`，Serve 将使用 LRU 策略逐出最近最少使用的模型。
:::

:::{tip}
此代码示例使用 Pytorch Model 对象。您也可以定义自己的模型类并在此处使用它。要在模型被驱逐时释放资源，请实现该 `__del__` 方法。Ray Serve 内部调用该 `__del__` 方法在模型被驱逐时释放资源。
:::


`serve.get_multiplexed_model_id` 于从请求标头中检索模型 id，然后将 model_id 传递到 `get_model` 函数中。如果在副本中找不到模型 id，Serve 将从 s3 bucket 加载模型并将其缓存在副本中。如果在副本中找到模型 id，Serve 将返回缓存的模型。

:::{note}
在内部，serve router 将根据请求标头中的模型 ID 将流量路由到相应的副本。
如果所有持有该模型的副本都已超额订阅，ray serve 会将请求发送到未加载该模型的新副本。该副本将从 s3 存储桶中加载模型并缓存它。
:::

要向特定模型发送请求，请在请求标头中包含该 `serve_multiplexed_model_id` 字段，并将值设置为要向其发送请求的模型 ID。
```{literalinclude} doc_code/multiplexed.py
:language: python
:start-after: __serve_request_send_example_begin__
:end-before: __serve_request_send_example_end__
```
:::{note}
`serve_multiplexed_model_id` 在请求标头中是必需的，并且其值应该是您要向其发送请求的模型 ID。

如果 `serve_multiplexed_model_id` 在请求标头中找不到，Serve 会将其视为正常请求并将其路由到随机副本。
:::

运行上述代码后，您应该在部署日志中看到以下几行：
```
INFO 2023-05-24 01:19:03,853 default_Model default_Model#EjYmnQ CUpzhwUUNw / default replica.py:442 - Started executing request CUpzhwUUNw
INFO 2023-05-24 01:19:03,854 default_Model default_Model#EjYmnQ CUpzhwUUNw / default multiplex.py:131 - Loading model '1'.
INFO 2023-05-24 01:19:04,859 default_Model default_Model#EjYmnQ CUpzhwUUNw / default replica.py:542 - __CALL__ OK 1005.8ms
```

如果您继续加载更多模型并超出 `max_num_models_per_replica`，则最近最少使用的模型将被逐出，并且您将在部署日志中看到以下几行：::
```
INFO 2023-05-24 01:19:15,988 default_Model default_Model#rimNjA WzjTbJvbPN / default replica.py:442 - Started executing request WzjTbJvbPN
INFO 2023-05-24 01:19:15,988 default_Model default_Model#rimNjA WzjTbJvbPN / default multiplex.py:145 - Unloading model '3'.
INFO 2023-05-24 01:19:15,988 default_Model default_Model#rimNjA WzjTbJvbPN / default multiplex.py:131 - Loading model '4'.
INFO 2023-05-24 01:19:16,993 default_Model default_Model#rimNjA WzjTbJvbPN / default replica.py:542 - __CALL__ OK 1005.7ms
```

您还可以使用 {mod}`options <ray.serve.handle.RayServeHandle>` API 向特定模型发送请求。
```{literalinclude} doc_code/multiplexed.py
:language: python
:start-after: __serve_handle_send_example_begin__
:end-before: __serve_handle_send_example_end__
```

使用模型组合时，您可以使用 Serve DeploymentHandle 将请求从上游部署发送到多路复用部署。您需要在选项中设置 `multiplexed_model_id` 。例如：
```{literalinclude} doc_code/multiplexed.py
:language: python
:start-after: __serve_model_composition_example_begin__
:end-before: __serve_model_composition_example_end__
```
