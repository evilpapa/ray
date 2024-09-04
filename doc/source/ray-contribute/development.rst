.. _building-ray:

从源代码构建 Ray
=========================

对于多数 Ray 用户，通过最新的 wheels 或 pip 包安装 Ray 通常就足够了。然而，你可能想要构建最新的 master 分支。

.. tip::

  如果你只是编辑 Python 文件，避免长时间的构建，可以参考 :ref:`python-develop`。

  如果已经按照 :ref:`python-develop` 中的说明操作，并想要切换到本节的完整构建，请先卸载。

.. contents::
  :local:

克隆仓库
--------------------

要在本地构建 Ray，你需要克隆 Git 仓库，首先在 GitHub 上 fork 仓库。然后你可以将其克隆到你的机器上：

.. tab-set::

    .. tab-item:: Git SSH

        要使用 SSH 克隆仓库，请运行：

        .. code-block:: shell

            git clone git@github.com:[your username]/ray.git

    .. tab-item:: Git HTTPS

        要使用 HTTPS 克隆仓库，请运行：

        .. code-block:: shell

            git clone https://github.com/[your username]/ray.git

然后进入 Ray git 仓库目录：

.. code-block:: shell

    cd ray

接下来确保将你的仓库连接到上游（主项目）Ray 仓库。这样你就可以在提出更改（pull requests）时将你的代码推送到你的仓库，同时也可以从主项目中拉取更新。

.. tab-set::

    .. tab-item:: Git SSH

        通过 SSH 连接你的仓库（默认）运行以下命令：

        .. code-block:: shell

            git remote add upstream git@github.com:ray-project/ray.git

    .. tab-item:: Git HTTPS

        使用 HTTPS 连接你的仓库运行以下命令：

        .. code-block:: shell

            git remote add upstream https://github.com/ray-project/ray.git

每次你想要更新本地版本时，你可以从主仓库拉取更改：

.. code-block:: shell

    # Checkout the local master branch
    git checkout master
    # Pull the latest changes from the main repository
    git pull upstream master

准备 Python 环境
------------------------------

你可能想要使用 Python 的虚拟环境。例如，你可以使用 Anaconda 的 ``conda``：

.. tab-set::

    .. tab-item:: conda

        设置一个名为 ``ray`` 的 ``conda`` 环境：

        .. code-block:: shell

            conda create -c conda-forge python=3.9 -n ray


        激活你的虚拟环境，告诉 shell/terminal 使用这个特定的 Python：

        .. code-block:: shell

            conda activate ray

        你需要在每次启动新的 shell/terminal 时激活虚拟环境来工作在 Ray 上。

    .. tab-item:: venv

        使用 Python 的集成 ``venv`` 模块在当前目录创建一个名为 ``venv`` 的虚拟环境：

        .. code-block:: shell

            python -m venv venv

        者包含一个目录，其中包含项目的本地 Python 使用的所有包。你只需要执行这一步一次。

        激活你的虚拟环境，告诉 shell/terminal 使用这个特定的 Python：

        .. code-block:: shell

            source venv/bin/activate

        你需要在每次启动新的 shell/terminal 时激活虚拟环境来工作在 Ray 上。

        创建一个新的虚拟环境可能会使用较旧版本的 ``pip`` 和 ``wheel``。为了避免安装包时出现问题，请使用模块 ``pip`` 安装 ``pip``（本身）和 ``wheel`` 的最新版本：

        .. code-block:: shell

            python -m pip install --upgrade pip wheel

.. _python-develop:

构建 Ray（仅 Python）
--------------------------

.. note:: 除非另有说明，目录和文件路径都是相对于项目根目录的。

RLlib， Tune， Autoscaler 以及大多数 Python 文件不需要您构建和编译 Ray。按照这些说明在本地开发 Ray 的 Python 文件，而无需构建 Ray。

1. 如上所述，确保您克隆了 Ray 的 git 存储库。

2. 确保如上所述激活 Python（虚拟）环境。

3. 使用 Pip 安装 **最新的 Ray wheels.** 参考 :ref:`install-nightlies` 说明。

.. code-block:: shell

    # 例如，对于 Python 3.8:
    pip install -U https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp38-cp38-manylinux2014_x86_64.whl

4. 用本地的已编辑拷贝版本替换安装包重的 Python 文件。我们提供了一个简单的脚本来帮助你完成操作： ``python python/ray/setup-dev.py``。运行此脚本会移除 ``ray`` pip 包绑定的  ``ray/tune``， ``ray/rllib``， ``ray/autoscaler`` 文件夹 （在其他文件夹），并替换为本地代码链接。这种方法，在你 git 克隆中改变文件会直接影响于你安装的 Ray 的行为。

