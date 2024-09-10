# 在云虚拟机上的 Ray
(cloud-vm-index)=

## 概述

在本节中，我们将介绍如何在云虚拟机上启动 Ray 集群。 Ray 内置了启动 AWS 和 GCP 集群
的支持，并且还具有针对 Azure、阿里云和 vSphere 的社区维护集成。
每个 Ray 集群都由一个头节点和一组工作节点组成。 可选的
[自动缩放](vms-autoscaling) 支持允许根据 Ray 工作负载的要求
调整 Ray 集群的大小，并根据需要添加和删除工作节点。
Ray 支持由多个异构计算节点「包括 GPU 节点」组成的集群。

具体来说，你将学习如何：

- 在公共云中设置和配置 Ray
- 部署应用程序并监控集群

## 了解更多

Ray 文档提供了在虚拟机上开始运行 Ray 工作负载所需的所有信息。

```{eval-rst}
.. grid:: 1 2 2 2
    :gutter: 1
    :class-container: container pb-3
    
    .. grid-item-card::
    
        **入门**
        ^^^
    
        了解如何启动 Ray 集群并在云中部署 Ray 应用程序。
    
        +++
        .. button-ref:: vm-cluster-quick-start
            :color: primary
            :outline:
            :expand:

            在虚拟机安装 Ray
    
    .. grid-item-card::

        **示例**
        ^^^
    
        在云中尝试 Ray 工作负载示例
    
        +++
        .. button-ref:: vm-cluster-examples
            :color: primary
            :outline:
            :expand:

            尝试工作负载示例
    
    .. grid-item-card::

        **用户指南**
        ^^^
    
        了解配置云集群的最佳实践
    
        +++
        .. button-ref:: vm-cluster-guides
            :color: primary
            :outline:
            :expand:

            阅读用户指南
    
    .. grid-item-card::

        **API 参考**
        ^^^
    
        查找云集群的 API 参考
    
        +++
        .. button-ref:: vm-cluster-api-references
            :color: primary
            :outline:
            :expand:

            检查 API 参考
```
