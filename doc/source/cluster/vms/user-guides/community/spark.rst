.. _ray-Spark-deploy:

部署在独立的 Spark 集群上
=====================================

本文档介绍了在 `Spark 独立集群<https://spark.apache.org/docs/latest/spark-standalone.html>`_ 上运行 Ray 集群的几个高级步骤。

运行基础示例
-----------------------

这是一个 spark 应用程序示例代码，它在 spark 上启动 ray 集群，
然后执行 ray 应用程序代码，然后关闭启动的 ray 集群。

1) 创建一个包含spark应用程序代码的python文件，
假设python文件名为“ray-on-spark-example1.py”。

.. code-block:: python

    from pyspark.sql import SparkSession
    from ray.util.spark import setup_ray_cluster, shutdown_ray_cluster, MAX_NUM_WORKER_NODES
    if __name__ == "__main__":
        spark = SparkSession \
            .builder \
            .appName("Ray on spark example 1") \
            .config("spark.task.cpus", "4") \
            .getOrCreate()

        # Set up a ray cluster on this spark application, it creates a background
        # spark job that each spark task launches one ray worker node.
        # ray head node is launched in spark application driver side.
        # Resources (CPU / GPU / memory) allocated to each ray worker node is equal
        # to resources allocated to the corresponding spark task.
        setup_ray_cluster(num_worker_nodes=MAX_NUM_WORKER_NODES)

        # You can any ray application code here, the ray application will be executed
        # on the ray cluster setup above.
        # You don't need to set address for `ray.init`,
        # it will connect to the cluster created above automatically.
        ray.init()
        ...

        # Terminate ray cluster explicitly.
        # If you don't call it, when spark application is terminated, the ray cluster
        # will also be terminated.
        shutdown_ray_cluster()

2) 将上面的spark应用程序提交到spark standalone集群。

.. code-block:: bash

    #!/bin/bash
    spark-submit \
      --master spark://{spark_master_IP}:{spark_master_port} \
      path/to/ray-on-spark-example1.py

在 Spark 集群上创建长期运行的 Ray 集群
----------------------------------------------------

这是一个 spark 应用程序示例代码，它在 spark 上启动一个长时间运行的 ray 集群。
创建的 ray 集群可以被远程 python 进程访问。

1) 创建一个包含spark应用程序代码的python文件，
假设python文件名为“long-running-ray-cluster-on-spark.py”。

.. code-block:: python

    from pyspark.sql import SparkSession
    import time
    from ray.util.spark import setup_ray_cluster, MAX_NUM_WORKER_NODES

    if __name__ == "__main__":
        spark = SparkSession \
            .builder \
            .appName("long running ray cluster on spark") \
            .config("spark.task.cpus", "4") \
            .getOrCreate()

        cluster_address = setup_ray_cluster(
            num_worker_nodes=MAX_NUM_WORKER_NODES
        )
        print("Ray cluster is set up, you can connect to this ray cluster "
              f"via address ray://{cluster_address}")

        # Sleep forever until the spark application being terminated,
        # at that time, the ray cluster will also be terminated.
        while True:
            time.sleep(10)

2) 将上面的spark应用程序提交到spark standalone集群。

.. code-block:: bash

    #!/bin/bash
    spark-submit \
      --master spark://{spark_master_IP}:{spark_master_port} \
      path/to/long-running-ray-cluster-on-spark.py

Ray on Spark APIs
-----------------

.. autofunction:: ray.util.spark.setup_ray_cluster

.. autofunction:: ray.util.spark.shutdown_ray_cluster
