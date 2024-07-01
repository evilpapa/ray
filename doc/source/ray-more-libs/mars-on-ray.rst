.. _mars-on-ray:

Ray 上使用 Mars
=================

.. _`issue on GitHub`: https://github.com/mars-project/mars/issues


`Mars`_ 是一个基于张量的统一大规模数据计算框架，可以扩展 Numpy、Pandas 和 Scikit-learn。
Mars 之 Ray 让你的程序使用 Ray 集群轻松扩展。目前 Mars on Ray 同时支持 Ray actors 和 task 作为执行后端。
如果使用 Ray actors ，任务将由 mars scheduler 调度。
此模式可以重用所有 mars scheduler 优化。
如果使用 ray jobs 模式，所有任务将由 ray 调度，这可以重用 ray 特性提供的故障转移和管道功能。


.. _`Mars`: https://mars-project.readthedocs.io/en/latest/


安装
-------------
你可以简单地通过 pip 安装 Mars：

.. code-block:: bash

    pip install pymars>=0.8.3


入门
----------------

在 Ray 集群上运行 Mars 作业很容易。


通过以下方式在本地启动新的 Mars on Ray 运行时：


.. code-block:: python

    import ray
    ray.init()
    import mars
    mars.new_ray_session()
    import mars.tensor as mt
    mt.random.RandomState(0).rand(1000_0000, 5).sum().execute()


或者连接到已初始化的 Mars on Ray 运行时：


.. code-block:: python

    import mars
    mars.new_ray_session('http://<web_ip>:<ui_port>')
    # perform computation


与数据集交互：


.. code-block:: python

    import mars.tensor as mt
    import mars.dataframe as md
    df = md.DataFrame(
        mt.random.rand(1000_0000, 4),
        columns=list('abcd'))
    # Convert mars dataframe to ray dataset
    import ray
    # ds = md.to_ray_dataset(df)
    ds = ray.data.from_mars(df)
    print(ds.schema(), ds.count())
    ds.filter(lambda row: row["a"] > 0.5).show(5)
    # Convert ray dataset to mars dataframe
    # df2 = md.read_ray_dataset(ds)
    df2 = ds.to_mars()
    print(df2.head(5).execute())

有关更多信息 ， 请参阅Mars on Ray ： https://mars-project.readthedocs.io/en/latest/installation/ray.html#mars-ray 。
