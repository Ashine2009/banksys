# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys`
- **一句话目标**:基于银行营销数据,提供交互式数据分析与在线认购预测系统。
- **使用者/受益者**:银行业务分析师、营销团队;通过数据洞察与模型预测提升定期存款认购转化率。
- **核心功能**:
  - **数据分析交互页面**:上传/加载银行营销数据,进行交互式探索、筛选、可视化(分布图、相关性、趋势等)。
  - **在线预测系统**:基于离线训练的 ML 模型,提供 Web 表单输入页面,用户输入客户特征后实时返回认购预测(yes/no)及置信度。
- **输入/数据**:
  - 来源:`data/train.csv`(22,500 行)、`data/test.csv`(7,500 行)
  - 列:age, job, marital, education, default, housing, loan, contact, month, day_of_week, duration, campaign, pdays, previous, poutcome, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed, subscribe
  - 敏感程度:**非敏感**(公开银行营销数据集,来自 UCI Machine Learning Repository)
  - 是否进 Git:**是**(数据集较小,约 30,000 行,公开数据,可直接入库)

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程指定;ML 生态成熟 |
| Web/应用框架 | Streamlit | 快速构建数据应用与交互界面;无需前后端分离;内建组件丰富 |
| 数据处理 | pandas, numpy | 表格数据处理标准库 |
| 可视化 | plotly / matplotlib | 交互式图表;Streamlit 原生兼容 |
| ML 模型 | scikit-learn (RandomForest / LogisticRegression / GradientBoosting) | 经典二分类模型;可解释性好;无需 GPU |
| 模型序列化 | joblib | 与 scikit-learn 无缝集成 |
| 测试 | pytest | 课程指定;生态第一 |
| 格式/静态检查 | ruff | 课程指定;快、统一替换 flake8+isort+black |
| 打包/运行 | Docker | 课程指定;保证环境一致性 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys/
├── standards/                     # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md      # ← 本文件
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
├── data/                          # 原始数据(公开,入库)
│   ├── train.csv
│   └── test.csv
├── app/                           # Streamlit 应用主目录(多页面)
│   ├── main.py                    # 入口:多页面导航
│   ├── pages/
│   │   ├── 1_📊_数据分析.py        # 数据分析页面
│   │   └── 2_🔮_在线预测.py        # 在线预测页面
│   └── utils.py                   # 共享工具(加载数据、预处理等)
├── model/                         # 模型训练与预测
│   ├── train.py                   # 离线训练脚本
│   ├── predict.py                 # 预测接口(加载模型+推理)
│   └── artifacts/                 # 训练产物(模型文件,不进 Git)
│       └── .gitkeep
├── tests/                         # 测试
│   ├── __init__.py
│   ├── test_data_loading.py
│   ├── test_preprocessing.py
│   ├── test_model_train.py
│   ├── test_model_predict.py
│   └── test_app.py
├── requirements.txt               # 生产运行依赖
├── requirements-dev.txt           # 本地/CI 检查依赖(pytest, ruff)
├── Dockerfile                     # 容器构建
├── .dockerignore
├── .github/workflows/
│   ├── ci.yml                     # PR 触发:ruff + pytest + docker build
│   └── cd.yml                     # main 合并触发:SSH 部署 + 健康检查
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov --cov-fail-under=80` |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | **模型 AUC ≥ 0.70**;`model/train.py` 输出 AUC 值,CI 门禁校验 |
| 应用健康检查 | Streamlit 页面 `/healthz` 端点可访问(通过 `_stcore/health` 或自定义健康检查脚本) |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 数据集(`data/*.csv`)公开且较小,**直接入库**。
- 模型产物(`model/artifacts/*.joblib`)**不进 Git**(`.gitignore` 排除)。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- Streamlit 应用端口:**容器内 8501,主机映射 8004**(端口段 8004-8010 预留回退)。
- **本地部署**(无远程服务器):合并 main 后 CD 由 GitHub Actions runner 执行本地 `docker build` + `docker run`;健康检查通过 `curl localhost:8004`。用户也可手动 `docker compose up` 或直接 `streamlit run`。

## 6. 部署/CI 占位符取值

> 本项目**无远程服务器**,部署在本地。CD 仅验证 `docker build` 通过+容器能启动+健康检查,不涉及 SSH。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys` | 应用名/镜像名/容器名 |
| `<PORT>` | `8004` | 服务端口(主机侧) |
| `<PORT_MAX>` | `8010` | 端口回退区间上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `_stcore/health` | Streamlit 健康检查路径 |
| `<CONTAINER_PORT>` | `8501` | 容器内 Streamlit 默认端口 |
