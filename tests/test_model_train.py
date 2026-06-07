"""测试模型训练脚本."""

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "model"))

from model.train import (
    load_data,
    build_preprocessor,
    build_model,
    evaluate_model,
    train,
    ARTIFACTS_DIR,
    TARGET_COL,
)


# ===== Fixtures =====


@pytest.fixture
def small_csv():
    """创建小型 CSV 供训练测试(含所有特征列+目标)。"""
    np.random.seed(42)
    n = 200
    data = {
        "age": np.random.randint(20, 70, n),
        "job": np.random.choice(["admin.", "technician", "blue-collar", "services"], n),
        "marital": np.random.choice(["married", "single", "divorced"], n),
        "education": np.random.choice(
            ["high.school", "university.degree", "basic.9y"], n
        ),
        "default": np.random.choice(["no", "yes"], n, p=[0.8, 0.2]),
        "housing": np.random.choice(["no", "yes"], n),
        "loan": np.random.choice(["no", "yes"], n),
        "contact": np.random.choice(["cellular", "telephone"], n),
        "month": np.random.choice(["may", "jul", "aug", "jun", "nov", "apr"], n),
        "day_of_week": np.random.choice(["mon", "tue", "wed", "thu", "fri"], n),
        "duration": np.random.randint(0, 4000, n),
        "campaign": np.random.randint(1, 30, n),
        "pdays": np.random.randint(0, 999, n),
        "previous": np.random.randint(0, 5, n),
        "poutcome": np.random.choice(["nonexistent", "failure", "success"], n),
        "emp_var_rate": np.random.uniform(-3, 2, n),
        "cons_price_index": np.random.uniform(90, 100, n),
        "cons_conf_index": np.random.uniform(-50, -30, n),
        "lending_rate3m": np.random.uniform(0.5, 5, n),
        "nr_employed": np.random.uniform(4900, 5300, n),
        TARGET_COL: np.random.choice(["no", "yes"], n, p=[0.7, 0.3]),
    }
    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f, index=False)
        return Path(f.name)


@pytest.fixture
def real_train_path():
    """真实训练数据路径。"""
    p = Path(__file__).resolve().parent.parent / "data" / "train.csv"
    if p.exists():
        return str(p)
    pytest.skip("真实数据不存在")


# ===== load_data =====


def test_load_data_synthetic(small_csv):
    X, y = load_data(str(small_csv))
    assert len(X) == 200
    assert len(y) == 200
    assert set(y.unique()).issubset({0, 1})
    assert TARGET_COL not in X.columns


def test_load_data_real(real_train_path):
    X, y = load_data(real_train_path)
    assert len(X) == 22500
    assert len(y) == 22500
    assert y.isin([0, 1]).all()


# ===== build_preprocessor =====


def test_build_preprocessor():
    preprocessor = build_preprocessor()
    assert preprocessor is not None
    assert hasattr(preprocessor, "fit_transform")


def test_preprocessor_fit_transform(small_csv):
    X, y = load_data(str(small_csv))
    preprocessor = build_preprocessor()
    X_t = preprocessor.fit_transform(X)
    assert X_t.shape[0] == len(X)
    assert X_t.shape[1] > len(X.columns)  # one-hot 后列数更多


# ===== build_model =====


def test_build_model_lr():
    model = build_model("lr")
    from sklearn.linear_model import LogisticRegression

    assert isinstance(model, LogisticRegression)


def test_build_model_rf():
    model = build_model("rf")
    from sklearn.ensemble import RandomForestClassifier

    assert isinstance(model, RandomForestClassifier)


def test_build_model_unknown():
    with pytest.raises(ValueError, match="未知模型类型"):
        build_model("xgboost")


# ===== evaluate_model =====


def test_evaluate_model(small_csv):
    X, y = load_data(str(small_csv))
    preprocessor = build_preprocessor()
    classifier = build_model("rf")
    from sklearn.pipeline import Pipeline

    pipeline = Pipeline([("prep", preprocessor), ("clf", classifier)])
    pipeline.fit(X, y)
    metrics = evaluate_model(pipeline, X, y)
    assert "accuracy" in metrics
    assert "auc" in metrics
    assert 0 <= metrics["auc"] <= 1
    assert 0 <= metrics["accuracy"] <= 1


# ===== train 集成测试 =====


def test_train_full_pipeline_rf(small_csv):
    """完整训练流程(RandomForest)应在合成数据上成功。"""
    result = train(
        data_path=str(small_csv),
        test_path=str(small_csv),  # 用同一份数据当测试集
        model_type="rf",
    )
    assert "train_metrics" in result
    assert result["train_metrics"]["auc"] >= 0.70
    assert "test_metrics" in result
    assert Path(result["model_path"]).exists()


def test_train_full_pipeline_lr(small_csv):
    """完整训练流程(LogisticRegression)。"""
    result = train(
        data_path=str(small_csv),
        test_path=str(small_csv),
        model_type="lr",
    )
    assert result["train_metrics"]["auc"] >= 0.70


def test_train_saves_artifacts(small_csv):
    """训练后应保存模型和特征名文件。"""
    # 清理旧产物
    for f in ARTIFACTS_DIR.glob("*.joblib"):
        f.unlink()
    for f in ARTIFACTS_DIR.glob("*.json"):
        f.unlink()

    train(data_path=str(small_csv), test_path=str(small_csv), model_type="rf")

    model_file = ARTIFACTS_DIR / "model.joblib"
    feature_file = ARTIFACTS_DIR / "feature_names.json"

    assert model_file.exists()
    assert feature_file.exists()

    with open(feature_file) as f:
        features = json.load(f)
    assert isinstance(features, list)
    assert len(features) > 0


def test_train_idempotent(small_csv):
    """多次训练应覆盖旧模型,不报错。"""
    train(data_path=str(small_csv), test_path=str(small_csv), model_type="rf")
    train(data_path=str(small_csv), test_path=str(small_csv), model_type="rf")
    # 不应抛出异常
    assert True
