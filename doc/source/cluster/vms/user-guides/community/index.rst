.. _ref-cluster-setup:

社区支持的集群管理器
====================================

.. note::

    如果您使用 AWS、Azure、GCP 或 vSphere，则可以使用 :ref:`Ray 集群启动器 <cluster-index>` 来简化集群设置过程。

以下是社区支持的集群管理器列表。

.. toctree::
   :maxdepth: 2

   yarn.rst
   slurm.rst
   lsf.rst
   spark.rst

.. _ref-additional-cloud-providers:

使用自定义云或集群管理器
=======================================

Ray 集群启动器目前开箱即用地支持 AWS、Azure、GCP、阿里云、vSphere 和 Kuberay。要在其他云提供商或集群管理器上使用 Ray 集群启动器和 Autoscaler，您可以实现 `node_provider.py <https://github.com/ray-project/ray/tree/master/python/ray/autoscaler/node_provider.py>`_ 接口 (100 LOC)。
实现节点提供程序后，您可以在集群启动器配置的 `提供商 <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/local/example-full.yaml#L18>`_ 注册它。

.. code-block:: yaml

    provider:
      type: "external"
      module: "my.module.MyCustomNodeProvider"

您可以参考 `AWSNodeProvider <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/_private/aws/node_provider.py#L95>`_、 `KuberayNodeProvider <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/_private/kuberay/node_provider.py#L148>`_ 和
 `LocalNodeProvider <https://github.com/ray-project/ray/blob/master/python/ray/autoscaler/_private/local/node_provider.py#L166>`_ 提供的更多示例。