.. code-block:: shell

    # This replaces `<package path>/site-packages/ray/<package>`
    # with your local `ray/python/ray/<package>`.
    python python/ray/setup-dev.py

.. note:: [高级] 您还可以选择跳过为您选择的目录创建符号链接。

.. code-block:: shell

    # This links all folders except "_private" and "dashboard" without user prompt.
    python setup-dev.py -y --skip _private dashboard

.. warning:: （对于 Ray 或 Ray wheel）如果使用此方法设置你的环境，请不要运行 ``pip uninstall ray`` 或 ``pip install -U`` 。要卸载或者升级，你首先必须运行 ``rm -rf`` 删除 pip 安装 site （通常为 ``site-packages/ray`` 路径），然后使用 pip 重新安装（参考上面的命令），最终重新运行上面的 ``setup-dev.py`` 脚本。

.. code-block:: shell

    # To uninstall, delete the symlinks first.
    rm -rf <package path>/site-packages/ray # Path will be in the output of `setup-dev.py`.
    pip uninstall ray # or `pip install -U <wheel>`

准备在 Linux 上构建 Ray
-------------------------------

.. tip:: 如果您仅编辑 Tune/RLlib/Autoscaler 文件，请按照 :ref:`python-develop` 的说明进行操作，以避免较长的构建时间。

要在 Ubuntu 上构建 Ray，请运行以下命令：

.. code-block:: bash

  # Add a PPA containing gcc-9 for older versions of Ubuntu.
  sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
  sudo apt-get update
  sudo apt-get install -y build-essential curl gcc-9 g++-9 pkg-config psmisc unzip
  sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 \
                --slave /usr/bin/g++ g++ /usr/bin/g++-9 \
                --slave /usr/bin/gcov gcov /usr/bin/gcov-9

  # Install Bazel.
  ci/env/install-bazel.sh

  # Install node version manager and node 14
  $(curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh)
  nvm install 14
  nvm use 14


对于 RHELv8（Redhat EL 8.0-64 Minimal），运行以下命令：

.. code-block:: bash

  sudo yum groupinstall 'Development Tools'
  sudo yum install psmisc

在 RedHat 中，从此链接手动安装 Bazel： https://docs.bazel.build/versions/main/install-redhat.html

准备在 MacOS 上构建 Ray
-------------------------------

.. tip:: 假设您已经在 Mac 上安装了 Brew 和 Bazel，并且还在 Mac 上安装了 grpc 和 protobuf，请先考虑便通过命令``brew uninstall grpc``， ``brew uninstall protobuf``删除它们（grpc 和 protobuf） , 以顺利构建。如果您之前已经构建了源代码但仍然出现类似 ``No such file or directory:``，的错误，请尝试通过运行命令 ``brew uninstall binutils`` 和 ``bazel clean --expunge`` 清理主机上的先前构建。

要在 MacOS 上构建 Ray，首先安装以下依赖项：

.. code-block:: bash

  brew update
  brew install wget

  # Install Bazel.
  ray/ci/env/install-bazel.sh

在 Linux 和 MacOS 上构建 Ray（完整版）
------------------------------------

确保您拥有 Ray 的 git 存储库的本地克隆，如上所述。您还需要安装 NodeJS_ 来构建仪表板。

进入项目目录，如：

.. code-block:: shell

    cd ray

现在您可以构建仪表板。从本地 Ray 项目目录内部进入仪表板客户端目录：

.. code-block:: bash

  cd dashboard/client

然后您可以安装依赖项并构建仪表板：

.. code-block:: bash

  npm ci
  npm run build

此后，您现在可以返回到顶级 Ray 目录：

.. code-block:: shell

  cd ../..


现在让我们为 Python 构建 Ray。确保您激活了可以使用的任何 Python（或 conda） 虚拟环境，如上所述。

进入Ray 项目 ``python/`` 目录并使用以下 ``pip`` 命令安装项目：

.. code-block:: bash

  # Install Ray.
  cd python/
  # You may need to set the following two env vars if your platform is MacOS ARM64(M1).
  # See https://github.com/grpc/grpc/issues/25082 for more details.
  # export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
  # export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
  pip install -e . --verbose  # Add --user if you see a permission denied error.

``-e`` 意味着 “可编辑”，因此您对 Ray 目录中的文件所做的更改
将生效，而无需重新安装该包。

.. warning:: 如果你运行 ``python setup.py install`` 文件将从 Ray 目录复制到 Python 包目录 （``/lib/python3.6/site-packages/ray``）。这意味着你对 Ray 目录中的文件所做的更改不会产生任何效果。

