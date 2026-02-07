"""Demo 1: Daft 基础使用 - 单元测试"""

import pytest
from pathlib import Path

import daft
from daft import col

from demo1_daft_basics.src.examples import (
    # 第一组 - 数据读取
    get_data_dir,
    read_products_csv,
    read_products_parquet,
    read_products_json,
    create_sample_dataframe,
    # 第二组 - 基础操作
    select_columns,
    filter_by_price,
    filter_by_category,
    sort_by_column,
    add_discount_amount_column,
    deduplicate,
    # 第三组 - 数据处理
    group_by_category_stats,
    group_by_category_brand_stats,
    join_with_category_stats,
    handle_missing_values,
    cast_column_types,
    # 第四组 - 高级特性
    categorize_price,
    text_length,
    apply_price_category,
    apply_text_length,
    show_query_plan,
    compare_read_performance,
    compare_with_pandas,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DATA_DIR = get_data_dir()
DATA_FILES_EXIST = (
    (DATA_DIR / "products.csv").exists()
    and (DATA_DIR / "products.parquet").exists()
    and (DATA_DIR / "products.json").exists()
)

needs_data = pytest.mark.skipif(
    not DATA_FILES_EXIST, reason="数据文件不存在，请先运行 generate_data.py"
)


@pytest.fixture
def sample_df():
    """构造一个小型测试 DataFrame，不依赖数据文件"""
    return daft.from_pydict({
        "product_id": ["P001", "P002", "P003", "P004", "P005"],
        "name": ["手机A", "电脑B", "耳机C", "手机D", "电脑E"],
        "category": ["电子产品", "电子产品", "电子产品", "服装", "服装"],
        "brand": ["华为", "小米", None, "耐克", "阿迪达斯"],
        "price": [2999.0, 4999.0, 199.0, 599.0, 1299.0],
        "original_price": [3999.0, 5999.0, 299.0, 799.0, 1599.0],
        "discount": [25, 17, 33, 25, 19],
        "rating": [4.5, 4.8, None, 4.2, 4.6],
        "review_count": [1000, 2000, 500, 300, 800],
        "stock": [100, 50, 200, 150, 80],
    })


@pytest.fixture
def dup_df():
    """包含重复行的 DataFrame"""
    return daft.from_pydict({
        "product_id": ["P001", "P001", "P002"],
        "name": ["手机A", "手机A", "电脑B"],
        "category": ["电子产品", "电子产品", "电子产品"],
        "brand": ["华为", "华为", "小米"],
        "price": [2999.0, 2999.0, 4999.0],
        "original_price": [3999.0, 3999.0, 5999.0],
        "discount": [25, 25, 17],
        "rating": [4.5, 4.5, 4.8],
        "review_count": [1000, 1000, 2000],
        "stock": [100, 100, 50],
    })


# ---------------------------------------------------------------------------
# 第一组 - 数据读取
# ---------------------------------------------------------------------------

class TestDataReading:

    def test_get_data_dir(self):
        d = get_data_dir()
        assert isinstance(d, Path)
        assert d.name == "data"

    @needs_data
    def test_read_products_csv(self):
        df = read_products_csv()
        result = df.limit(5).collect()
        assert len(result) == 5
        assert "product_id" in result.column_names

    @needs_data
    def test_read_products_parquet(self):
        df = read_products_parquet()
        result = df.limit(5).collect()
        assert len(result) == 5
        assert "product_id" in result.column_names

    @needs_data
    def test_read_products_json(self):
        df = read_products_json()
        result = df.limit(5).collect()
        assert len(result) == 5
        assert "product_id" in result.column_names

    @needs_data
    def test_create_sample_dataframe(self):
        df = create_sample_dataframe()
        result = df.collect()
        assert len(result) == 10


# ---------------------------------------------------------------------------
# 第二组 - 基础操作
# ---------------------------------------------------------------------------

class TestBasicOperations:

    def test_select_columns(self, sample_df):
        result = select_columns(sample_df, ["product_id", "name"]).collect()
        assert result.column_names == ["product_id", "name"]
        assert len(result) == 5

    def test_filter_by_price_min_only(self, sample_df):
        result = filter_by_price(sample_df, min_price=1000).collect()
        prices = result.to_pydict()["price"]
        assert all(p >= 1000 for p in prices)

    def test_filter_by_price_range(self, sample_df):
        result = filter_by_price(sample_df, min_price=500, max_price=3000).collect()
        prices = result.to_pydict()["price"]
        assert all(500 <= p <= 3000 for p in prices)

    def test_filter_by_category(self, sample_df):
        result = filter_by_category(sample_df, "电子产品").collect()
        categories = result.to_pydict()["category"]
        assert all(c == "电子产品" for c in categories)
        assert len(result) == 3

    def test_sort_ascending(self, sample_df):
        result = sort_by_column(sample_df, "price", descending=False).collect()
        prices = result.to_pydict()["price"]
        assert prices == sorted(prices)

    def test_sort_descending(self, sample_df):
        result = sort_by_column(sample_df, "price", descending=True).collect()
        prices = result.to_pydict()["price"]
        assert prices == sorted(prices, reverse=True)

    def test_add_discount_amount_column(self, sample_df):
        result = add_discount_amount_column(sample_df).collect()
        assert "discount_amount" in result.column_names
        data = result.to_pydict()
        for orig, price, amt in zip(
            data["original_price"], data["price"], data["discount_amount"]
        ):
            assert abs(amt - (orig - price)) < 0.01

    def test_deduplicate(self, dup_df):
        result = deduplicate(dup_df).collect()
        assert len(result) == 2


# ---------------------------------------------------------------------------
# 第三组 - 数据处理
# ---------------------------------------------------------------------------

class TestDataProcessing:

    def test_group_by_category_stats(self, sample_df):
        result = group_by_category_stats(sample_df).collect()
        data = result.to_pydict()
        assert "avg_price" in result.column_names
        assert "max_price" in result.column_names
        assert "count" in result.column_names
        # 应有 2 个类别
        assert len(result) == 2

    def test_group_by_category_brand_stats(self, sample_df):
        result = group_by_category_brand_stats(sample_df).collect()
        assert "avg_rating" in result.column_names
        assert "count" in result.column_names
        # 至少有 2 个分组
        assert len(result) >= 2

    def test_join_with_category_stats(self, sample_df):
        result = join_with_category_stats(sample_df).collect()
        assert "avg_price" in result.column_names
        assert "max_price" in result.column_names
        # join 后行数应与原始数据一致
        assert len(result) == 5

    def test_handle_missing_values(self, sample_df):
        result = handle_missing_values(sample_df).collect()
        data = result.to_pydict()
        assert None not in data["brand"]
        assert None not in data["rating"]
        # 原来 brand 为 None 的应变为 '未知品牌'
        assert "未知品牌" in data["brand"]

    def test_cast_column_types(self, sample_df):
        result = cast_column_types(sample_df).collect()
        schema = {f.name: f.dtype for f in result.schema()}
        assert schema["price"] == daft.DataType.float32()
        assert schema["review_count"] == daft.DataType.int32()


# ---------------------------------------------------------------------------
# 第四组 - 高级特性
# ---------------------------------------------------------------------------

class TestAdvancedFeatures:

    def test_categorize_price(self):
        df = daft.from_pydict({"price": [50.0, 500.0, 2000.0, None]})
        result = df.with_column("cat", categorize_price(col("price"))).collect()
        cats = result.to_pydict()["cat"]
        assert cats == ["低", "中", "高", "未知"]

    def test_text_length(self):
        df = daft.from_pydict({"name": ["hello", "世界", None]})
        result = df.with_column("len", text_length(col("name"))).collect()
        lens = result.to_pydict()["len"]
        assert lens == [5, 2, 0]

    def test_apply_price_category(self, sample_df):
        result = apply_price_category(sample_df).collect()
        assert "price_category" in result.column_names
        cats = result.to_pydict()["price_category"]
        assert set(cats).issubset({"低", "中", "高", "未知"})

    def test_apply_text_length(self, sample_df):
        result = apply_text_length(sample_df).collect()
        assert "name_length" in result.column_names
        lens = result.to_pydict()["name_length"]
        assert all(isinstance(l, int) and l > 0 for l in lens)

    def test_show_query_plan(self, sample_df):
        df = sample_df.where(col("price") > 1000)
        plan = show_query_plan(df)
        assert isinstance(plan, str)
        assert "Filter" in plan

    @needs_data
    def test_compare_read_performance(self):
        result = compare_read_performance()
        assert "csv" in result
        assert "parquet" in result
        assert "json" in result
        assert all(isinstance(v, float) and v > 0 for v in result.values())

    @needs_data
    def test_compare_with_pandas(self):
        result = compare_with_pandas()
        assert "pandas" in result
        assert "daft" in result
        assert all(isinstance(v, float) and v > 0 for v in result.values())
