"""🔮 在线预测 — 客户认购倾向预测页面."""

import sys
from pathlib import Path

import streamlit as st

# 确保项目根目录在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from model.predict import predict, validate_input

# ===== 页面配置 =====
st.set_page_config(page_title="在线预测", page_icon="🔮", layout="wide")
st.title("🔮 在线认购预测")

st.markdown("输入客户特征,预测其是否会认购定期存款。")

# ===== 检查模型是否就绪 =====
try:
    from model.predict import get_model

    get_model()
    model_ready = True
except FileNotFoundError as e:
    st.error(f"⚠️ 模型未训练: {e}")
    st.info("请先运行以下命令训练模型:\n```bash\npython model/train.py\n```")
    model_ready = False

# ===== 输入表单 =====
with st.form("prediction_form", clear_on_submit=False):
    st.subheader("📝 客户特征输入")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**👤 个人信息**")
        age = st.number_input(
            "年龄 (age)", min_value=17, max_value=100, value=35, step=1
        )
        job = st.selectbox(
            "职业 (job)",
            [
                "admin.",
                "technician",
                "blue-collar",
                "services",
                "management",
                "retired",
                "entrepreneur",
                "self-employed",
                "housemaid",
                "unemployed",
                "student",
            ],
            index=1,
        )
        marital = st.selectbox(
            "婚姻状态 (marital)",
            ["married", "single", "divorced", "unknown"],
        )
        education = st.selectbox(
            "教育程度 (education)",
            [
                "university.degree",
                "high.school",
                "professional.course",
                "basic.9y",
                "basic.6y",
                "basic.4y",
                "unknown",
            ],
        )

    with col2:
        st.markdown("**💰 财务信息**")
        default = st.selectbox("是否有信用违约 (default)", ["no", "yes", "unknown"])
        housing = st.selectbox("是否有住房贷款 (housing)", ["no", "yes", "unknown"])
        loan = st.selectbox("是否有个人贷款 (loan)", ["no", "yes", "unknown"])

        st.markdown("**📞 联系信息**")
        contact = st.selectbox("联系方式 (contact)", ["cellular", "telephone"])
        month = st.selectbox(
            "最后联系月份 (month)",
            [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ],
            index=4,
        )
        day_of_week = st.selectbox(
            "最后联系星期 (day_of_week)",
            ["mon", "tue", "wed", "thu", "fri"],
        )

    with col3:
        st.markdown("**📊 活动指标**")
        duration = st.number_input(
            "通话时长/秒 (duration)",
            min_value=0,
            max_value=5000,
            value=300,
            step=10,
            help="与客户最后一次通话的持续时间(秒)",
        )
        campaign = st.number_input(
            "活动联系次数 (campaign)",
            min_value=1,
            max_value=50,
            value=2,
            step=1,
            help="本次活动期间联系该客户的次数",
        )
        pdays = st.number_input(
            "上次联系间隔 (pdays)",
            min_value=0,
            max_value=999,
            value=999,
            step=1,
            help="距上次活动联系的天数;999=之前未联系过",
        )
        previous = st.number_input(
            "之前联系次数 (previous)",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            help="本次活动之前联系该客户的次数",
        )
        poutcome = st.selectbox(
            "上次活动结果 (poutcome)",
            ["nonexistent", "failure", "success"],
        )

    st.divider()
    st.subheader("📈 经济指标")

    col4, col5 = st.columns(2)

    with col4:
        emp_var_rate = st.slider(
            "就业变化率 (emp_var_rate)",
            min_value=-3.5,
            max_value=3.0,
            value=-1.8,
            step=0.1,
        )
        cons_price_index = st.slider(
            "消费价格指数 (cons_price_index)",
            min_value=85.0,
            max_value=100.0,
            value=93.5,
            step=0.01,
        )
        cons_conf_index = st.slider(
            "消费者信心指数 (cons_conf_index)",
            min_value=-55.0,
            max_value=-25.0,
            value=-40.0,
            step=0.1,
        )

    with col5:
        lending_rate3m = st.slider(
            "3个月拆借利率 (lending_rate3m)",
            min_value=0.5,
            max_value=6.0,
            value=3.5,
            step=0.01,
        )
        nr_employed = st.slider(
            "雇员数(千) (nr_employed)",
            min_value=4800.0,
            max_value=5400.0,
            value=5100.0,
            step=0.1,
        )

    submitted = st.form_submit_button(
        "🚀 预测认购倾向", type="primary", use_container_width=True
    )

# ===== 预测结果 =====
if submitted:
    if not model_ready:
        st.error("模型未就绪,无法预测。")
    else:
        features = {
            "age": age,
            "job": job,
            "marital": marital,
            "education": education,
            "default": default,
            "housing": housing,
            "loan": loan,
            "contact": contact,
            "month": month,
            "day_of_week": day_of_week,
            "duration": duration,
            "campaign": campaign,
            "pdays": pdays,
            "previous": previous,
            "poutcome": poutcome,
            "emp_var_rate": emp_var_rate,
            "cons_price_index": cons_price_index,
            "cons_conf_index": cons_conf_index,
            "lending_rate3m": lending_rate3m,
            "nr_employed": nr_employed,
        }

        # 前端校验
        errors = []
        for name, value in features.items():
            err = validate_input(value, name)
            if err:
                errors.append(err)

        if errors:
            st.error("❌ 输入校验未通过:")
            for e in errors:
                st.warning(f"• {e}")
        else:
            try:
                with st.spinner("🔮 预测中..."):
                    result = predict(features)

                st.divider()
                st.subheader("📋 预测结果")

                col_r1, col_r2, col_r3 = st.columns(3)

                is_yes = result["prediction"] == "yes"
                with col_r1:
                    if is_yes:
                        st.success("### ✅ 会认购")
                    else:
                        st.error("### ❌ 不会认购")

                with col_r2:
                    st.metric(
                        "认购概率",
                        f"{result['probability']:.2%}",
                    )

                with col_r3:
                    st.metric(
                        "置信度",
                        f"{result['confidence']:.2%}",
                    )

                # 概率条
                st.progress(result["probability"])

                # 关键特征摘要
                st.divider()
                st.caption("📝 本次输入关键特征摘要:")
                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("年龄", age)
                with summary_cols[1]:
                    st.metric("职业", job)
                with summary_cols[2]:
                    st.metric("通话时长", f"{duration}s")
                with summary_cols[3]:
                    st.metric("上次结果", poutcome)

            except Exception as e:
                st.error(f"预测失败: {e}")
