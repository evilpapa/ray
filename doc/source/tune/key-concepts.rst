.. _tune-60-seconds:

========================
Ray Tune 关键概念
========================

.. TODO: should we introduce checkpoints as well?
.. TODO: should we at least mention "Stopper" classes here?

让我们快速了解一下使用 Tune 所需了解的关键概念。
如果您想立即查看实用教程，请访问我们的 :ref:`用户指南 <tune-guides>`。
实际上，Tune 有六个您需要了解的关键组件。

首先，在 `搜索空间` 中定义你调整的超参数，并将它们传递到要调整的 `trainable` 对象中。
然后选择一个 `搜索算法` 来有效优化参数，并可选择
使用 `scheduler` 来提前停止搜索并加快实验速度。
与其他配置一起， 你的 `trainable` 、搜索算法和调度程序被传递到  ``Tuner`` ，它将创建并运行您的  `trials`。
`Tuner`  返回 `ResultGrid` 以检查您的实验结果。
下图显示了这些组件的概述，我们将在下一节中详细介绍。

.. image:: images/tune_flow.png

.. _tune_60_seconds_trainables:

Ray Tune 可训练项
-------------------

简而言之， :ref:`Trainable <trainable-docs>` 是可以传递到 Tune 运行的对象。
Ray Tune 有两种定义 `trainable` 的方法，即， :ref:`函数 API <tune-function-api>`
和 :ref:`类 API <tune-class-api>`。
两者都是定义 `trainable` 的有效方法，但通常建议使用 Function API，
并在本指南的其余部分中使用。

假设我们要优化一个简单的目标函数 ``a (x ** 2) + b`` ，如其中 ``a`` 和 ``b`` 是我们要调整目标  `minimize`  的超参数。
由于目标也有一个变量 ``x``，我们需要测试 ``x`` 不同的值。
给定的 ``a``、 ``b`` 和 ``x``具体的选择，我们可以评估目标函数并得到最小化 `score` 。

.. tab-set::

    .. tab-item:: 函数 API

        使用 :ref:`基于函数的 API <tune-function-api>` ，您可以创建一个函数（此处称为 ``trainable``），
        该函数接受超参数字典。
        此函数在“训练循环”中计算  ``score`` 值，并 `reports` 分数给 Tune：

        .. literalinclude:: doc_code/key_concepts.py
            :language: python
            :start-after: __function_api_start__
            :end-before: __function_api_end__

        注意，我们使用 ``session.report(...)`` 来报告训练循环中的中间结果 ``score`` ，
        这在许多机器学习任务中都很有用。
        如果您只想报告此循环之外的最终结果 ``score``， 则只需使用在结尾使用 ``return {"score": score}`` 返回 ``trainable`` 函数的分数。
        你也可以使用 ``yield {"score": score}`` 代替  ``session.report()``。

    .. tab-item:: 类 API

        以下是使用 :ref:`基于类的 API <tune-class-api>` 指定目标函数的示例：

        .. literalinclude:: doc_code/key_concepts.py
            :language: python
            :start-after: __class_api_start__
            :end-before: __class_api_end__

        .. tip:: ``session.report`` 不能在 ``Trainable`` 类上使用。

在此处了解有关 :ref:`Trainables here <trainable-docs>` 的详细信息，
并 :ref:`查看我们的示例 <tune-general-examples>`。
接下来，让我们仔细看看你传到 trainable 的 ``config`` 字典。

.. _tune-key-concepts-search-spaces:

调整搜索空间
------------------

为了优化 *超参数*，你必须定义一个 *搜索空间*。
搜索空间定义超参数的有效值，并可以指定如何
对这些值进行采样（例如从均匀分布或正态分布中采样）。



Tune 提供各种函数来定义搜索空间和采样方法。
:ref:`您可以在此处找到这些搜索空间定义的文档 <tune-search-space>`。

以下是涵盖所有搜索空间函数的示例。再次重申，
:ref:`以下是所有这些函数的完整解释 <tune-search-space>`。

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __config_start__
    :end-before: __config_end__

.. _tune_60_seconds_trials:

调优试验
-----------

您使用 :ref:`Tuner.fit <tune-run-ref>` 来执行和管理超参数调整并生成您的 `trials`。
至少，您的 ``Tuner`` 调用将接受一个 trainable 作为第一个参数，以及一个 ``param_space`` 字典
来定义搜索空间。

