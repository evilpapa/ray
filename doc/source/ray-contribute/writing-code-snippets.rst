.. _writing-code-snippets_ref:

==========================
如何编写代码片段
==========================

用户通过示例学习。因此，无论您是编写文档字符串还是用户指南，
都应包含说明相关 API 的示例。
您的示例应该可以直接运行，以便用户可以复制并根据自己的需求进行调整。

本页描述了如何编写代码片段以便在 CI 中进行测试。

.. note::
    本指南中的示例使用 reStructuredText。如果您
    正在编写 Markdown，请使用 MyST 语法。
    要了解更多信息，请阅读
    `MyST 文档 <https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html#directives-a-block-level-extension-point>`_.

-----------------
示例类型
-----------------

有三种类型的例子： *doctest-style*, *code-output-style*, 和 *literalinclude*.

*doctest-style* 示例
========================

*doctest-style* 样式的示例模拟交互式 Python 会话。 ::

    .. doctest::

        >>> def is_even(x):
        ...     return (x % 2) == 0
        >>> is_even(0)
        True
        >>> is_even(1)
        False

它们的渲染如下：

.. doctest::

    >>> def is_even(x):
    ...     return (x % 2) == 0
    >>> is_even(0)
    True
    >>> is_even(1)
    False

.. tip::

    如果您正在编写文档字符串，请排除 `.. doctest::` 以简化您的代码。 ::

        Example:
            >>> def is_even(x):
            ...     return (x % 2) == 0
            >>> is_even(0)
            True
            >>> is_even(1)
            False

*code-output-style* 示例
============================

*code-output-style* 示例包含普通的 Python 代码。 ::

    .. testcode::

        def is_even(x):
            return (x % 2) == 0

        print(is_even(0))
        print(is_even(1))

    .. testoutput::

        True
        False

它们的渲染如下：

.. testcode::

    def is_even(x):
        return (x % 2) == 0

    print(is_even(0))
    print(is_even(1))

.. testoutput::

    True
    False

*literalinclude* 示例
=========================

*literalinclude* 示例显示 Python 模块。 ::

    .. literalinclude:: ./doc_code/example_module.py
        :language: python
        :start-after: __is_even_begin__
        :end-before: __is_even_end__

.. literalinclude:: ./doc_code/example_module.py
    :language: python

它们的渲染如下：

.. literalinclude:: ./doc_code/example_module.py
    :language: python
    :start-after: __is_even_begin__
    :end-before: __is_even_end__

---------------------------------------
你应该写哪种类型的例子？
---------------------------------------

对于应该使用哪种风格，并没有硬性规定。选择
最能体现你的 API 的风格。

.. tip::
    如果您不确定使用哪种样式，请使用 *code-block-style*。

何时使用 *doctest-style*
===========================

如果您正在编写一个强调对象表示的小示例，或者
想要打印中间对象，请使用 *doctest-style*. ::

    .. doctest::

        >>> import ray
        >>> ds = ray.data.range(100)
        >>> ds.schema()
        Column  Type
        ------  ----
        id      int64
        >>> ds.take(5)
        [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]

何时使用 *code-block-style*
==============================

