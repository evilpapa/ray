.. _tune-main:

Ray Tune: 超参数调优
===============================

.. image:: images/tune_overview.png
    :scale: 50%
    :align: center

Tune 是一个 Python 库，用于执行任何规模的实验和超参数调整。
您可以通过运行最先进的算法「:ref:`以人群为基础的训练 「PBT」 <tune-scheduler-pbt>` 和 :ref:`HyperBand/ASHA <tune-scheduler-hyperband>`」来调整您最喜欢的机器学习框架「例如 :ref:`PyTorch <tune-pytorch-cifar-ref>`、 :ref:`XGBoost <tune-xgboost-ref>`、 :doc:`Scikit-Learn <examples/tune-sklearn>`、 :doc:`TensorFlow and Keras <examples/tune_mnist_keras>` 以及 :doc:`more <examples/index>`) 。
Tune 还与各种其他超参数优化工具集成，包括 :doc:`Ax <examples/ax_example>`、 :doc:`BayesOpt <examples/bayesopt_example>`、 :doc:`BOHB <examples/bohb_example>`、 :doc:`Dragonfly <examples/dragonfly_example>`、 :doc:`FLAML <examples/flaml_example>`、 :doc:`Hyperopt <examples/hyperopt_example>`、 :doc:`Nevergrad <examples/nevergrad_example>`、 :doc:`Optuna <examples/optuna_example>` 以及 :doc:`SigOpt <examples/sigopt_example>`。

**单击以下选项卡可查看各种机器学习框架的代码示例：**:

.. tab-set::

    .. tab-item:: 快速开始

        要运行此示例，请安装以下内容： ``pip install "ray[tune]"``。

        在这个快速入门示例中，您将看到一个形式为 ``f(x) = a**2 + b`` 的简单函数 `minimize` ，即我们的  `objective`  函数。
        ``a`` 越接近零 ``b`` 越小， ``f(x)`` 的总值就越小。
        我们将为 ``a`` 和 ``b`` 定义一个所谓的 `search space` ，并让 Ray Tune 探索良好值的空间。

        .. callout::

            .. literalinclude:: ../../../python/ray/tune/tests/example.py
               :language: python
               :start-after: __quick_start_begin__
               :end-before: __quick_start_end__

            .. annotations::
                <1> 定义目标函数。

                <2> 定义搜索空间。

                <3> 开始运行 Tune 并打印最佳结果。


    .. tab-item:: Keras+Hyperopt

        要使用 Hyperopt 调整 Keras 模型，您需要将模型包装在一个目标函数中，
        您可以访问该函数的 ``config`` 来选择超参数。
        在下面的示例中，我们仅调整模型第一层的 ``activation`` 参数，
        但您可以调整所需的任何模型参数。
        定义搜索空间后，您只需初始化对象  ``HyperOptSearch`` 并传递给 ``run`` 。
        告诉 Ray Tune 您要优化哪个指标以及是否要最大化或最小化它很重要。

        .. callout::

            .. literalinclude:: doc_code/keras_hyperopt.py
                :language: python
                :start-after: __keras_hyperopt_start__
                :end-before: __keras_hyperopt_end__

            .. annotations::
                <1> 将 Keras 模型包装在目标函数中。

                <2> 定义搜索空间，初始化搜索算法。

                <3> 开始最大限度提高准确度的 Tune 运行。

    .. tab-item:: PyTorch+Optuna

        要使用 Optuna 调整 PyTorch 模型，您需要将模型包装在一个目标函数中，
        您可以访问该函数的 ``config`` 来选择超参数。
        在下面的示例中，我们仅调整模型优化器的  ``momentum`` 和 学习率「 ``lr`` 」参数，
        但您可以调整所需的任何其他模型参数。
        定义搜索空间后，您只需初始化对象 ``OptunaSearch`` 并将其传递给 ``run``。
        告诉 Ray Tune 您要优化哪个指标以及是否要最大化或最小化它很重要。
        我们在迭代后停止调整此训练运行，但您也可以轻松定义其他停止规则。


        .. callout::

            .. literalinclude:: doc_code/pytorch_optuna.py
                :language: python
                :start-after: __pytorch_optuna_start__
                :end-before: __pytorch_optuna_end__

            .. annotations::
                <1> 将 PyTorch 模型包装在目标函数中。

                <2> 定义搜索空间，初始化搜索算法。

                <3> 启动 Tune 运行，最大化平均准确率，并在 5 次迭代后停止。

