"""banksys — 银行营销数据分析与在线认购预测系统 入口."""

import streamlit as st

# ===== 页面配置 =====
st.set_page_config(
    page_title="banksys · 银行营销分析与预测",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== 首页内容 =====
st.title("🏦 banksys — 银行营销数据分析与认购预测系统")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 📊 数据分析
        交互式探索银行营销数据集,了解客户特征分布与认购转化规律。

        **功能:**
        - 数据集概览与缺失值检测
        - 特征分布直方图与柱状图
        - 按认购结果分组对比
        - 散点图与趋势线
        - 相关性热力图
        - 实时筛选与交叉分析

        👈 在侧边栏选择 **📊 数据分析** 开始探索
    """
    )

with col2:
    st.markdown(
        """
        ### 🔮 在线预测
        基于机器学习模型,输入客户特征即时预测认购倾向。

        **功能:**
        - 客户特征输入表单(20个特征)
        - 前端输入校验
        - 实时预测(yes/no)
        - 概率与置信度输出
        - 模型未训练时友好提示

        👈 在侧边栏选择 **🔮 在线预测** 开始预测
    """
    )

st.markdown("---")

# ===== 快速状态检查 =====
st.subheader("🔍 系统状态")

status_col1, status_col2 = st.columns(2)

with status_col1:
    # 数据检查
    from app.utils import DATA_DIR

    train_path = DATA_DIR / "train.csv"
    if train_path.exists():
        st.success(f"✅ 训练数据就绪: {train_path.name}")
    else:
        st.error(f"❌ 训练数据缺失: {train_path}")

with status_col2:
    # 模型检查
    from model.predict import MODEL_PATH

    if MODEL_PATH.exists():
        st.success("✅ 模型已训练")
    else:
        st.warning("⚠️ 模型未训练 — 预测功能暂不可用")
        st.code("python model/train.py", language="bash")

st.divider()
st.caption(
    "技术栈: Python 3.11 · Streamlit · scikit-learn · plotly · Docker | 端口: 8004"
)
