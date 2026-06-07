"""banksys 数据加载与预处理工具."""

from pathlib import Path

import pandas as pd
import numpy as np


# 数据目录(相对项目根目录)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filepath: str | Path) -> pd.DataFrame:
    """加载 CSV 文件为 DataFrame。

    Args:
        filepath: CSV 文件路径(相对或绝对)。

    Returns:
        pd.DataFrame

    Raises:
        FileNotFoundError: 文件不存在时抛出。
        ValueError: 文件为空时抛出。
    """
    path = Path(filepath)
    if not path.is_absolute():
        path = DATA_DIR / path.name

    if not path.exists():
        raise FileNotFoundError(f"数据文件不存在: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"数据文件为空: {path}") from None
    if df.empty:
        raise ValueError(f"数据文件为空: {path}")
    return df


def get_basic_stats(df: pd.DataFrame) -> dict:
    """获取 DataFrame 基础统计信息。

    Returns:
        dict: 包含行数、列数、列名列表。
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
    }


def get_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    """按类型分组列名。

    Returns:
        dict: {"numeric": [...], "categorical": [...]}
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return {"numeric": numeric_cols, "categorical": categorical_cols}


def get_missing_info(df: pd.DataFrame) -> pd.DataFrame:
    """计算每列缺失值统计。

    Returns:
        DataFrame: 含列名、缺失数、缺失比例。
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    result = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
        }
    )
    result = result[result["missing_count"] > 0].reset_index(drop=True)
    return result


def get_target_distribution(df: pd.DataFrame, target_col: str) -> dict:
    """获取目标列分布统计。

    Args:
        df: 数据。
        target_col: 目标列名。

    Returns:
        dict: {"counts": {value: count}, "percentages": {value: pct}}
    """
    counts = df[target_col].value_counts().to_dict()
    percentages = (df[target_col].value_counts(normalize=True) * 100).round(2).to_dict()
    return {"counts": counts, "percentages": percentages}


# ===== 预处理函数(供模型训练与预测共用) =====


def preprocess_features(df: pd.DataFrame, fit: bool = True, **kwargs) -> pd.DataFrame:
    """对原始特征做编码预处理,保持输入输出为 DataFrame。

    - 分类变量使用 one-hot 编码
    - 数值变量保持不变
    - 处理 unknown / nonexistent 等特殊值

    Args:
        df: 原始数据(不含目标列)。
        fit: True 时从数据中学习类别映射,False 时使用传入的映射。
        **kwargs: 可选,fit=False 时传入 category_dummies 映射。

    Returns:
        编码后的 DataFrame。
    """
    df = df.copy()

    # 标准化分类变量中的特殊值
    categorical_cols = df.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        df[col] = df[col].fillna("unknown").astype(str)

    # One-hot 编码
    df_encoded = pd.get_dummies(df, columns=categorical_cols.tolist(), drop_first=True)

    if fit:
        return df_encoded, df_encoded.columns.tolist()
    else:
        # 预测时对齐训练时的特征列
        train_columns = kwargs.get("train_columns", [])
        for col in train_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        return df_encoded[train_columns]
