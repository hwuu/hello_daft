"""
Demo 1: Daft 基础使用 - 示例函数模块

提供 4 组函数，分别对应 4 个 Notebook：
1. 数据读取
2. 基础操作
3. 数据处理
4. 高级特性
"""

import io
import sys
import time
from pathlib import Path

import daft
from daft import col


# ---------------------------------------------------------------------------
# 第一组 - 数据读取
# ---------------------------------------------------------------------------

def get_data_dir() -> Path:
    """获取数据目录路径"""
    return Path(__file__).resolve().parent.parent / "data"


def read_products_csv(path=None) -> daft.DataFrame:
    """读取 CSV 格式的产品数据"""
    if path is None:
        path = str(get_data_dir() / "products.csv")
    return daft.read_csv(str(path))


def read_products_parquet(path=None) -> daft.DataFrame:
    """读取 Parquet 格式的产品数据"""
    if path is None:
        path = str(get_data_dir() / "products.parquet")
    return daft.read_parquet(str(path))


def read_products_json(path=None) -> daft.DataFrame:
    """读取 JSON 格式的产品数据"""
    if path is None:
        path = str(get_data_dir() / "products.json")
    return daft.read_json(str(path))


def create_sample_dataframe(path=None) -> daft.DataFrame:
    """从 CSV 取前 10 行作为示例 DataFrame"""
    df = read_products_csv(path)
    return df.limit(10)


# ---------------------------------------------------------------------------
# 第二组 - 基础操作
# ---------------------------------------------------------------------------

def select_columns(df: daft.DataFrame, columns: list[str]) -> daft.DataFrame:
    """选择指定列"""
    return df.select(*columns)


def filter_by_price(
    df: daft.DataFrame, min_price: float, max_price: float = None
) -> daft.DataFrame:
    """按价格过滤，支持仅设下限或同时设上下限"""
    if max_price is None:
        return df.where(col("price") >= min_price)
    return df.where((col("price") >= min_price) & (col("price") <= max_price))


def filter_by_category(df: daft.DataFrame, category: str) -> daft.DataFrame:
    """按类别过滤"""
    return df.where(col("category") == category)


def sort_by_column(
    df: daft.DataFrame, column: str, descending: bool = False
) -> daft.DataFrame:
    """按指定列排序"""
    return df.sort(column, desc=descending)


def add_discount_amount_column(df: daft.DataFrame) -> daft.DataFrame:
    """添加折扣金额列: original_price - price"""
    return df.with_column(
        "discount_amount",
        col("original_price") - col("price"),
    )


def deduplicate(df: daft.DataFrame) -> daft.DataFrame:
    """去重"""
    return df.distinct()


# ---------------------------------------------------------------------------
# 第三组 - 数据处理
# ---------------------------------------------------------------------------

def group_by_category_stats(df: daft.DataFrame) -> daft.DataFrame:
    """按类别统计：平均价格、最高价格、产品数量"""
    return df.groupby("category").agg(
        col("price").mean().alias("avg_price"),
        col("price").max().alias("max_price"),
        col("price").count().alias("count"),
    )


def group_by_category_brand_stats(df: daft.DataFrame) -> daft.DataFrame:
    """按类别+品牌统计：平均评分、产品数量"""
    return df.groupby("category", "brand").agg(
        col("rating").mean().alias("avg_rating"),
        col("product_id").count().alias("count"),
    )


def join_with_category_stats(df: daft.DataFrame) -> daft.DataFrame:
    """将原始数据与类别统计信息进行内连接"""
    stats = group_by_category_stats(df)
    return df.join(stats, on="category", how="inner")


def handle_missing_values(df: daft.DataFrame) -> daft.DataFrame:
    """处理缺失值：brand 填充为 '未知品牌'，rating 填充为 0.0"""
    return df.with_columns({
        "brand": col("brand").fill_null("未知品牌"),
        "rating": col("rating").fill_null(0.0),
    })


def cast_column_types(df: daft.DataFrame) -> daft.DataFrame:
    """类型转换：price 转为 float32，review_count 转为 int32"""
    return df.with_columns({
        "price": col("price").cast(daft.DataType.float32()),
        "review_count": col("review_count").cast(daft.DataType.int32()),
    })


# ---------------------------------------------------------------------------
# 第四组 - 高级特性
# ---------------------------------------------------------------------------

@daft.func(return_dtype=daft.DataType.string())
def categorize_price(price):
    """价格分类 UDF：低(<100)、中(100-1000)、高(>1000)"""
    if price is None:
        return "未知"
    elif price < 100:
        return "低"
    elif price <= 1000:
        return "中"
    else:
        return "高"


@daft.func(return_dtype=daft.DataType.int64())
def text_length(text):
    """文本长度 UDF"""
    if text is None:
        return 0
    return len(text)


def apply_price_category(df: daft.DataFrame) -> daft.DataFrame:
    """应用价格分类 UDF"""
    return df.with_column("price_category", categorize_price(col("price")))


def apply_text_length(df: daft.DataFrame) -> daft.DataFrame:
    """应用文本长度 UDF 到 name 列"""
    return df.with_column("name_length", text_length(col("name")))


def show_query_plan(df: daft.DataFrame) -> str:
    """捕获并返回查询计划字符串"""
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        df.explain(show_all=True)
    finally:
        sys.stdout = old_stdout
    return buffer.getvalue()


def compare_read_performance(data_dir=None) -> dict:
    """对比 CSV / Parquet / JSON 读取 + collect 性能，返回耗时字典"""
    if data_dir is None:
        data_dir = get_data_dir()
    else:
        data_dir = Path(data_dir)

    results = {}
    for fmt, reader in [
        ("csv", lambda: daft.read_csv(str(data_dir / "products.csv"))),
        ("parquet", lambda: daft.read_parquet(str(data_dir / "products.parquet"))),
        ("json", lambda: daft.read_json(str(data_dir / "products.json"))),
    ]:
        start = time.time()
        reader().collect()
        results[fmt] = round(time.time() - start, 4)

    return results


def compare_with_pandas(csv_path=None) -> dict:
    """Daft vs Pandas 读取 CSV 性能对比，返回耗时字典"""
    import pandas as pd

    if csv_path is None:
        csv_path = str(get_data_dir() / "products.csv")
    else:
        csv_path = str(csv_path)

    # Pandas
    start = time.time()
    pd.read_csv(csv_path)
    pandas_time = round(time.time() - start, 4)

    # Daft
    start = time.time()
    daft.read_csv(csv_path).collect()
    daft_time = round(time.time() - start, 4)

    return {"pandas": pandas_time, "daft": daft_time}
