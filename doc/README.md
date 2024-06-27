# Ray 文档

Ray 工程文档仓库，发布在 [docs.ray.io](https://docs.ray.io).

## 安装

要构建此文档，请确保先安装 `ray` 。
要进行本地文档构建请安装以下依赖：

```bash
pip install -r requirements-doc.txt
```

## 构建文档

要编译文档并在本地打开，请在此目录运行以下命令：

```bash
make develop && open _build/html/index.html
```

> **_NOTE:_**  以上命令用于开发。要从 CI 重现构建失败，
> 你可以使用 `make html` ，它同 `make develop` 相同，但会把警告作为错误处理。
> 此外，注意 `make develop` 使用 `FAST` 环境变量来跳过构建过程中的一些昂贵的部分。
> 特别是，它将大力修剪左侧导航，
> 但保持文档本身完好无损。

## 仅构建子项目

通常，文档中的更改仅涉及一个子项目，例如 Tune 或 Train。
要仅构建这一个子项目，并忽略其余项目
（导致由于引用损坏等而出现构建警告），请运行以下命令：

```shell
DOC_LIB=<project> sphinx-build -b html -d _build/doctrees  source _build/html
```
`<project>` 是子项目的名称并可以是在 `source/` 下的任一文档项目如
`tune`， `rllib`， `train`， `cluster`， `serve`， `data` 或者以
 `ray-` 打头的，如 `ray-observability`。

## 公告和包含

要添加新的公告和其他头部或底部的文档页信息，
首先检查 `_includes` 文件夹来查看所需信息是否已经存在（比如 “get help” 或者 “招聘” 等。）
如果没有，请添加所需的模板并相应地包含它，即使用

```markdown
.. include:: /_includes/<my-announcement>
```

这确保了文档页面间的信息传递一致性。

## 检查破坏的链接

要检查是否存在断开的链接，
请运行以下命令（由于存在误报，我们目前不在 CI 中运行此操作）。

```bash
make linkcheck
```

## 运行 doctests

要对 Python 文件中带有文档字符串的示例运行测试，请运行以下命令：

```shell
make doctest
```

## 将示例添加为 MyST Markdown 笔记本

你现在可以添加 [可执行笔记本](https://myst-nb.readthedocs.io/en/latest/use/markdown.html) 到项目中，
它将会构建到文档中。
一个 [可在这里找到的示例](./source/serve/tutorials/rllib.md)。
默认情况下，使用 `make evolve` 构建文档不会运行这些笔记本。
如果设置 `RUN_NOTEBOOKS` 环境变量为 `"cache"`，每个笔记本单元都将在您构建文档时运行，
并且输出会缓存在 `_build/.jupyter_cache`。

```bash
RUN_NOTEBOOKS="cache" make develop
```

强制重新运行笔记本，使用 `RUN_NOTEBOOKS="force"`。

使用缓存，这意味着首次构建文档时，可能会花好一会来运行笔记本。
这之后，笔记本运行只有在笔记本源文件变化后触发。

使用笔记本作为示例的好处是您不必将代码与文档分开，但仍可以轻松地对代码进行冒烟测试。

## 从外部（生态系统）存储库添加 Markdown 文档

为了避免此存储库中的 docs 文件夹和生态系统库（例如 xgboost-ray）的外部存储库中
存在重复的文档文件的情况，
您可以指定在构建过程中从其他 GitHub 存储库下载的 Markdown 文件。

为此，只需使用注释的格式编辑列在 `source/custom_directives.py` 中的 `EXTERNAL_MARKDOWN_FILES` 即可。
在构建过程之前，将下载、预处理并保存到给定路径的指定文件。
然后构建过程将正常进行。

虽然 GitHub Markdown 和 MyST 都是常见 Markdown 的超集，但在语法上存在差异。
此外，某些内容（例如 Sphinx 标题）不适合显示在 GitHub 上。
为了解决这个问题，会执行简单的预处理以允许在 GitHub 和文档中呈现差异。
你可以在 Markdown 文件中使用两个命令 （`$UNCOMMENT` 和 `$REMOVE`/`$END_REMOVE`），
指定方式如下：

### `$UNCOMMENT`

GitHub:

```html
<!--$UNCOMMENTthis will be uncommented--> More text
```

在文档中，这将变成：

```html
this will be uncommented More text
```

### `$REMOVE`/`$END_REMOVE`

GitHub:

```html
<!--$REMOVE-->This will be removed<!--$END_REMOVE--> More text
```

在文档中，这将变成：

```html
More text
```

请注意，解析非常简单（正则表达式替换）并且不支持嵌套。

## 测试本地修改

如果您想要在特定文件上本地运行预处理（例如，查看文档构建后它将如何呈现），请运行 `source/preprocess_github_markdown.py PATH_TO_MARKDOWN_FILE PATH_TO_PREPROCESSED_MARKDOWN_FILE`。 请确保也在在 `source/custom_directives.py` 文件中编辑  `EXTERNAL_MARKDOWN_FILES` ，以便您的文件不会被从 GitHub 下载的文件覆盖。
