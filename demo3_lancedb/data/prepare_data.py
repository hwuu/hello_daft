"""
数据准备脚本 - 下载并清洗中文商品评论数据集

数据来源: online_shopping_10_cats (10 类中文商品评论)
用法:
    python prepare_data.py [--output demo3_lancedb/data] [--sample-per-cat 300]
"""

import argparse
import io
import urllib.request
from pathlib import Path

import pandas as pd

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "jamosnet/JD-comments-sentiment-analysis/"
    "master/online_shopping_10_cats.csv"
)


def download_csv(url: str) -> pd.DataFrame:
    """下载 CSV 并返回 DataFrame"""
    print(f"正在下载数据: {url}")
    response = urllib.request.urlopen(url)
    raw_bytes = response.read()
    # 去除 BOM 字符
    text = raw_bytes.decode("utf-8-sig")
    df = pd.read_csv(io.StringIO(text))
    print(f"下载完成，共 {len(df):,} 条记录")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """清洗数据：去除空值行、去除 BOM 残留"""
    before = len(df)
    # 删除 review 列为空的行
    df = df.dropna(subset=["review"])
    # 删除 review 为纯空白的行
    df = df[df["review"].str.strip().astype(bool)]
    # 去除 review 中可能残留的 BOM 字符
    df["review"] = df["review"].str.replace("\ufeff", "", regex=False)
    after = len(df)
    print(f"清洗完成: {before:,} -> {after:,} 条（删除 {before - after:,} 条无效记录）")
    return df.reset_index(drop=True)


def sample_balanced(df: pd.DataFrame, sample_per_cat: int) -> pd.DataFrame:
    """每个类别均衡采样"""
    cats = df["cat"].unique()
    print(f"共 {len(cats)} 个类别: {', '.join(sorted(cats))}")

    sampled = []
    for cat in sorted(cats):
        cat_df = df[df["cat"] == cat]
        n = min(sample_per_cat, len(cat_df))
        sampled.append(cat_df.sample(n=n, random_state=42))
        print(f"  {cat}: {len(cat_df):,} -> {n}")

    result = pd.concat(sampled, ignore_index=True)
    print(f"采样完成，共 {len(result):,} 条记录")
    return result


def main():
    parser = argparse.ArgumentParser(description="下载并清洗中文商品评论数据集")
    parser.add_argument(
        "--output", type=str, default=".", help="输出目录（默认: 当前目录）"
    )
    parser.add_argument(
        "--sample-per-cat",
        type=int,
        default=300,
        help="每个类别采样数量（默认: 300）",
    )
    args = parser.parse_args()

    # 下载
    df = download_csv(DATA_URL)

    # 清洗
    df = clean_data(df)

    # 均衡采样
    df = sample_balanced(df, args.sample_per_cat)

    # 保存
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    csv_path = output_path / "reviews.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n已保存到 {csv_path}（{csv_path.stat().st_size / 1024:.1f} KB）")

    # 输出统计
    print(f"\n数据统计:")
    print(f"  总记录数: {len(df):,}")
    print(f"  列: {list(df.columns)}")
    print(f"  类别分布:")
    print(df["cat"].value_counts().to_string(header=False))


if __name__ == "__main__":
    main()
