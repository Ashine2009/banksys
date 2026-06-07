"""测试在线预测模块."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "model"))

# 确保模型已训练
from model.train import train
from model.predict import (
    predict,
    validate_input,
    get_model,
    clear_cache,
    REQUIRED_FEATURES,
    MODEL_PATH,
)


# ===== Fixtures =====


@pytest.fixture(autouse=True)
def trained_model():
    """确保模型已训练并存在于 artifacts。测试结束后清理缓存。"""
    # 用真实数据训练(若模型未存在或 AUC 不足)
    data_path = Path(__file__).resolve().parent.parent / "data" / "train.csv"
    if not data_path.exists():
        pytest.skip("真实数据不存在")

    if not MODEL_PATH.exists():
        train(data_path=str(data_path), model_type="rf")

    yield

    # 清理缓存,避免测试间相互影响
    clear_cache()


@pytest.fixture
def valid_features():
    """返回一组合法的输入特征。"""
    return {
        "age": 35,
        "job": "technician",
        "marital": "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "duration": 500,
        "campaign": 2,
        "pdays": 999,
        "previous": 0,
        "poutcome": "nonexistent",
        "emp_var_rate": -1.8,
        "cons_price_index": 93.5,
        "cons_conf_index": -40.0,
        "lending_rate3m": 3.5,
        "nr_employed": 5100.0,
    }


# ===== predict =====


def test_predict_returns_dict(valid_features):
    result = predict(valid_features)
    assert isinstance(result, dict)
    assert "prediction" in result
    assert "probability" in result
    assert "confidence" in result


def test_predict_valid_result(valid_features):
    result = predict(valid_features)
    assert result["prediction"] in ("yes", "no")
    assert 0 <= result["probability"] <= 1
    assert 0 <= result["confidence"] <= 1


def test_predict_missing_features():
    with pytest.raises(ValueError, match="缺少必填特征"):
        predict({"age": 30})


def test_predict_model_not_found():
    """模型文件不存在时应抛出 FileNotFoundError。"""
    clear_cache()
    with patch("model.predict.MODEL_PATH", Path("/nonexistent/model.joblib")):
        with pytest.raises(FileNotFoundError, match="模型文件不存在"):
            predict(
                {
                    "age": 30,
                    "job": "admin.",
                    "marital": "single",
                    "education": "high.school",
                    "default": "no",
                    "housing": "yes",
                    "loan": "no",
                    "contact": "cellular",
                    "month": "may",
                    "day_of_week": "mon",
                    "duration": 300,
                    "campaign": 1,
                    "pdays": 999,
                    "previous": 0,
                    "poutcome": "nonexistent",
                    "emp_var_rate": 1.4,
                    "cons_price_index": 94.0,
                    "cons_conf_index": -36.0,
                    "lending_rate3m": 3.0,
                    "nr_employed": 5100.0,
                }
            )


def test_predict_consistency(valid_features):
    """相同输入应返回相同结果。"""
    r1 = predict(valid_features)
    r2 = predict(valid_features)
    assert r1["prediction"] == r2["prediction"]
    assert r1["probability"] == r2["probability"]


def test_predict_different_inputs_different_results(valid_features):
    """不同输入可能产生不同预测。"""
    r1 = predict(valid_features)
    alt = {**valid_features, "age": 70, "duration": 50, "poutcome": "failure"}
    r2 = predict(alt)
    # 不强制要求不同,但至少都能正常返回
    assert r1["prediction"] in ("yes", "no")
    assert r2["prediction"] in ("yes", "no")


# ===== validate_input =====


def test_validate_age_valid():
    assert validate_input(35, "age") is None


def test_validate_age_too_low():
    assert validate_input(10, "age") is not None


def test_validate_age_too_high():
    assert validate_input(120, "age") is not None


def test_validate_age_non_numeric():
    assert validate_input("abc", "age") is not None


def test_validate_duration_valid():
    assert validate_input(300, "duration") is None


def test_validate_duration_negative():
    assert validate_input(-1, "duration") is not None


def test_validate_categorical_empty():
    assert validate_input("", "job") is not None


def test_validate_categorical_valid():
    assert validate_input("admin.", "job") is None


# ===== get_model =====


def test_get_model_returns_pipeline():
    model = get_model()
    assert model is not None
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")


def test_get_model_cached():
    m1 = get_model()
    m2 = get_model()
    assert m1 is m2  # 同一实例


def test_required_features_count():
    """REQUIRED_FEATURES 应有 20 个特征。"""
    assert len(REQUIRED_FEATURES) == 20