借助 Tune，您还可以用不到 10 行代码启动多节点 :ref:`分布式超参数扫描 <tune-distributed-ref>` 。
并且，您可以使用  `Ray Serve`_ 在同一基础架构上将模型从训练转移到服务。

.. _`Ray Serve`: ../serve/index.html


.. grid:: 1 2 3 4
    :gutter: 1
    :class-container: container pb-3

    .. grid-item-card::

        **入门**
        ^^^

        在我们的入门教程中，您将学习如何使用 Tune 有效地调整 PyTorch 模型。

        +++
        .. button-ref:: tune-tutorial
            :color: primary
            :outline:
            :expand:

            开始使用 Tune

    .. grid-item-card::

        **关键概念**
        ^^^

        了解 Ray Tune 背后的关键概念。
        了解调优运行、搜索算法、调度程序和其他功能。

        +++
        .. button-ref:: tune-60-seconds
            :color: primary
            :outline:
            :expand:

            Tune 的关键概念

    .. grid-item-card::

        **用户指南**
        ^^^

        我们的指南将向您介绍 Tune 的主要功能，
        例如分布式训练或早期停止。


        +++
        .. button-ref:: tune-guides
            :color: primary
            :outline:
            :expand:

            学习如何使用 Tune

    .. grid-item-card::

        **示例**
        ^^^

        在我们的示例中，您可以找到使用
        scikit-learn、Keras、TensorFlow、PyTorch 和 mlflow 等框架以及最先进的搜索算法集成的实用教程。

        +++
        .. button-ref::  tune-examples-ref
            :color: primary
            :outline:
            :expand:

            Ray Tune 示例

    .. grid-item-card::

        **Ray Tune 常见问题解答**
        ^^^

        在我们详细的常见问题解答中找到常见问题的答案。

        +++
        .. button-ref:: tune-faq
            :color: primary
            :outline:
            :expand:

            Ray Tune FAQ

    .. grid-item-card::

        **Ray Tune API**
        ^^^

        获取有关 Ray Tune API 的更多深入信息，包括有关搜索空间、算法和训练配置的所有信息。

        +++
        .. button-ref:: tune-api-ref
            :color: primary
            :outline:
            :expand:

            阅读 API 参考


为什么选择 Tune？
----------------

还有许多其他超参数优化库。
如果您是 Tune 的新手，您可能会想知道“Tune 有什么不同？”

.. dropdown:: 尖端优化算法
    :animate: fade-in-slide-down

    作为用户，您可能正在研究超参数优化，因为您想要快速提高模型性能。

    Tune 使您能够利用各种这些尖端的优化算法，通过
    `尽早终止不良运行 <tune-scheduler-hyperband>`_、
    :ref:`选择更好的参数进行评估 <tune-search-alg>`，甚至
    :ref:`在训练期间更改超参数 <tune-scheduler-pbt>` 来优化计划，从而降低调整成本。

.. dropdown:: 一流的开发人员生产力工具
    :animate: fade-in-slide-down

    许多超参数优化框架的一个关键问题是需要重构代码以适应框架。
    使用 Tune，您只需 :ref:`添加一些代码片段 <tune-tutorial>` 即可优化模型。

    此外，Tune 从您的代码训练工作流程中删除了样板，
    支持 :ref:`实验结果的多种存储选项「NFS、云存储」 <tune-storage-options>` 以及
    :ref:`将结果记录到 <tune-logging>` MLflow 和 TensorBoard 等工具中，同时还具有高度可定制性。

.. dropdown:: 开箱即用的多 GPU 和分布式训练
    :animate: fade-in-slide-down

    众所周知，超参数调优非常耗时，因此通常需要将此过程并行化。
    大多数其他调优框架都要求您实现自己的多进程框架或构建自己的分布式系统来加快超参数调优速度。

    但是，Tune 允许您透明地 :ref:`跨多个 GPU 和多个节点进行并行化 <tune-parallelism>`。
    Tune 甚至具有无缝 :ref:`容错和云支持 <tune-distributed-ref>`，允许您使用廉价的可抢占实例
    将超参数搜索扩大 100 倍，同时将成本降低 10 倍。

