.. _tune-tutorial:

.. TODO: make this an executable notebook later on.

Ray Tune 入门
=============================

本教程将引导您完成设置 Tune 实验的过程。
首先，我们采用 PyTorch 模型并向您展示如何利用 Ray Tune 来
优化此模型的超参数。
具体来说，我们将通过 HyperOpt 利用早期停止和贝叶斯优化来实现这一点。

.. tip:: 如果您对如何改进本教程有任何建议，
    请 `告诉我们 <https://github.com/ray-project/ray/issues/new/choose>`_！

要运行此示例，您需要安装以下内容：

.. code-block:: bash

    $ pip install "ray[tune]" torch torchvision

设置 Pytorch 模型进行调整
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

首先，让我们先导入一些依赖项。
我们导入一些 PyTorch 和 TorchVision 模块来帮助我们创建模型并对其进行训练。
此外，我们将导入 Ray Tune 来帮助我们优化模型。
如您所见，我们使用所谓的调度程序，在本例中的  ``ASHAScheduler`` ，
我们将在本教程后面使用它来调整模型。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __tutorial_imports_begin__
   :end-before: __tutorial_imports_end__

然后，让我们定义一个我们将要训练的简单 PyTorch 模型。
如果您不熟悉 PyTorch，定义模型的最简单方法是实现一个 ``nn.Module`` 。

这需要您设置模型的 ``__init__`` 并实现 ``forwward`` 。
在此示例中，我们使用一个小型卷积神经网络，该神经网络由一个 2D 卷积层、一个完全连接层和
一个 softmax 函数组成。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after:  __model_def_begin__
   :end-before:  __model_def_end__

下面，我们实现了用于训练和评估 Pytorch 模型的函数。
为此，我们定义了一个 ``train`` 和一个 ``test`` 函数。
如果您知道如何执行此操作，请跳至下一部分。

.. dropdown:: 训练和评估模型

    .. literalinclude:: /../../python/ray/tune/tests/tutorial.py
       :language: python
       :start-after: __train_def_begin__
       :end-before: __train_def_end__

.. _tutorial-tune-setup:

为使用 Tune 的训练设置 ``Tuner`` 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

下面，我们定义一个函数，用于训练 Pytorch 模型多个 epoch。
此函数将在后台单独的 :ref:`Ray Actor （进程） <actor-guide>` 上执行，
因此我们需要将模型的性能反馈给 Tune（位于主 Python 进程上）。

为此，我们在训练函数中调用 :ref:`session.report <tune-function-docstring>` ，
将性能值发送回 Tune。由于该函数是在单独的进程上执行的，
因此请确保该函数可由 :ref:`Ray 序列化 <serialization-guide>` 。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __train_func_begin__
   :end-before: __train_func_end__

让我们通过调用 :ref:`Tuner.fit <tune-run-ref>` ，并从 :ref:`均匀分布 <tune-search-space>` 中
随机抽取学习率和动量。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __eval_func_begin__
   :end-before: __eval_func_end__

``Tuner.fit`` 返回一个 :ref:`ResultGrid 对象 <tune-analysis-docs>`。
您可以使用它来绘制本次试验的表现。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __plot_begin__
   :end-before: __plot_end__

.. note:: Tune 将自动在您的机器或集群上所有可用的核心/GPU 上运行并行试验。
    要限制并发试验的数量，请使用 :ref:`ConcurrencyLimiter <limiter>`。


采用自适应连续减半的提前停止 (ASHAScheduler) 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

让我们将早期停止集成到我们的优化过程中。让我们使用 :ref:`ASHA <tune-scheduler-hyperband>`， 这是一种可扩展的 `原则性早起停止`_ 算法。

.. _`原则性早起停止`: https://blog.ml.cmu.edu/2018/12/12/massively-parallel-hyperparameter-optimization/

从高层次来看，ASHA 会终止那些前景不佳的试验，并将更多的时间和资源分配给更有前景的试验。
随着我们的优化过程变得更加高效，通过调整 ``num_samples`` 参数，我们可以 **将搜索空间增加 5 倍**。

ASHA 在 Tune 中作为 “试验调度程序” 实现。
这些试验调度程序可以提前终止不良试验、暂停试验、克隆试验以及更改正在运行的试验的超参数。
有关可用调度程序和库集成的更多详细信息，请参阅 :ref:`the TrialScheduler 文档 <tune-schedulers>` 。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __run_scheduler_begin__
   :end-before: __run_scheduler_end__

您可以在 Jupyter 笔记本中运行下面的代码来直观地了解试验进度。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __plot_scheduler_begin__
   :end-before: __plot_scheduler_end__

.. image:: /images/tune-df-plot.png
    :scale: 50%
    :align: center

您还可以使用 :ref:`TensorBoard <tensorboard>` 来可视化结果。

.. code:: bash

    $ tensorboard --logdir {logdir}


在 Tune 中使用搜索算法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

除了 :ref:`TrialSchedulers <tune-schedulers>`之外，您还可以使用
贝叶斯优化等智能搜索技术进一步优化超参数。
为此，您可以使用 Tune :ref:`搜索算法 <tune-search-alg>`。
搜索算法利用优化算法来智能地导航给定的超参数空间。

请注意，每个库都有定义搜索空间的特定方式。

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __run_searchalg_begin__
   :end-before: __run_searchalg_end__

Tune 允许您将一些搜索算法与不同的试验调度程序结合使用。参阅 :ref:`此页面了解更多信息 <tune-schedulers>`。

调整后评估模型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

您可以使用 :ref:`ExperimentAnalysis 对象 <tune-analysis-docs>` 评估最佳训练模型来检索最佳模型：

.. literalinclude:: /../../python/ray/tune/tests/tutorial.py
   :language: python
   :start-after: __run_analysis_begin__
   :end-before: __run_analysis_end__


下一步
----------

* 查看 :ref:`Tune 教程 <tune-guides>` 获取有关将 Tune 与您喜欢的机器学习库结合使用的指南。
* 浏览我们的 :ref:`示例库 <tune-general-examples>` ，了解如何将 Tune 与 PyTorch、XGBoost、Tensorflow 等结合使用。
* 如果您遇到问题或者有任何疑问，请在我们的 Github 上提出问题并 `告知我们 <https://github.com/ray-project/ray/issues>`__ 。
* 要检查应用程序的运行情况，您可以使用 :ref:`Ray 仪表盘 <observability-getting-started>`。
