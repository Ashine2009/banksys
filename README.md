# banksys — 银行营销数据分析与在线认购预测系统

基于 Streamlit 的银行营销数据交互式分析与机器学习预测应用。

## 功能

| 功能 | 说明 |
|---|---|
| 📊 数据分析 | 交互式 EDA:特征分布、相关性热力图、按认购结果分组对比、实时筛选 |
| 🔮 在线预测 | 输入客户特征,实时返回定期存款认购预测(yes/no)与置信度 |

## 技术栈

- **Python 3.11** + **Streamlit** — Web 应用框架
- **scikit-learn** — 机器学习模型(LogisticRegression / RandomForest)
- **pandas + plotly** — 数据处理与可视化
- **pytest + ruff** — 测试与代码质量
- **Docker** — 容器化部署
- **GitHub Actions** — CI/CD

## 快速开始

### 本地运行(无需 Docker)

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. 训练模型
python model/train.py

# 3. 启动应用
streamlit run app/main.py --server.port 8004
```

访问 http://localhost:8004

### Docker 运行

```bash
# 构建并运行(主机端口 8004 → 容器 8501)
docker build -t banksys:latest .
docker run -d --name banksys --restart unless-stopped -p 8004:8501 banksys:latest

# 健康检查
curl http://localhost:8004/_stcore/health
```

## 项目结构

```text
banksys/
├── app/                    # Streamlit 应用
│   ├── main.py             # 入口 + 导航
│   ├── pages/              # 多页面
│   └── utils.py            # 共享工具
├── model/                  # ML 模型
│   ├── train.py            # 离线训练脚本
│   ├── predict.py          # 预测推理
│   └── artifacts/          # 模型产物(不进 Git)
├── data/                   # 银行营销数据集
├── tests/                  # 单元测试
├── standards/              # 项目规范与活记忆
├── .github/workflows/      # CI/CD
├── Dockerfile
└── requirements.txt
```

## 开发

```bash
pip install -r requirements-dev.txt   # 含 pytest + ruff
ruff format --check .                 # 格式检查
ruff check .                          # 静态检查
pytest --cov --cov-fail-under=80     # 测试 + 覆盖率
```

## 部署

合并 `main` 后 CD 自动执行 `docker build` + `docker run` + 健康检查,端口 8004。
