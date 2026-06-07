"""离线训练脚本 — 训练银行营销认购预测模型.

Usage:
    python model/train.py                    # 默认 RandomForest
    python model/train.py --model lr         # LogisticRegression 基线
    python model/train.py --data data/train.csv  # 指定训练数据
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ===== 路径常量 =====
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "model" / "artifacts"
TARGET_COL = "subscribe"

# 特征列(不含目标列和 id)
FEATURE_COLS = [
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

# ===== 数据加载 =====


def load_data(data_path: str) -> tuple[pd.DataFrame, pd.Series]:
    """加载数据并分离特征与目标。

    Returns:
        (X, y): 特征 DataFrame 与目标 Series(0/1 编码)。
    """
    df = pd.read_csv(data_path)

    # 过滤出存在的特征列
    available_cols = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available_cols].copy()
    y = df[TARGET_COL].map({"yes": 1, "no": 0})

    if y.isnull().any():
        raise ValueError(f"目标列 {TARGET_COL} 含未知值: {df[TARGET_COL].unique()}")

    return X, y


# ===== 预处理 Pipeline =====


def build_preprocessor() -> ColumnTransformer:
    """构建特征预处理器。

    - 数值列标准化
    - 分类列 OneHot 编码(处理未知类别)
    """
    numeric_cols = [
        "age",
        "duration",
        "campaign",
        "pdays",
        "previous",
        "emp_var_rate",
        "cons_price_index",
        "cons_conf_index",
        "lending_rate3m",
        "nr_employed",
    ]
    categorical_cols = [
        "job",
        "marital",
        "education",
        "default",
        "housing",
        "loan",
        "contact",
        "month",
        "day_of_week",
        "poutcome",
    ]

    # 仅处理数据中实际存在的列
    numeric_cols = [c for c in numeric_cols if c in FEATURE_COLS]
    categorical_cols = [c for c in categorical_cols if c in FEATURE_COLS]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_cols,
            ),
        ]
    )
    return preprocessor


# ===== 模型工厂 =====


def build_model(model_type: str = "rf", random_state: int = 42):
    """创建分类器。

    Args:
        model_type: "lr" (LogisticRegression) 或 "rf" (RandomForest).
        random_state: 随机种子。

    Returns:
        sklearn 分类器实例。
    """
    if model_type == "lr":
        return LogisticRegression(max_iter=2000, random_state=random_state)
    elif model_type == "rf":
        return RandomForestClassifier(
            n_estimators=100, max_depth=15, random_state=random_state, n_jobs=-1
        )
    else:
        raise ValueError(f"未知模型类型: {model_type}, 可选 lr / rf")


# ===== 评估函数 =====


def evaluate_model(model, X, y_true) -> dict:
    """评估模型并返回指标字典。

    Args:
        model: 已训练的 Pipeline 或分类器。
        X: 特征。
        y_true: 真实标签(0/1)。

    Returns:
        dict: {"auc": ..., "accuracy": ..., "precision": ..., "recall": ..., "f1": ...}
    """
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
    }
    if y_proba is not None:
        metrics["auc"] = round(roc_auc_score(y_true, y_proba), 4)

    return metrics


# ===== 主训练流程 =====


def train(
    data_path: str = str(DATA_DIR / "train.csv"),
    test_path: str = str(DATA_DIR / "test.csv"),
    model_type: str = "rf",
    random_state: int = 42,
) -> dict:
    """完整训练流程:加载→预处理→训练→评估→保存。

    Returns:
        dict: 包含 train_metrics, test_metrics, model_path, feature_names。
    """
    print(f"📂 加载训练数据: {data_path}")
    X, y = load_data(data_path)

    print(f"📊 训练集: {len(X)} 条, 正样本率 {y.mean():.2%}")

    # 构建 Pipeline
    preprocessor = build_preprocessor()
    classifier = build_model(model_type, random_state)
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )

    # 训练
    print(f"🏋️ 训练模型: {model_type}")
    pipeline.fit(X, y)

    # 训练集评估
    train_metrics = evaluate_model(pipeline, X, y)
    print(f"📈 训练集指标: {train_metrics}")

    # AUC 门禁检查
    auc = train_metrics.get("auc")
    if auc is None:
        print("⚠️ 模型不支持 predict_proba,跳 AUC 门禁。")
    elif auc < 0.70:
        print(f"❌ AUC={auc:.4f} < 0.70,训练未通过质量门禁!")
        sys.exit(1)
    else:
        print(f"✅ AUC={auc:.4f} ≥ 0.70,质量门禁通过。")

    # 测试集评估(仅当测试集包含目标列时)
    test_metrics = {}
    test_path_obj = Path(test_path)
    if test_path_obj.exists():
        test_df = pd.read_csv(test_path)
        if TARGET_COL in test_df.columns:
            print(f"📂 加载测试数据: {test_path}")
            X_test, y_test = load_data(test_path)
            test_metrics = evaluate_model(pipeline, X_test, y_test)
            print(f"📈 测试集指标: {test_metrics}")
        else:
            print(f"⚠️ 测试数据不含目标列 '{TARGET_COL}',跳过评估,仅做训练集验证。")
    else:
        print("⚠️ 测试数据不存在,跳过测试集评估。")

    # 保存模型
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACTS_DIR / "model.joblib"
    joblib.dump(pipeline, model_path)
    print(f"💾 模型已保存: {model_path}")

    # 保存特征名(供预测时对齐)
    feature_names = list(X.columns)
    feature_path = ARTIFACTS_DIR / "feature_names.json"
    with open(feature_path, "w", encoding="utf-8") as f:
        json.dump(feature_names, f, ensure_ascii=False)
    print(f"💾 特征名已保存: {feature_path}")

    # 汇总结果
    result = {
        "model_type": model_type,
        "train_rows": len(X),
        "positive_rate": round(y.mean(), 4),
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "model_path": str(model_path),
        "feature_names": feature_names,
    }
    return result


# ===== CLI =====


def main():
    parser = argparse.ArgumentParser(description="训练银行营销认购预测模型")
    parser.add_argument(
        "--model",
        choices=["lr", "rf"],
        default="rf",
        help="模型类型: lr=LogisticRegression, rf=RandomForest (默认: rf)",
    )
    parser.add_argument(
        "--data",
        default=str(DATA_DIR / "train.csv"),
        help="训练数据路径 (默认: data/train.csv)",
    )
    parser.add_argument(
        "--test",
        default=str(DATA_DIR / "test.csv"),
        help="测试数据路径 (默认: data/test.csv)",
    )
    parser.add_argument("--seed", type=int, default=42, help="随机种子 (默认: 42)")
    args = parser.parse_args()

    result = train(
        data_path=args.data,
        test_path=args.test,
        model_type=args.model,
        random_state=args.seed,
    )

    print("\n📊 ====== 训练结果汇总 ======")
    print(json.dumps(result["train_metrics"], indent=2))
    if result["test_metrics"]:
        print(json.dumps(result["test_metrics"], indent=2))
    print(f"模型文件: {result['model_path']}")


if __name__ == "__main__":
    main()
