.. include:: /_includes/_latest_contribution_doc.rst

.. _getting-involved:

参与/贡献
===============================


.. toctree::
    :hidden:

    development
    docs
    writing-code-snippets
    fake-autoscaler
    ../ray-core/examples/testing-tips
    debugging
    profiling

Ray 不仅仅是一个分布式应用程序的框架，它还是一个由
开发人员、研究人员和热爱机器学习的人们组成的活跃社区。

.. tip:: `在我们的论坛 <https://discuss.ray.io/>`_提问！ 
  社区非常活跃，致力于帮助人们成功构建他们的 Ray 应用程序。

您可以在 `GitHub`_` 上加入我们「并加星标！」 。

.. _`GitHub`: https://github.com/ray-project/ray

贡献给 Ray
-------------------

我们欢迎「并鼓励！」对 Ray 的所有形式的贡献，包括但不限于：

- 补丁和 PR 的代码审查。
- 推送补丁。
- 文档和示例。
- 参与论坛社区和问题讨论。
- 代码可读性并通过代码注释来提高可读性。
- 测试用例使代码库更加健壮。
- 教程、博客文章、推广项目的演讲。
- 通过 Ray 增强提案 (REP) 实现的功能和主要变化： https://github.com/ray-project/enhancements

我可以做什么？
-------------------

我们使用 Github 来跟踪问题、功能请求和错误。请查看标记为
`"good first issue" <https://github.com/ray-project/ray/issues?utf8=%E2%9C%93&q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`__ 作为起点。

设置你的开发环境
---------------------------------------

要编辑 Ray 源代码，您需要签出存储库并从源代码构建 Ray。 按照 :ref:`这些说明构建 <building-ray>` Ray 的本地副本以轻松进行更改。

提交并合并贡献
-------------------------------------

合并贡献有几个步骤。

1. 首先将最新版本的 master 合并到您的开发分支中。

   .. code:: bash

     git remote add upstream https://github.com/ray-project/ray.git
     git pull . upstream/master

2. 确保所有现有 `tests <getting-involved.html#testing>`__ 和 `linters <getting-involved.html#lint-and-formatting>`__ 均已通过。
   运行 ``setup_hooks.sh`` 以创建一个 git hook，它将在推送更改之前运行 linter。
3. 如果引入新功能或修补错误，请确保在 ``ray/python/ray/tests/`` 相关文件中添加新的测试用例。
4. 记录代码。公共函数需要记录，并记得提供使用示例「如果适用」。
   请参阅 ``doc/README.md`` 获取有关编辑和构建公共文档的说明。
5. 处理 PR 上的评论。在审核过程中，
   您可能需要解决与其他更改的合并冲突。要解决合并冲突，
   请在您的分支上运行 ``git pull . upstream/master`` 「请不要使用 rebase，因为
   它对 GitHub 审核工具不太友好。合并时所有提交都将被压缩。」
6. 审阅者将合并并批准拉取请求；如果拉取请求变得陈旧，
   请务必 ping 他们。

PR 审核流程
-----------------

对于 ``ray-project`` 组织内的贡献者：
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- 首次创建 PR 时，请向该 `assignee` 部分添加审阅者。
- 受让人将审查您的 PR ，如果需要进一步操作，请添加添加标签 `@author-action-required` 。
- 解决他们的评论并从 PR 中删除 `@author-action-required` 标签。
- 重复此过程，直到受让人批准您的 PR。
- 一旦 PR 获得批准，作者将负责确保 PR 通过构建。如果构建成功，则添加标签 `test-ok` 。
- 一旦构建通过，提交者将合并 PR。

对于不属于该 ``ray-project`` 组织的贡献者：
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- 您的 PR 很快就会有受让人。PR 的受让人将积极与贡献者合作以合并 PR。
- 请在提出您的评论后主动联系受让人！

测试
-------

尽管我们有钩子可以为每个拉取请求自动运行单元测试，
但我们建议您事先在本地运行单元测试，
以减轻审阅者的负担并加快审阅过程。

如果您是第一次运行测试，可以使用以下命令安装所需的依赖项：

