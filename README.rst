.. image:: https://github.com/ray-project/ray/raw/master/doc/source/images/ray_header_logo.png

.. image:: https://readthedocs.org/projects/ray/badge/?version=master
    :target: http://docs.ray.io/en/master/?badge=master

.. image:: https://img.shields.io/badge/Ray-Join%20Slack-blue
    :target: https://forms.gle/9TSdDYUgxYs8SA9e8

.. image:: https://img.shields.io/badge/Discuss-Ask%20Questions-blue
    :target: https://discuss.ray.io/

.. image:: https://img.shields.io/twitter/follow/raydistributed.svg?style=social&logo=twitter
    :target: https://twitter.com/raydistributed

|

Ray 是一个统一的框架，用于扩展 AI 和 Python 应用程序。Ray 由一个核心分布式运行时和一组用于简化 ML 计算的 AI 库组成：

.. image:: https://github.com/ray-project/ray/raw/master/doc/source/images/what-is-ray-padded.svg

..
  https://docs.google.com/drawings/d/1Pl8aCYOsZCo61cmp57c7Sja6HhIygGCvSZLi_AuBuqo/edit

学习更多 `Ray AI 类库`_ :

- `Data`_: ML 可扩展数据集
- `Train`_: 分布式训练
- `Tune`_: 可扩展超参转换
- `RLlib`_: 可扩展的强化学习
- `Serve`_: 可扩展及可编程服务

或者更多关于 `Ray Core`_ 及其关键抽象

- `Tasks`_: 在集群执行的无状态函数。
- `Actors`_: 在集群中创建的有状态工作进程。
- `Objects`_: 跨集群可访问的不可变值。

使用 `Ray 看板 <https://docs.ray.io/en/latest/ray-core/ray-dashboard.html>`__ 监控并调试 Ray 应用。

Ray 可运行在任何机器，集群，云上，Kubernetes，以及具有不断发展的
`社区集成生态系统`__.

使用： ``pip install ray`` 安装 Ray。对于每日版本，查看
`安装页 <https://docs.ray.io/en/latest/installation.html>`__.

.. _`Serve`: https://docs.ray.io/en/latest/serve/index.html
.. _`Data`: https://docs.ray.io/en/latest/data/dataset.html
.. _`Workflow`: https://docs.ray.io/en/latest/workflows/concepts.html
.. _`Train`: https://docs.ray.io/en/latest/train/train.html
.. _`Tune`: https://docs.ray.io/en/latest/tune/index.html
.. _`RLlib`: https://docs.ray.io/en/latest/rllib/index.html
.. _`ecosystem of community integrations`: https://docs.ray.io/en/latest/ray-overview/ray-libraries.html


为什么是 Ray？
--------

当今的机器学习工作负载的计算密集程度越来越高。 尽管笔记本电脑等单节点开发环境很方便，但无法扩展以满足这些需求。

Ray 是一种将 Python 和 AI 应用程序从笔记本电脑扩展到集群的统一方法。

借助 Ray，您可以将相同的代码从笔记本电脑无缝扩展到集群。 Ray 被设计为通用型，这意味着它可以高效地运行任何类型的工作负载。 如果您的应用程序是用 Python 编写的，您可以使用 Ray 对其进行扩展，无需其他基础设施。

更多信息
----------------

- `文档`_
- `Ray 架构白皮书`_
- `Exoshuffle: Ray 中的大规模数据 shuffle`_
- `Ownership: 用于细粒度任务的分布式期货系统`_
- `RLlib 论文`_
- `Tune 论文`_

*老文档：*

- `Ray 论文`_
- `Ray HotOS 论文`_
- `Ray v1 架构白皮书`_

.. _`Ray AI Libraries`: https://docs.ray.io/en/latest/ray-air/getting-started.html
.. _`Ray Core`: https://docs.ray.io/en/latest/ray-core/walkthrough.html
.. _`Tasks`: https://docs.ray.io/en/latest/ray-core/tasks.html
.. _`Actors`: https://docs.ray.io/en/latest/ray-core/actors.html
.. _`Objects`: https://docs.ray.io/en/latest/ray-core/objects.html
.. _`Documentation`: http://docs.ray.io/en/latest/index.html
.. _`Ray Architecture v1 whitepaper`: https://docs.google.com/document/d/1lAy0Owi-vPz2jEqBSaHNQcy2IBSDEHyXNOQZlGuj93c/preview
.. _`Ray Architecture whitepaper`: https://docs.google.com/document/d/1tBw9A4j62ruI5omIJbMxly-la5w4q_TjyJgJL_jN2fI/preview
.. _`Exoshuffle: large-scale data shuffle in Ray`: https://arxiv.org/abs/2203.05072
.. _`Ownership: a distributed futures system for fine-grained tasks`: https://www.usenix.org/system/files/nsdi21-wang.pdf
.. _`Ray paper`: https://arxiv.org/abs/1712.05889
.. _`Ray HotOS paper`: https://arxiv.org/abs/1703.03924
.. _`RLlib paper`: https://arxiv.org/abs/1712.09381
.. _`Tune paper`: https://arxiv.org/abs/1807.05118

深入
----------------

.. list-table::
   :widths: 25 50 25 25
   :header-rows: 1

   * - 平台
     - 目的
     - 预计响应时间
     - 支持水平
   * - `Discourse 论坛`_
     - 用于有关开发的讨论和有关使用的问题。
     - < 1 day
     - Community
   * - `GitHub Issues`_
     - 用于报告错误和提交功能请求。
     - < 2 days
     - Ray OSS Team
   * - `Slack`_
     - 用于与其他 Ray 用户协作。
     - < 2 days
     - Community
   * - `StackOverflow`_
     - 用于询问有关如何使用 Ray 的问题。
     - 3-5 days
     - Community
   * - `聚会小组`_
     - 用于了解 Ray 项目和最佳实践。
     - Monthly
     - Ray DevRel
   * - `Twitter`_
     - 用于及时了解新功能。
     - Daily
     - Ray DevRel

.. _`Discourse 论坛`: https://discuss.ray.io/
.. _`GitHub 讨论`: https://github.com/ray-project/ray/issues
.. _`StackOverflow`: https://stackoverflow.com/questions/tagged/ray
.. _`聚会小组`: https://www.meetup.com/Bay-Area-Ray-Meetup/
.. _`Twitter`: https://twitter.com/raydistributed
.. _`Slack`: https://forms.gle/9TSdDYUgxYs8SA9e8

