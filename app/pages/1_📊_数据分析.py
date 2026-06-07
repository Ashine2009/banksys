"""📊 数据分析 — 银行营销数据交互式探索页面."""

import streamlit as st
import pandas as pd
import plotly.express as px

from app.utils import (
    load_csv,
    get_basic_stats,
    get_column_types,
    get_missing_info,
    get_target_distribution,
    DATA_DIR,
)

# ===== 页面配置 =====
st.set_page_config(page_title="数据分析", page_icon="📊", layout="wide")
st.title("📊 银行营销数据分析")

# ===== 数据加载 =====
DATA_PATH = DATA_DIR / "train.csv"
TARGET_COL = "subscribe"

try:
    df = load_csv(DATA_PATH)
    st.success(f"✅ 数据加载成功 — 共 {len(df)} 条记录, {len(df.columns)} 个特征")
except (FileNotFoundError, ValueError) as e:
    st.error(f"❌ 数据加载失败: {e}")
    st.info(f"请确保 `{DATA_PATH}` 存在且非空。")
    st.stop()

# ===== 侧边栏:筛选条件 =====
st.sidebar.header("🔍 筛选条件")
col_types = get_column_types(df)

# 数值筛选
age_min, age_max = int(df["age"].min()), int(df["age"].max())
age_range = st.sidebar.slider("年龄范围", age_min, age_max, (age_min, age_max))

# 职业多选
jobs = sorted(df["job"].dropna().unique())
selected_jobs = st.sidebar.multiselect("职业(可多选)", jobs, default=jobs)

# 婚姻状态
marital_options = sorted(df["marital"].dropna().unique())
selected_marital = st.sidebar.multiselect(
    "婚姻状态", marital_options, default=marital_options
)

# ===== 应用筛选 =====
filtered_df = df[
    (df["age"] >= age_range[0])
    & (df["age"] <= age_range[1])
    & (df["job"].isin(selected_jobs))
    & (df["marital"].isin(selected_marital))
]
st.sidebar.caption(
    f"当前筛选后: {len(filtered_df)} 条记录 ({len(filtered_df) / len(df) * 100:.1f}%)"
)

# ===== 主区域:Tabs =====
tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 数据概览", "📈 特征分布", "🔬 关系探索", "🔥 相关性热力图"]
)

# ---- Tab 1: 数据概览 ----
with tab1:
    st.subheader("数据集概览")

    col_left, col_right = st.columns(2)
    with col_left:
        stats = get_basic_stats(filtered_df)
        st.metric("行数", stats["rows"])
        st.metric("列数", stats["columns"])
        st.write("**列名:**")
        st.write(stats["column_names"])

    with col_right:
        missing = get_missing_info(filtered_df)
        if len(missing) > 0:
            st.warning("⚠️ 存在缺失值")
            st.dataframe(missing, use_container_width=True)
        else:
            st.success("✅ 无缺失值")

    st.subheader("原始数据")
    st.dataframe(filtered_df, use_container_width=True, height=400)

# ---- Tab 2: 特征分布 ----
with tab2:
    st.subheader("特征分布分析")

    numeric_cols = [c for c in col_types["numeric"] if c not in ("id",)]
    categorical_cols = [c for c in col_types["categorical"] if c != TARGET_COL]

    # 数值特征直方图
    selected_num = st.selectbox("选择数值特征", numeric_cols, key="hist_num")
    show_by_target = st.checkbox(
        "按认购结果(subscribe)分层着色", value=True, key="hist_color"
    )

    fig = px.histogram(
        filtered_df,
        x=selected_num,
        color=TARGET_COL if show_by_target else None,
        barmode="overlay",
        opacity=0.7,
        marginal="box",
        title=f"{selected_num} 分布",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 基础统计
    st.caption(f"**{selected_num}** 基础统计:")
    st.write(filtered_df[selected_num].describe())

    st.divider()

    # 分类特征柱状图
    selected_cat = st.selectbox("选择分类特征", categorical_cols, key="bar_cat")
    cat_counts = filtered_df[selected_cat].value_counts().reset_index()
    cat_counts.columns = [selected_cat, "count"]

    fig_bar = px.bar(
        cat_counts,
        x=selected_cat,
        y="count",
        color=selected_cat,
        title=f"{selected_cat} 频数分布",
    )
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # 按 subscribe 分组的分类对比
    st.caption(f"**{selected_cat}** × subscribe 交叉:")
    cross = pd.crosstab(
        filtered_df[selected_cat], filtered_df[TARGET_COL], normalize="index"
    )
    st.dataframe(cross.style.format("{:.1%}"), use_container_width=True)

# ---- Tab 3: 关系探索 ----
with tab3:
    st.subheader("数值特征关系")

    col_x, col_y = st.columns(2)
    with col_x:
        x_col = st.selectbox("X 轴", numeric_cols, index=0, key="scatter_x")
    with col_y:
        # 默认选 duration 作为 Y 轴
        default_y = numeric_cols.index("duration") if "duration" in numeric_cols else 0
        y_col = st.selectbox("Y 轴", numeric_cols, index=default_y, key="scatter_y")

    fig_scatter = px.scatter(
        filtered_df,
        x=x_col,
        y=y_col,
        color=TARGET_COL,
        opacity=0.6,
        title=f"{x_col} vs {y_col} (按 subscribe 着色)",
        trendline="lowess" if len(filtered_df) > 0 else None,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 目标变量分布
    st.divider()
    st.subheader("认购结果分布")
    target_dist = get_target_distribution(filtered_df, TARGET_COL)
    dist_df = pd.DataFrame(
        {"类别": target_dist["counts"].keys(), "数量": target_dist["counts"].values()}
    )
    fig_pie = px.pie(
        dist_df,
        names="类别",
        values="数量",
        title="subscribe 分布",
        color="类别",
        color_discrete_map={"no": "#EF553B", "yes": "#00CC96"},
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ---- Tab 4: 相关性热力图 ----
with tab4:
    st.subheader("数值特征相关性矩阵")

    corr_cols = [c for c in numeric_cols if c != "id"]
    corr_matrix = filtered_df[corr_cols].corr()

    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="相关系数热力图",
    )
    fig_heatmap.update_layout(height=700)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.caption("💡 红色=正相关,蓝色=负相关;绝对值越大,相关性越强。")

# ===== 页脚 =====
st.divider()
st.caption(
    f"数据来源: {DATA_PATH} | 原始行数: {len(df)} | 当前筛选后: {len(filtered_df)}"
)
