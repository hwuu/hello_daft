# Demo 3: LanceDB 向量数据库与语义搜索

LanceDB 是一个嵌入式向量数据库，本教程通过中文商品评论数据集，演示向量存储、嵌入生成和语义搜索的完整流程，并展示 Daft 与 LanceDB 的集成使用。

## 前置要求

- Python 环境（推荐 conda `hello_daft` 环境）
- SiliconFlow API Key（用于嵌入生成，Notebook 02/03 需要）
  ```bash
  export OPENAI_API_KEY='your-siliconflow-key'
  export OPENAI_BASE_URL='https://api.siliconflow.cn/v1'
  ```

## 快速开始

```bash
# 1. 安装依赖
pip install -r demo3_lancedb/requirements.txt

# 2. 准备数据（下载并清洗中文评论数据集，约 3000 条）
python demo3_lancedb/data/prepare_data.py --output demo3_lancedb/data

# 3. 启动 Notebook
jupyter notebook demo3_lancedb/notebooks/
```

## Notebook 列表

| 序号 | Notebook | 简介 |
|------|----------|------|
| 01 | [LanceDB 介绍与基础操作](notebooks/01_introduction.ipynb) | 向量数据库概念、LanceDB 连接与 CRUD 操作（无需 API Key） |
| 02 | [嵌入与语义搜索](notebooks/02_embeddings_search.ipynb) | 使用 SiliconFlow API 生成嵌入，实现语义搜索与混合搜索 |
| 03 | [Daft + LanceDB 集成](notebooks/03_daft_and_lancedb.ipynb) | 用 Daft 读写 Lance 格式、数据预处理与嵌入生成的完整 pipeline |