``Tuner.fit()`` 函数还提供了许多功能，例如 :ref:`日志记录 <tune-logging>`、
:ref:`检查点 <tune-trial-checkpoint>`、和 :ref:`早起停止 <tune-stopping-ref>`。
在最小化的示例 ``a (x ** 2) + b`` 中，一个简单的 Tune 运行，具有 ``a`` 和 ``b`` 的简单搜索空间，
如下所示：

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __run_tunable_start__
    :end-before: __run_tunable_end__

``Tuner.fit`` 将从其参数中生成几个超参数配置，并将它们包装到
:ref:`Trial 对象 <trial-docstring>` 中。

试验包含大量信息。
例如，您可以使用 ( ``trial.config``)、试验 ID (``trial.trial_id``），
试验的资源规范 (``resources_per_trial`` 或 ``trial.placement_group_factory``) 以及许多其他值来获取超参数配置。

默认的， ``Tuner.fit`` 将执行直到所有试验停止或出错。
以下是试运行的示例输出：

.. TODO: how to make sure this doesn't get outdated?
.. code-block:: bash

    == Status ==
    Memory usage on this node: 11.4/16.0 GiB
    Using FIFO scheduling algorithm.
    Resources requested: 1/12 CPUs, 0/0 GPUs, 0.0/3.17 GiB heap, 0.0/1.07 GiB objects
    Result logdir: /Users/foo/ray_results/myexp
    Number of trials: 1 (1 RUNNING)
    +----------------------+----------+---------------------+-----------+--------+--------+----------------+-------+
    | Trial name           | status   | loc                 |         a |      b |  score | total time (s) |  iter |
    |----------------------+----------+---------------------+-----------+--------+--------+----------------+-------|
    | Trainable_a826033a | RUNNING  | 10.234.98.164:31115 | 0.303706  | 0.0761 | 0.1289 |        7.54952 |    15 |
    +----------------------+----------+---------------------+-----------+--------+--------+----------------+-------+


您还可以通过指定样本数量（ ``num_samples`` ）轻松运行 10 次试验。
Tune 会自动 :ref:`确定将并行运行多少次试验 <tune-parallelism>`。
请注意，除了样本数量的设置，如果你设置了 ``num_samples=-1``， 
你也可以通过  ``time_budget_s`` （以秒为单位）指定时间预算。

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __run_tunable_samples_start__
    :end-before: __run_tunable_samples_end__


最后，你可以通过 Tune 的 :ref:`搜索空间 API API <tune-default-search-space>` 使用更有趣的搜索空间来优化超参数，
例如使用随机样本或网格搜索。
以下是 ``a`` 和 ``b`` 在 ``[0, 1]`` 之间均匀采样的示例：

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __search_space_start__
    :end-before: __search_space_end__

要了解有关配置 Tune 运行的各种方法的更多信息，
查看 :ref:`Tuner API 参考 <tune-run-ref>`。

.. _search-alg-ref:

调整搜索算法
----------------------

为了优化训练过程的超参数，您可以使用
:ref:`搜索算法 <tune-search-alg>` 来建议超参数配置。
如果您未指定搜索算法，Tune 将默认使用随机搜索，这可以
为您的超参数优化提供一个良好的起点。

例如，要通过 ``bayesian-optimization`` 包使用 Tune 进行简单的贝叶斯优化（请确保首先运行 ``pip install bayesian-optimization`` ），
我们可以定义一个使用 ``BayesOptSearch`` 的  ``algo`` 。
只需将其通过一个 ``search_alg`` 参数传递给 ``tune.TuneConfig``，该参数由 ``Tuner`` 接收：

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __bayes_start__
    :end-before: __bayes_end__

Tune 具有与许多流行的 **优化** 库集成的搜索算法，
例如 :ref:`Nevergrad <nevergrad>`、 :ref:`HyperOpt <tune-hyperopt>` 或 :ref:`Optuna <tune-optuna>`。
 Tune 会自动将提供的搜索空间转换为
 搜索算法和底层库期望的搜索空间。
有关更多详细信息，请参阅 :ref:`搜索算法 API 文档 <tune-search-alg>` 。

以下是 Tune 中所有可用搜索算法的概述：

.. list-table::
   :widths: 5 5 2 10
   :header-rows: 1

   * - SearchAlgorithm
     - 概括
     - 网站
     - 代码示例
   * - :ref:`Random search/grid search <tune-basicvariant>`
     - 随机搜索/网格搜索
     -
     - :doc:`/tune/examples/includes/tune_basic_example`
   * - :ref:`AxSearch <tune-ax>`
     - 贝叶斯/赌博机优化
     - [`Ax <https://ax.dev/>`__]
     - :doc:`/tune/examples/includes/ax_example`
   * - :ref:`BlendSearch <BlendSearch>`
     - 混合搜索
     - [`Bs <https://github.com/microsoft/FLAML/tree/main/flaml/tune>`__]
     - :doc:`/tune/examples/includes/blendsearch_example`
   * - :ref:`CFO <CFO>`
     - 低成本超参数优化
     - [`Cfo <https://github.com/microsoft/FLAML/tree/main/flaml/tune>`__]
     - :doc:`/tune/examples/includes/cfo_example`
   * - :ref:`DragonflySearch <Dragonfly>`
     - 可扩展贝叶斯优化
     - [`Dragonfly <https://dragonfly-opt.readthedocs.io/>`__]
     - :doc:`/tune/examples/includes/dragonfly_example`
   * - :ref:`HyperOptSearch <tune-hyperopt>`
     - Tree-Parzen 估计量
     - [`HyperOpt <http://hyperopt.github.io/hyperopt>`__]
     - :doc:`/tune/examples/hyperopt_example`
   * - :ref:`BayesOptSearch <bayesopt>`
     - 贝叶斯优化
     - [`BayesianOptimization <https://github.com/fmfn/BayesianOptimization>`__]
     - :doc:`/tune/examples/includes/bayesopt_example`
   * - :ref:`TuneBOHB <suggest-TuneBOHB>`
     - Bayesian Opt/HyperBand
     - [`BOHB <https://github.com/automl/HpBandSter>`__]
     - :doc:`/tune/examples/includes/bohb_example`
   * - :ref:`NevergradSearch <nevergrad>`
     - 无梯度优化
     - [`Nevergrad <https://github.com/facebookresearch/nevergrad>`__]
     - :doc:`/tune/examples/includes/nevergrad_example`
   * - :ref:`OptunaSearch <tune-optuna>`
     - Optuna 搜索算法
     - [`Optuna <https://optuna.org/>`__]
     - :doc:`/tune/examples/optuna_example`
   * - :ref:`SigOptSearch <sigopt>`
     - 闭源
     - [`SigOpt <https://sigopt.com/>`__]
     - :doc:`/tune/examples/includes/sigopt_example`

.. note:: 不同 :ref:`Tune 的试验调度程序 <tune-schedulers>` 不同，
    Tune 搜索算法不能影响或停止训练过程。
    但是，你可以将它们一起使用，以尽早停止对不良试验的评估。

如果您想实现自己的搜索算法，该界面很容易实现，
您可以 :ref:`阅读此处的说明 <byo-algo>`。

Tune 还提供了与搜索算法一起使用的有用实用程序：

 * :ref:`repeater`: 支持使用多个随机种子运行每个 *采样超参数* 。
 * :ref:`limiter`: 限制运行优化时并发试验的次数。
 * :ref:`shim`: 允许根据给定的字符串创建搜索算法对象。

请注意，在上面的例子中，我们告诉 Tune 在 ``20`` 次训练迭代后 ``stop``。
这种使用明确规则停止试验的方法很有用，但在许多情况下，我们可以使用 `schedulers` 做得更好。

.. _schedulers-ref:

调整调度
---------------

为了提高训练过程的效率，您可以使用 :ref:`Trial Scheduler <tune-schedulers>`。
For instance, in our ``trainable`` example minimizing a function in a training loop, we used ``session.report()``.
This reported `incremental` results, given a hyperparameter configuration selected by a search algorithm.
Based on these reported results, a Tune scheduler can decide whether to stop the trial early or not.
If you don't specify a scheduler, Tune will use a first-in-first-out (FIFO) scheduler by default, which simply
passes through the trials selected by your search algorithm in the order they were picked and does not perform any early stopping.

In short, schedulers can stop, pause, or tweak the
hyperparameters of running trials, potentially making your hyperparameter tuning process much faster.
Unlike search algorithms, :ref:`Trial Scheduler <tune-schedulers>` do not select which hyperparameter
configurations to evaluate.

Here's a quick example of using the so-called ``HyperBand`` scheduler to tune an experiment.
All schedulers take in a ``metric``, which is the value reported by your trainable.
The ``metric`` is then maximized or minimized according to the ``mode`` you provide.
To use a scheduler, just pass in a ``scheduler`` argument to ``tune.TuneConfig``, which is taken in by ``Tuner``:

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __hyperband_start__
    :end-before: __hyperband_end__


Tune includes distributed implementations of early stopping algorithms such as
`Median Stopping Rule <https://research.google.com/pubs/pub46180.html>`__, `HyperBand <https://arxiv.org/abs/1603.06560>`__,
and `ASHA <https://openreview.net/forum?id=S1Y7OOlRZ>`__.
Tune also includes a distributed implementation of `Population Based Training (PBT) <https://www.deepmind.com/blog/population-based-training-of-neural-networks>`__
and `Population Based Bandits (PB2) <https://arxiv.org/abs/2002.02518>`__.

.. tip:: The easiest scheduler to start with is the ``ASHAScheduler`` which will aggressively terminate low-performing trials.

When using schedulers, you may face compatibility issues, as shown in the below compatibility matrix.
Certain schedulers cannot be used with search algorithms,
and certain schedulers require that you implement :ref:`checkpointing <tune-trial-checkpoint>`.

Schedulers can dynamically change trial resource requirements during tuning.
This is implemented in :ref:`ResourceChangingScheduler<tune-resource-changing-scheduler>`,
which can wrap around any other scheduler.

.. list-table:: Scheduler Compatibility Matrix
   :header-rows: 1

   * - Scheduler
     - Need Checkpointing?
     - SearchAlg Compatible?
     - Example
   * - :ref:`ASHA <tune-scheduler-hyperband>`
     - No
     - Yes
     - :doc:`Link </tune/examples/includes/async_hyperband_example>`
   * - :ref:`Median Stopping Rule <tune-scheduler-msr>`
     - No
     - Yes
     - :ref:`Link <tune-scheduler-msr>`
   * - :ref:`HyperBand <tune-original-hyperband>`
     - Yes
     - Yes
     - :doc:`Link </tune/examples/includes/hyperband_example>`
   * - :ref:`BOHB <tune-scheduler-bohb>`
     - Yes
     - Only TuneBOHB
     - :doc:`Link </tune/examples/includes/bohb_example>`
   * - :ref:`Population Based Training <tune-scheduler-pbt>`
     - Yes
     - Not Compatible
     - :doc:`Link </tune/examples/includes/pbt_function>`
   * - :ref:`Population Based Bandits <tune-scheduler-pb2>`
     - Yes
     - Not Compatible
     - :doc:`Basic Example </tune/examples/includes/pb2_example>`, :doc:`PPO example </tune/examples/includes/pb2_ppo_example>`

Learn more about trial schedulers in :ref:`the scheduler API documentation <schedulers-ref>`.

.. _tune-concepts-analysis:

Tune ResultGrid
---------------

``Tuner.fit()`` returns an :ref:`ResultGrid <tune-analysis-docs>` object which has methods you can use for
analyzing your training.
The following example shows you how to access various metrics from an ``ResultGrid`` object, like the best available
trial, or the best hyperparameter configuration for that trial:

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __analysis_start__
    :end-before: __analysis_end__

This object can also retrieve all training runs as dataframes,
allowing you to do ad-hoc data analysis over your results.

.. literalinclude:: doc_code/key_concepts.py
    :language: python
    :start-after: __results_start__
    :end-before: __results_end__

See the :ref:`result analysis user guide <tune-analysis-guide>` for more usage examples.

What's Next?
-------------

Now that you have a working understanding of Tune, check out:

* :ref:`tune-guides`: Tutorials for using Tune with your preferred machine learning library.
* :doc:`/tune/examples/index`: End-to-end examples and templates for using Tune with your preferred machine learning library.
* :doc:`/tune/getting-started`: A simple tutorial that walks you through the process of setting up a Tune experiment.


Further Questions or Issues?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: /_includes/_help.rst