如果您正在编写更长的示例，或者对象表示与您的示例不相关，请使用 *code-block-style*. ::

    .. testcode::

        from typing import Dict
        import numpy as np
        import ray

        ds = ray.data.read_csv("s3://anonymous@air-example-data/iris.csv")

        # Compute a "petal area" attribute.
        def transform_batch(batch: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
            vec_a = batch["petal length (cm)"]
            vec_b = batch["petal width (cm)"]
            batch["petal area (cm^2)"] = vec_a * vec_b
            return batch

        transformed_ds = ds.map_batches(transform_batch)
        print(transformed_ds.materialize())

    .. testoutput::

        MaterializedDataset(
           num_blocks=...,
           num_rows=150,
           schema={
              sepal length (cm): double,
              sepal width (cm): double,
              petal length (cm): double,
              petal width (cm): double,
              target: int64,
              petal area (cm^2): double
           }
        )

何时使用 *literalinclude*
============================
如果您正在编写端到端示例并且您的示例不包含输出，请使用
*literalinclude*.

-----------------------------------
如何处理难以测试的示例？
-----------------------------------

什么时候可以不测试示例？
=======================================

您不需要测试依赖于外部系统（如权重和偏差）的示例。

跳过 *doctest-style* 示例
=================================

要跳过 *doctest-style* 示例，请将 `# doctest: +SKIP` 附加到你的 Python 代码中。 ::

    .. doctest::

        >>> import ray
        >>> ray.data.read_images("s3://private-bucket")  # doctest: +SKIP

跳过 *code-block-style* 示例
====================================

要跳过 *code-block-style* 示例，请将 `:skipif: True` 添加到 `testoutput` 代码块。 ::

    .. testcode::
        :skipif: True

        from ray.air.integrations.wandb import WandbLoggerCallback
        callback = WandbLoggerCallback(
            project="Optimization_Project",
            api_key_file=...,
            log_config=True
        )

----------------------------------------------
如何处理长输出或非确定性输出
----------------------------------------------

如果您的 Python 代码是不确定的，或者您的输出过长，您可能需要跳过全部或部分输出。

忽略 *doctest-style* 输出
================================

要忽略 *doctest-style* 的部分输出，请用省略号替换有问题的部分。 ::

    >>> import ray
    >>> ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")
    Dataset(
       num_blocks=...,
       num_rows=...,
       schema={image: numpy.ndarray(shape=(32, 32, 3), dtype=uint8)}
    )

要完全忽略输出，请编写 *code-block-style* 代码块。不要使用 `# doctest: +SKIP`。

忽略 *code-block-style* 输出
===================================

如果输出的某些部分很长或者不确定，请用省略号
替换有问题的部分。 ::

    .. testcode::

        import ray
        ds = ray.data.read_images("s3://anonymous@ray-example-data/image-datasets/simple")
        print(ds)

    .. testoutput::

        Dataset(
           num_blocks=...,
           num_rows=...,
           schema={image: numpy.ndarray(shape=(32, 32, 3), dtype=uint8)}
        )

如果您的输出是不确定的并且您想要显示示例输出，请添加
`:options: +MOCK`。 ::

    .. testcode::

        import random
        print(random.random())

    .. testoutput::
        :options: +MOCK

        0.969461416250246

如果您的输出难以测试并且您不想显示示例输出，请排除
``testoutput``. ::

    .. testcode::

        print("This output is hidden and untested")


------------------------------
如何使用 GPU 测试示例
------------------------------

要配置 Bazel 以使用 GPU 运行示例，请完成以下步骤：

#. 打开相应的 ``BUILD`` 文件。 如果您的示例在 ``doc/`` 文件夹，
   打开 ``doc/BUILD``。如果您的示例在 ``python/`` 文件夹，打开
   ``python/ray/train/BUILD``。

#. 找到 ``doctest`` 规则。它看起来像这样： ::

    doctest(
        files = glob(
            include=["source/**/*.rst"],
        ),
        size = "large",
        tags = ["team:none"]
    )

#. 将包含示例的文件添加到排除文件列表中。 ::

    doctest(
        files = glob(
            include=["source/**/*.rst"],
            exclude=["source/data/requires-gpus.rst"]
        ),
        tags = ["team:none"]
    )

#. 如果尚不存在，请创建一个设置 ``gpu`` 为 ``True`` 的 ``doctest`` 规则。 ::

    doctest(
        files = [],
        tags = ["team:none"],
        gpu = True
    )

#. 将包含示例的文件添加到 GPU 规则。 ::

    doctest(
        files = ["source/data/requires-gpus.rst"]
        size = "large",
        tags = ["team:none"],
        gpu = True
    )

有关实际示例，请参见 ``doc/BUILD`` 或者 ``python/ray/train/BUILD``。

----------------------------
如何本地测试示例
----------------------------

要在本地测试示例，请安装 Ray fork `pytest-sphinx`。

.. code-block:: bash

    pip install git+https://github.com/ray-project/pytest-sphinx

然后，在模块、文档字符串或用户指南上运行 pytest。

.. code-block:: bash

    pytest --doctest-modules python/ray/data/read_api.py
    pytest --doctest-modules python/ray/data/read_api.py::ray.data.read_api.range
    pytest --doctest-modules doc/source/data/getting-started.rst