.. tip::

  如果您的机器在构建过程中内存不足或构建导致其他程序崩溃，请尝试将以下行添加到 ``~/.bazelrc``:

  ``build --local_ram_resources=HOST_RAM*.5 --local_cpu_resources=4``

  该 ``build --disk_cache=~/bazel-cache`` 选项对于加速重复构建也很有用。

.. note::
  Warning: 如果您在构建 protobuf 时遇到错误，从 miniconda 切换到 anaconda 可能会有所帮助。

.. _NodeJS: https://nodejs.org

在 Windows 上构建 Ray（完整版）
------------------------------

**要求**

在撰写本节时，以下链接是正确的。如果 URL 发生变化，请在相应的组织网站上搜索。

- Bazel 4.2 (https://github.com/bazelbuild/bazel/releases/tag/4.2.1)
- Microsoft Visual Studio 2019 (或 Microsoft Build Tools 2019 - https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019)
- JDK 15 (https://www.oracle.com/java/technologies/javase-jdk15-downloads.html)
- Miniconda 3 (https://docs.conda.io/en/latest/miniconda.html)
- git for Windows, version 2.31.1 或更新版本 (https://git-scm.com/download/win)

您还可以使用附带的脚本来安装 Bazel：

.. code-block:: bash

  # Install Bazel.
  ray/ci/env/install-bazel.sh
  # (Windows users: please manually place Bazel in your PATH, and point
  # BAZEL_SH to MSYS2's Bash: ``set BAZEL_SH=C:\Program Files\Git\bin\bash.exe``)

**步骤**

1. 在 Windows 10 系统上启用开发者模式。这是必要的，以便 git 可以创建符号链接。

   1. 打开设置应用程序；
   2. 转到“更新和安全”；
   3. 转到左侧窗格中的“面向开发人员”；
   4. 打开“开发者模式”。

2. 将以下 Miniconda 子目录添加到 PATH。如果 Miniconda 是为所有用户安装的，则以下路径是正确的。如果 Miniconda 是为单个用户安装的，请相应调整路径。

   - ``C:\ProgramData\Miniconda3``
   - ``C:\ProgramData\Miniconda3\Scripts``
   - ``C:\ProgramData\Miniconda3\Library\bin``

3. 定义一个环境变量 ``BAZEL_SH`` 指向 ``bash.exe``。如果为所有用户安装了 Windows 版 git，则 bash 的路径应为 ``C:\Program Files\Git\bin\bash.exe``。如果为单个用户安装了 git，请相应调整路径。

4. Bazel 4.2 安装。 转到 Bazel 4.2 发布网页并
下载 bazel-4.2.1-windows-x86_64.exe。将 exe 复制到您选择的目录中。
将环境变量 BAZEL_PATH 定义为完整的 exe 路径（例如：
``set BAZEL_PATH=C:\bazel\bazel.exe``）。还将 Bazel 目录添加到
 ``PATH`` （例如： ``set PATH=%PATH%;C:\bazel`` ）

5. 下载 Ray 源码并构建。

.. code-block:: shell

  # cd to the directory under which the ray source tree will be downloaded.
  git clone -c core.symlinks=true https://github.com/ray-project/ray.git
  cd ray\python
  pip install -e . --verbose

影响构建的环境变量
--------------------------------------------

您可以使用以下环境变量来调整构建（运行 ``pip install -e .`` 或 ``python setup.py install`` ）：

- ``RAY_INSTALL_JAVA``: 如果设置等于 ``1``，将执行额外的构建步骤
  来构建代码库的 Java 部分
- ``RAY_INSTALL_CPP``: 如果设置等于 ``1``， ``ray-cpp`` 将安装
- ``RAY_DISABLE_EXTRA_CPP``: 如果设置等于 ``1``，则常规（非
  ``cpp``）构建将不会提供某些 ``cpp`` 接口
- ``SKIP_BAZEL_BUILD``: 如果设置等于 ``1``，则不会执行任何 Bazel 构建步骤
- ``SKIP_THIRDPARTY_INSTALL``: 如果设置将跳过第三方python包的安装
- ``RAY_DEBUG_BUILD``: 可以设置为 ``debug``， ``asan`` 或 ``tsan``。任何其他值将被忽略
- ``BAZEL_ARGS``: 如果已设置，则将一组以空格分隔的参数传递给 Bazel。例如，
  这对于限制构建期间的资源使用非常有用。 有关有效参数的更多信息，请参阅 https://bazel.build/docs/user-manual
- ``IS_AUTOMATED_BUILD``: 用于在 CI 中调整 CI 机器的构建
- ``SRC_DIR``: 可以设置为源签出的根，默认是 ``cwd()`` 的 ``None``
- ``BAZEL_SH``: 在 Windows 上用于查找 ``bash.exe``，见下文
- ``BAZEL_PATH``: 在 Windows 上用于查找 ``bash.exe``，见下文
- ``MINGW_DIR``: 在 Windows 上用于查找 ``bazel.exe``， 如果在 ``BAZEL_PATH`` 中没有找到

安装用于开发的额外依赖项
--------------------------------------------------

可以使用以下命令  (``scripts/format.sh``)  安装 linter ：

.. code-block:: shell

 pip install -r python/requirements/lint-requirements.txt

可以使用以下命令安装运行 Ray 单元测试 ``python/ray/tests`` 的依赖项：

.. code-block:: shell

 pip install -c python/requirements.txt -r python/requirements/test-requirements.txt

运行 Ray Data / ML 库测试的要求文件位于 ``python/requirements/`` 下。

快速、调试和优化构建
---------------------------------

目前，Ray 的构建经过了优化，这可能需要很长时间
并且会干扰调试。 要执行快速、调试或优化构建，您可以运行
以下命令 （分别通过 ``-c`` ``fastbuild`` / ``dbg`` / ``opt``）：

.. code-block:: shell

 bazel build -c fastbuild //:ray_pkg

这将使用适当的选项重建 Ray（可能需要一段时间）。如果您需要
构建所有目标，则可以使用 ``"//:all"`` 替代
``//:ray_pkg``。

为了使此更改永久生效，您可以向用户级 ``~/.bazelrc`` 文件（不要与工作区级文件 ``.bazelrc`` 混淆）
添加如下行选项：

.. code-block:: shell

 build --compilation_mode=fastbuild

如果您这样做，请记住撤消此更改，除非您希望它影响
您将来的所有开发。

使用 ``dbg`` 代替 ``fastbuild`` 会生成更多的调试信息，
这样可以更容易地使用像 ``gdb`` 的调试器进行调试。

构建文档
-----------------

要了解有关构建文档的更多信息，请参阅 `为 Ray 文档做出贡献`_。

.. _为 Ray 文档做出贡献: https://docs.ray.io/en/master/ray-contribute/docs.html

使用本地存储库来获取依赖
-----------------------------------------

如果您想使用自定义依赖项构建 Ray（例如，
使用不同版本的 Cython），您可以按如下方式修改 ``.bzl`` 文件：

.. code-block:: python

  http_archive(
    name = "cython",
    ...,
  ) if False else native.new_local_repository(
    name = "cython",
    build_file = "bazel/BUILD.cython",
    path = "../cython",
  )

This replaces the existing ``http_archive`` rule with one that references a
sibling of your Ray directory (named ``cython``) using the build file
provided in the Ray repository (``bazel/BUILD.cython``).
这将使用 Ray 存储库（名为 ``cython`` ）中提供的构建文件
（ ``bazel/BUILD.cython`` ），将现有 ``http_archive`` 规则替换为引用 Ray 目录的
同级规则。
If the dependency already has a Bazel build file in it, you can use
``native.local_repository`` instead, and omit ``build_file``.
如果依赖项中已包含 Bazel 构建文件，则可以改用 
``native.local_repository``，并省略  ``build_file``。

要测试切换回原始规则，请更改 ``False`` 为 ``True``。

.. _`PR template`: https://github.com/ray-project/ray/blob/master/.github/PULL_REQUEST_TEMPLATE.md

故障排除
---------------

如果在开发克隆中导入 Ray ( ``python3 -c "import ray"``) 导致
此错误：

.. code-block:: python

  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File ".../ray/python/ray/__init__.py", line 63, in <module>
      import ray._raylet  # noqa: E402
    File "python/ray/_raylet.pyx", line 98, in init ray._raylet
      import ray.memory_monitor as memory_monitor
    File ".../ray/python/ray/memory_monitor.py", line 9, in <module>
      import psutil  # noqa E402
    File ".../ray/python/ray/thirdparty_files/psutil/__init__.py", line 159, in <module>
      from . import _psosx as _psplatform
    File ".../ray/python/ray/thirdparty_files/psutil/_psosx.py", line 15, in <module>
      from . import _psutil_osx as cext
  ImportError: cannot import name '_psutil_osx' from partially initialized module 'psutil' (most likely due to a circular import) (.../ray/python/ray/thirdparty_files/psutil/__init__.py)

然后您应该运行以下命令：

.. code-block:: bash

  rm -rf python/ray/thirdparty_files/
  python3 -m pip install setproctitle
