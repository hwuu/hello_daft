# Hello Daft - 分布式数据处理学习教程

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Daft](https://img.shields.io/badge/Daft-0.7.2-green.svg)](https://www.getdaft.io/)
[![Ray](https://img.shields.io/badge/Ray-2.9+-orange.svg)](https://docs.ray.io/)
[![LanceDB](https://img.shields.io/badge/LanceDB-0.4+-purple.svg)](https://lancedb.github.io/lancedb/)

一个面向初学者的系列教程，通过循序渐进的方式学习现代分布式数据处理技术栈。

## 教程概览

| Demo | 主题 | 学习内容 | 难度 |
|------|------|----------|------|
| [Demo 1](./demo1_daft/) | Daft 基础 | 分布式数据框架的使用 | ⭐ |
| [Demo 2](./demo2_ray/) | Ray on K8s | 分布式计算和 K8s 部署 | ⭐⭐ |
| [Demo 3](./demo3_lancedb/) | LanceDB | 向量数据库、语义搜索与综合应用 | ⭐⭐ |
| [Demo 4](./demo4_ai_platform/) | AI Platform | 微服务架构的 ML 平台（数据入库、训练、推理） | ⭐⭐⭐ |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/hwuu/hello-daft.git
cd hello-daft

# 安装依赖
pip install -r requirements.txt

# 从 Demo 1 开始
cd demo1_daft
jupyter notebook notebooks/01_introduction.ipynb
```

## 学习路径

```
Demo 1: Daft 基础
    ↓
Demo 2: Ray on Kubernetes
    ↓
Demo 3: LanceDB + 综合应用
    ↓
Demo 4: AI Platform（整合 Daft + Lance + PyTorch）
```

建议按顺序学习。Demo 4 是综合项目，整合了前三个 Demo 的技术栈构建完整的 ML 平台。

## 项目结构

```
hello_daft/
├── README.md
├── CLAUDE.md
├── requirements.txt
├── .gitignore
│
├── demo1_daft/                  # Demo 1: Daft 基础
│   ├── README.md
│   ├── requirements.txt
│   ├── notebooks/
│   ├── data/
│   └── tests/
│
├── demo2_ray/                   # Demo 2: Ray on K8s
│   ├── README.md
│   ├── requirements.txt
│   ├── notebooks/
│   ├── k8s/
│   └── scripts/
│
├── demo3_lancedb/               # Demo 3: LanceDB
│   ├── README.md
│   ├── notebooks/
│   ├── data/
│   └── lancedb_data/
│
├── demo4_ai_platform/           # Demo 4: AI Platform
│   ├── README.md
│   ├── design.md
│   ├── 01_ai_platform_tutorial.ipynb
│   ├── web/
│   ├── executor/
│   ├── orchestrator/
│   ├── scripts/
│   └── tests/
```
