"""测试数据加载与预处理工具."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from app.utils import (
    load_csv,
    get_basic_stats,
    get_column_types,
    get_missing_info,
    get_target_distribution,
    preprocess_features,
)


# ===== Fixtures =====


@pytest.fixture
def sample_csv():
    """创建临时 CSV 供测试使用。"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(
            "age,job,marital,subscribe\n"
            "30,admin.,married,no\n"
            "45,technician,single,yes\n"
            "28,blue-collar,married,no\n"
        )
        return Path(f.name)


@pytest.fixture
def sample_df():
    """创建示例 DataFrame。"""
    return pd.DataFrame(
        {
            "age": [30, 45, 28, 52],
            "job": ["admin.", "technician", "blue-collar", "admin."],
            "marital": ["married", "single", "married", "divorced"],
            "subscribe": ["no", "yes", "no", "yes"],
        }
    )


# ===== load_csv =====


def test_load_csv_success(sample_csv):
    df = load_csv(sample_csv)
    assert len(df) == 3
    assert list(df.columns) == ["age", "job", "marital", "subscribe"]


def test_load_csv_file_not_found():
    with pytest.raises(FileNotFoundError, match="数据文件不存在"):
        load_csv("nonexistent.csv")


def test_load_csv_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("")
        empty_path = Path(f.name)
    try:
        with pytest.raises(ValueError, match="数据文件为空"):
            load_csv(empty_path)
    finally:
        empty_path.unlink(missing_ok=True)


# ===== get_basic_stats =====


def test_basic_stats(sample_df):
    stats = get_basic_stats(sample_df)
    assert stats["rows"] == 4
    assert stats["columns"] == 4
    assert "age" in stats["column_names"]


# ===== get_column_types =====


def test_column_types(sample_df):
    types = get_column_types(sample_df)
    assert "age" in types["numeric"]
    assert "job" in types["categorical"]
    assert "subscribe" in types["categorical"]


# ===== get_missing_info =====


def test_missing_info_no_missing(sample_df):
    result = get_missing_info(sample_df)
    assert len(result) == 0  # 无缺失值时返回空


def test_missing_info_with_missing(sample_df):
    df = sample_df.copy()
    df.loc[0, "age"] = None
    result = get_missing_info(df)
    assert len(result) == 1
    assert result.iloc[0]["column"] == "age"
    assert result.iloc[0]["missing_pct"] == 25.0


# ===== get_target_distribution =====


def test_target_distribution(sample_df):
    dist = get_target_distribution(sample_df, "subscribe")
    assert dist["counts"]["no"] == 2
    assert dist["counts"]["yes"] == 2
    assert dist["percentages"]["no"] == 50.0


# ===== preprocess_features =====


def test_preprocess_fit(sample_df):
    features = sample_df.drop(columns=["subscribe"])
    encoded, columns = preprocess_features(features, fit=True)
    assert isinstance(encoded, pd.DataFrame)
    assert len(encoded) == 4
    assert isinstance(columns, list)
    assert "age" in encoded.columns


def test_preprocess_transform_with_columns(sample_df):
    features = sample_df.drop(columns=["subscribe"])
    encoded, train_cols = preprocess_features(features, fit=True)

    # 模拟新数据
    new_features = pd.DataFrame({"age": [35], "job": ["admin."], "marital": ["single"]})
    new_encoded = preprocess_features(new_features, fit=False, train_columns=train_cols)
    assert list(new_encoded.columns) == train_cols
    assert len(new_encoded) == 1
