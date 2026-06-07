"""在线预测模块 — 加载训练好的模型并执行推理."""

import json
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd

# ===== 路径常量 =====
ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT_DIR / "model" / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
FEATURE_NAMES_PATH = ARTIFACTS_DIR / "feature_names.json"

# ===== 预测所需特征 =====
REQUIRED_FEATURES = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]


# ===== 模型加载(缓存) =====

_model_cache: Optional[object] = None
_feature_names_cache: Optional[list[str]] = None


def get_model():
    """获取已缓存的模型。若未加载则加载。

    Returns:
        训练好的 sklearn Pipeline。

    Raises:
        FileNotFoundError: 模型文件不存在时抛出。
    """
    global _model_cache
    if _model_cache is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"模型文件不存在: {MODEL_PATH}\n"
                "请先运行 python model/train.py 训练模型。"
            )
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def get_feature_names() -> list[str]:
    """获取训练时使用的特征名列表。"""
    global _feature_names_cache
    if _feature_names_cache is None:
        if FEATURE_NAMES_PATH.exists():
            with open(FEATURE_NAMES_PATH) as f:
                _feature_names_cache = json.load(f)
        else:
            _feature_names_cache = REQUIRED_FEATURES
    return _feature_names_cache


def clear_cache():
    """清除模型缓存(测试用)。"""
    global _model_cache, _feature_names_cache
    _model_cache = None
    _feature_names_cache = None


# ===== 预测函数 =====


def predict(features: dict) -> dict:
    """根据客户特征预测认购倾向。

    Args:
        features: 特征字典,key 为特征名,value 为特征值。
                  必填: REQUIRED_FEATURES 中的全部 20 个特征。

    Returns:
        dict: {
            "prediction": "yes" | "no",
            "probability": float (0~1),
            "confidence": float (0~1),  # 概率或 1-概率 中较大者
        }

    Raises:
        ValueError: 缺少必填特征时抛出。
        FileNotFoundError: 模型未训练时抛出。
    """
    # 校验必填特征
    missing = [f for f in REQUIRED_FEATURES if f not in features]
    if missing:
        raise ValueError(f"缺少必填特征: {missing}")

    model = get_model()

    # 构造 DataFrame
    input_df = pd.DataFrame([features])
    input_df = input_df[REQUIRED_FEATURES]

    # 预测
    y_proba = model.predict_proba(input_df)[:, 1][0]
    y_pred = model.predict(input_df)[0]

    prediction_label = "yes" if y_pred == 1 else "no"
    confidence = y_proba if y_pred == 1 else 1 - y_proba

    return {
        "prediction": prediction_label,
        "probability": round(float(y_proba), 4),
        "confidence": round(float(confidence), 4),
    }


# ===== 输入校验 =====


def validate_input(value, feature_name: str) -> Optional[str]:
    """校验单个特征输入值的合法性。

    Args:
        value: 用户输入值。
        feature_name: 特征名。

    Returns:
        str: 错误信息,或 None(通过)。
    """
    numeric_features = {
        "age": (17, 100),
        "duration": (0, 5000),
        "campaign": (1, 50),
        "pdays": (0, 999),
        "previous": (0, 10),
    }

    if feature_name in numeric_features:
        lo, hi = numeric_features[feature_name]
        try:
            v = float(value)
        except (ValueError, TypeError):
            return f"{feature_name} 必须是数字"
        if v < lo or v > hi:
            return f"{feature_name} 应在 {lo} ~ {hi} 之间"
        return None

    # 分类特征:只要非空即可
    if not str(value).strip():
        return f"{feature_name} 不能为空"
    return None