.. code-block:: shell

    pip install -c python/requirements.txt -r python/requirements/test-requirements.txt

Python 开发测试
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

完整的测试套件太大，无法在一台机器上运行。但是，您可以运行单独的相关 Python 测试文件。假设测试集中的某个测试文件「例如 ``python/ray/tests/test_basic.py`` 失败。您可以按如下方式在本地运行该测试文件：

.. code-block:: shell

    # Directly calling `pytest -v ...` may lose import paths.
    python -m pytest -v -s python/ray/tests/test_basic.py

这将运行文件中的所有测试。要运行特定测试，请使用以下命令：

.. code-block:: shell

    # Directly calling `pytest -v ...` may lose import paths.
    python -m pytest -v -s test_file.py::name_of_the_test

针对 C++ 开发进行测试
~~~~~~~~~~~~~~~~~~~~~~~~~~~

要编译并运行所有 C++ 测试，您可以运行：

.. code-block:: shell

 bazel test $(bazel query 'kind(cc_test, ...)')

或者，您也可以运行一个特定的 C++ 测试。您可以使用：

.. code-block:: shell

 bazel test $(bazel query 'kind(cc_test, ...)') --test_filter=ClientConnectionTest --test_output=streamed

代码风格
----------

一般情况下，我们遵循 `Google 代码规范 <https://google.github.io/styleguide/>`__ 来编写 C++ 代码，遵循 `Black 代码风格 <https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html>`__ 来编写 Python 代码。Python 导入遵循 `PEP8 风格 <https://peps.python.org/pep-0008/#imports>`__。然而，代码保持局部一致的风格比严格遵循指南更为重要。如有疑问，请遵循组件的局部代码风格。

对于 Python 文档，我们遵循 `Google pydoc 格式 <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__。以下代码片段演示了规范的 Ray pydoc 格式：

.. testcode::

    def ray_canonical_doc_style(param1: int, param2: str) -> bool:
        """First sentence MUST be inline with the quotes and fit on one line.

        Additional explanatory text can be added in paragraphs such as this one.
        Do not introduce multi-line first sentences.

        Examples:
            .. doctest::

                >>> # Provide code examples for key use cases, as possible.
                >>> ray_canonical_doc_style(41, "hello")
                True

                >>> # A second example.
                >>> ray_canonical_doc_style(72, "goodbye")
                False

        Args:
            param1: The first parameter. Do not include the types in the
                docstring. They should be defined only in the signature.
                Multi-line parameter docs should be indented by four spaces.
            param2: The second parameter.

        Returns:
            The return value. Do not include types here.
        """

.. testcode::

    class RayClass:
        """The summary line for a class docstring should fit on one line.

        Additional explanatory text can be added in paragraphs such as this one.
        Do not introduce multi-line first sentences.

        The __init__ method is documented here in the class level docstring.

        All the public methods and attributes should have docstrings.

        Examples:
            .. testcode::

                obj = RayClass(12, "world")
                obj.increment_attr1()

        Args:
            param1: The first parameter. Do not include the types in the
                docstring. They should be defined only in the signature.
                Multi-line parameter docs should be indented by four spaces.
            param2: The second parameter.
        """

        def __init__(self, param1: int, param2: str):
            #: Public attribute is documented here.
            self.attr1 = param1
            #: Public attribute is documented here.
            self.attr2 = param2

        @property
        def attr3(self) -> str:
            """Public property of the class.

            Properties created with the @property decorator
            should be documented here.
            """
            return "hello"

        def increment_attr1(self) -> None:
            """Class methods are similar to regular functions.

            See above about how to document functions.
            """

            self.attr1 = self.attr1 + 1

有关如何在文档字符串中编写代码片段的更多详细信息，请参阅 :ref:`此内容 <writing-code-snippets_ref>` 。

Lint 和 格式化
~~~~~~~~~~~~~~~~~~~

我们还需要进行合并前的代码格式和 linting 测试。

* 对于 Python 格式化，请首先安装 `依赖项 <https://github.com/ray-project/ray/blob/master/python/requirements/lint-requirements.txt>`_ ：

.. code-block:: shell

  pip install -r python/requirements/lint-requirements.txt

