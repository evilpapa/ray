.. _ray-LSF-deploy:

部署在 LSF
================

本文档介绍了在 LSF 上运行 Ray 集群的几个高级步骤。

1) 使用 bsub 指令从 LSF 调度程序获取所需的节点。
2) 在所需节点上获取空闲端口以启动射线服务，如仪表板、GCS 等。
3) 在其中一个可用节点上启动 Ray 头节点。
4) 将所有工作节点连接到头节点。
5) 执行端口转发以访问 ray 仪表板。

步骤 1-4 已经自动化，可以轻松作为脚本运行，请参考以下 github repo 访问脚本并运行示例工作负载：

- `ray_LSF`_ Ray LSF。 用户可以在 LSF 上启动 Ray 集群，并通过该集群以批处理或交互模式运行 DL 工作负载。

.. _`ray_LSF`: https://github.com/IBMSpectrumComputing/ray-integration
