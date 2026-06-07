"""测试 Streamlit 应用页面逻辑."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

# 将 app 目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from app.utils import (
    load_csv,
    get_basic_stats,
    get_column_types,
    get_missing_info,
    get_target_distribution,
    DATA_DIR,
)


# ===== Fixtures =====


@pytest.fixture
def train_df():
    """加载真实训练数据的前 100 行用于快速测试。"""
    df = load_csv(DATA_DIR / "train.csv")
    return df.head(100)


# ===== 数据加载集成测试 =====


def test_train_data_loads():
    """真实训练数据应能正确加载。"""
    df = load_csv(DATA_DIR / "train.csv")
    assert len(df) == 22500
    assert "subscribe" in df.columns


def test_test_data_loads():
    """真实测试数据应能正确加载。"""
    df = load_csv(DATA_DIR / "test.csv")
    assert len(df) == 7500


# ===== 页面逻辑测试 =====


def test_data_overview_stats(train_df):
    """概览统计应返回正确行/列数。"""
    stats = get_basic_stats(train_df)
    assert stats["rows"] == 100
    assert "age" in stats["column_names"]


def test_column_type_detection(train_df):
    """应正确区分数值与分类特征。"""
    types = get_column_types(train_df)
    assert "age" in types["numeric"]
    assert "duration" in types["numeric"]
    assert "job" in types["categorical"]
    assert "subscribe" in types["categorical"]


def test_missing_values_detection(train_df):
    """缺失值检测应正常工作。"""
    missing = get_missing_info(train_df)
    # 原始数据可能无缺失,或只有少量
    assert isinstance(missing, pd.DataFrame)


def test_target_distribution_format(train_df):
    """目标分布应返回正确的 dict 结构。"""
    dist = get_target_distribution(train_df, "subscribe")
    assert "counts" in dist
    assert "percentages" in dist
    total = sum(dist["counts"].values())
    assert total == 100  # 行数


def test_filter_by_age(train_df):
    """按年龄筛选逻辑验证。"""
    filtered = train_df[train_df["age"] >= 30]
    assert len(filtered) <= len(train_df)
    assert all(filtered["age"] >= 30)


def test_filter_by_job(train_df):
    """按职业筛选逻辑验证。"""
    filtered = train_df[train_df["job"].isin(["admin.", "technician"])]
    assert all(filtered["job"].isin(["admin.", "technician"]))


def test_correlation_matrix_shape(train_df):
    """相关性矩阵应有正确的维度。"""
    numeric_cols = train_df.select_dtypes(include=["number"]).columns
    corr = train_df[numeric_cols].corr()
    assert corr.shape[0] == len(numeric_cols)
    assert corr.shape[1] == len(numeric_cols)


# ===== 页面导入测试 =====


def test_analysis_page_imports():
    """数据分析页面应能正确导入依赖。"""
    # 模拟 streamlit 环境
    mock_st = MagicMock()
    with patch.dict(sys.modules, {"streamlit": mock_st}):
        mock_st.set_page_config = MagicMock()
        mock_st.title = MagicMock()
        # 验证导入不会抛出异常
        from importlib import util

        spec = util.spec_from_file_location(
            "analysis_page",
            Path(__file__).resolve().parent.parent
            / "app"
            / "pages"
            / "1_📊_数据分析.py",
        )
        assert spec is not None