* 如果使用 C++ 进行开发，您将需要 `clang-format <https://www.kernel.org/doc/html/latest/process/clang-format.html>`_ 版本 ``12`` (从 `这里 <http://releases.llvm.org/download.html>`_ 下载此版本的 Clang)

您可以在本地运行以下命令：

.. code-block:: shell

    scripts/format.sh

类似下面的输出表示失败：

.. code-block:: shell

  WARNING: clang-format is not installed!  # This is harmless
  From https://github.com/ray-project/ray
   * branch                master     -> FETCH_HEAD
  python/ray/util/sgd/tf/tf_runner.py:4:1: F401 'numpy as np' imported but unused  # Below is the failure

此外，还有其他格式和语义检查器，用于检查下列组件「未包含在 ``scripts/format.sh``」：

* Python README 格式：

.. code-block:: shell

    cd python
    python setup.py check --restructuredtext --strict --metadata

* Python 和文档禁用词检查

.. code-block:: shell

    ./ci/lint/check-banned-words.sh

* Bazel 格式：

.. code-block:: shell

    ./ci/lint/bazel-format.sh

* clang-tidy 用于 C++ lint，需要安装 ``clang`` 和 ``clang-tidy`` 版本 12 ：

.. code-block:: shell

    ./ci/lint/check-git-clang-tidy-output.sh

您可以运行 ``setup_hooks.sh`` 创建一个 git hook，它将在您推送更改之前运行 linter。

了解 CI 测试作业
--------------------------

一旦使用具有多个 CI 测试作业的 `Buildkite <https://buildkite.com/ray-project/>`_ 打开 PR，
Ray 项目就会自动运行持续集成 (CI) 测试。

`CI`_ 测试文件夹包含所有集成测试脚本，
它们通过基于 ``pytest``, ``bazel`` 基准测试和其他 bash 测试脚本。
一些示例包括： 

* Raylet 集成测试命令：
    * ``bazel test //:core_worker_test``

* Bazel 测试命令：
    * ``bazel test --build_tests_only //:all``

* Ray 服务测试命令：
    * ``pytest python/ray/serve/tests``
    * ``python python/ray/serve/examples/echo_full.py``

如果 CI 构建异常似乎与您的更改无关，
请访问 `此链接 <https://flakey-tests.ray.io/>`_ 
检查已知不可靠的最新测试。

.. _`CI`: https://github.com/ray-project/ray/tree/master/ci


API 兼容性样式指南
-----------------------------

Ray 为 Ray 核心和库中的公共 API 提供稳定性保证，这些保证在 :ref:`API 稳定性指南 <api-stability>` 有描述。

很难将 API 兼容性的语义完全捕获到单个注释中「例如，公共 API 可能具有 “实验性” 参数」。对于更细粒度的稳定性合同，可以在 pydoc 中注明「例如，“该 ``random_shuffle`` 选项是实验性的”」。 如果可能，实验性参数也应在 Python 中以下划线为前缀「例如， `_owner=`」。

**其他建议**:

在 Python API 中，考虑强制使用 kwargs 而不是位置参数「使用 ``*`` 运算符」。与位置参数相比，kwargs 更容易保持向后兼容，例如，想象一下，如果您需要在下面弃用“opt1”，那么强制使用 kwargs 会更容易：

.. code-block:: python

    def foo_bar(file, *, opt1=x, opt2=y)
        pass

对于回调 API，考虑添加一个 ``**kwargs`` 占位符作为“前向兼容占位符”，以防将来需要将更多参数传递给回调，例如：

.. code-block:: python

    def tune_user_callback(model, score, **future_kwargs):
        pass



成为审阅者
-------------------

我们从活跃贡献者中识别审阅者。审阅者是不仅积极为项目做出贡献，
而且愿意参与新贡献的代码审查的个人。
项目的拉取请求必须由至少一名审阅者审阅才能合并。
目前没有正式的流程，
但 Ray 的活跃贡献者将由当前审阅者征集。


更多参与资源
-----------------------------------

.. include:: ../ray-contribute/involvement.rst


.. note::

    这些提示基于 TVM `贡献指南 <https://github.com/dmlc/tvm>`__。