.. dropdown:: 来自另一个超参数优化工具？
    :animate: fade-in-slide-down

    您可能已经在使用现有的超参数调整工具，例如 HyperOpt 或贝叶斯优化。

    在这种情况下，Tune 实际上允许您增强现有工作流程。
    Tune 的 :ref:`搜索算法 <tune-search-alg>` 各种流行的超参数调整库集成
    「参见 :ref:`示例 <tune-examples-ref>`」，并允许您无缝扩展优化过程 - 而不会牺牲性能。

使用 Tune 的项目
-------------------

以下是一些利用 Tune 的热门开源存储库和研究项目。
欢迎提交拉取请求以添加「或请求删除」列出的项目。

- `Softlearning <https://github.com/rail-berkeley/softlearning>`_: Softlearning 是一个强化学习框架，用于在连续域中训练最大熵策略。包括 Soft Actor-Critic 算法的官方实现。
- `Flambe <https://github.com/asappresearch/flambe>`_: 一个用于加速研究及其生产进程的 ML 框架。请参阅 `flambe.ai <https://flambe.ai>`_。
- `基于种群的增强 <https://github.com/arcelien/pba>`_: 基于种群的增强 (PBA) 是一种快速高效地学习用于神经网络训练的数据增强函数的算法。PBA 可在计算量少一千倍的情况下，达到 CIFAR 上最先进的结果。
- `Kakao 的 Fast AutoAugment <https://github.com/kakaobrain/fast-autoaugment>`_: Fast AutoAugment「已在 NeurIPS 2019 上接受」使用基于密度匹配的更有效的搜索策略来学习增强策略。
- `Allentune <https://github.com/allenai/allentune>`_: 来自 AllenAI 的 AllenNLP 超参数搜索。
- `machinable <https://github.com/frthjf/machinable>`_: 用于机器学习研究的模块化配置系统。请参阅 `machinable.org <https://machinable.org>`_。
- `NeuroCard <https://github.com/neurocard/neurocard>`_: NeuroCard「已在 VLDB 2021 上被接受」是一种用于多表连接查询的神经基数估计器。它使用最先进的深度密度模型来学习关系数据库表之间的相关性。



了解有关 Ray Tune 的更多信息
-------------------------

您可以在下面找到有关 Ray Tune 的博客文章和讨论：

- [博客] `Tune：用于在任何规模上快速调整超参数的 Python 库 <https://towardsdatascience.com/fast-hyperparameter-tuning-at-scale-d428223b081c>`_
- [博客] `使用 Ray Tune 进行前沿超参数调整 <https://medium.com/riselab/cutting-edge-hyperparameter-tuning-with-ray-tune-be6c0447afdf>`_
- [博客] `使用 Ray Tune 在 TensorFlow 中进行简单的超参数和架构搜索 <http://louiskirsch.com/ai/ray-tune>`_
- [幻灯片] `在 RISECamp 2019 上的演讲 <https://docs.google.com/presentation/d/1v3IldXWrFNMK-vuONlSdEuM82fuGTrNUDuwtfx4axsQ/edit?usp=sharing>`_
- [视频] `在 RISECamp 2018 上的演讲 <https://www.youtube.com/watch?v=38Yd_dXW51Q>`_
- [视频] `现代超参数优化指南 「PyData LA 2019」 <https://www.youtube.com/watch?v=10uz5U3Gy6E>`_ (`幻灯片 <https://speakerdeck.com/richardliaw/a-modern-guide-to-hyperparameter-optimization>`_)

引用 Tune
-----------

如果 Tune 对您的学术研究有帮助，我们鼓励您引用 `我们的论文 <https://arxiv.org/abs/1807.05118>`__。
以下是 bibtex 示例：

.. code-block:: tex

    @article{liaw2018tune,
        title={Tune: A Research Platform for Distributed Model Selection and Training},
        author={Liaw, Richard and Liang, Eric and Nishihara, Robert
                and Moritz, Philipp and Gonzalez, Joseph E and Stoica, Ion},
        journal={arXiv preprint arXiv:1807.05118},
        year={2018}
    }
