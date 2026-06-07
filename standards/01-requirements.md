# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含 ruff format、ruff check、pytest(覆盖率 ≥80%)、docker build。
- AC3: CI 全绿后合并 main。
- AC4: 合并 main 自动触发 CD,本地 `docker build` 通过 + 启动容器后健康检查通过(`http://localhost:8004/_stcore/health` 返回 200)。
- AC5: 无远程服务器;部署目标为本地 Docker 容器或直接 `streamlit run`,访问地址 `http://localhost:8004`。
- AC6: 提供 `docker-compose.yml`(可选)或启动脚本,一键本地拉起。
- AC7: 完成后更新 `standards/PROGRESS.md`。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行业务分析师**,
我想要 在 Web 页面上交互式地探索银行营销数据,
以便 快速了解客户特征分布、识别认购转化规律、为营销决策提供数据支撑。

验收标准:
- AC1: Given 应用已启动,When 用户打开数据分析页面,Then 页面显示数据集概览(行数、列数、各列类型、缺失值统计)。
- AC2: Given 数据已加载,When 用户选择数值型特征(如 age、duration),Then 页面显示该特征的直方图与基础统计量(均值、中位数、标准差)。
- AC3: Given 数据已加载,When 用户选择分类型特征(如 job、marital、education),Then 页面显示各类别的频数柱状图。
- AC4: Given 数据已加载,When 用户按 subscribe(yes/no) 分组查看某特征分布,Then 图表按认购结果分层着色,直观对比差异。
- AC5: Given 数据已加载,When 用户选择两个数值特征,Then 页面显示散点图,并按 subscribe 着色。
- AC6: Given 数据已加载,When 用户选择数据筛选条件(如年龄范围、职业),Then 图表和统计量按筛选条件实时更新。
- AC7: Given 数据已加载,When 用户切换到"相关性热力图"视图,Then 显示数值特征间的相关系数矩阵热力图。

技术备注:
- 使用 Streamlit 内置组件 + plotly 实现交互式图表。
- 数据从 `data/train.csv` 加载;页面须处理加载失败的友好提示。

---

### US-3 离线模型训练脚本 · 状态: Backlog

作为 **数据科学家**,
我想要 一个可复现的离线训练脚本,从银行营销数据训练二分类模型并保存,
以便 模型产物可被在线预测系统加载使用,且训练过程可审计、可复现。

验收标准:
- AC1: Given `data/train.csv` 存在,When 运行 `python model/train.py`,Then 完成数据预处理(编码分类变量、处理缺失值)并训练模型。
- AC2: Given 训练完成,When 脚本输出评估指标,Then 至少包含 AUC、Accuracy、Precision、Recall;AUC ≥ 0.70。
- AC3: Given 训练完成,When 脚本保存模型,Then 模型文件写入 `model/artifacts/` 目录(如 `model.joblib`);同时保存特征名列表供预测时对齐。
- AC4: Given 模型文件已存在,When 再次运行训练脚本,Then 覆盖旧模型并输出最新指标(幂等,无残留状态)。
- AC5: Given 测试数据 `data/test.csv` 存在,When 训练完成后在测试集上评估,Then 输出测试集 AUC 值。
- AC6: 使用 scikit-learn Pipeline(预处理 + 模型),确保训练与预测的特征处理一致。

技术备注:
- 模型选型:至少实现 LogisticRegression(基线) 与 RandomForestClassifier;通过命令行参数 `--model` 切换。
- `model/artifacts/` 目录不进 Git(已在 `.gitignore` 排除)。
- 训练脚本可接受 `--data` 参数指定数据路径,默认 `data/train.csv`。

---

### US-4 在线预测页面 · 状态: Backlog

作为 **银行客户经理**,
我想要 在 Web 页面上输入客户特征(年龄、职业、学历、经济指标等),点击预测按钮后即时获得认购倾向预测,
以便 在日常工作中快速判断客户是否有意愿认购定期存款,优先跟进高意向客户。

验收标准:
- AC1: Given 模型已训练并保存,When 用户打开在线预测页面,Then 页面显示输入表单,包含所有模型所需特征字段。
- AC2: Given 用户填写完整特征并点击"预测"按钮,When 模型推理完成,Then 页面显示预测结果(订阅/不订阅)及预测概率(置信度)。
- AC3: Given 用户未填写必填字段,When 点击预测,Then 页面显示友好的校验提示,而非程序报错。
- AC4: Given 用户输入非法值(如年龄为负数),When 点击预测,Then 页面提示具体错误字段及原因。
- AC5: Given 模型文件不存在,When 打开预测页面,Then 页面显示"模型未训练,请先运行训练脚本"的友好提示,而非 500 错误。
- AC6: Given 预测完成,When 页面显示结果,Then 同时展示本次输入的关键特征摘要,方便用户核对。

技术备注:
- 输入表单的默认值设置为各特征的中位数/众数,方便快速体验。
- 页面需调用 `model/predict.py` 中的预测函数;预测函数加载一次模型后缓存(使用 `@st.cache_resource`)。
- 分类特征使用下拉选择框,数值特征使用数字输入框或滑块。

---

### US-5 应用导航与整体体验 · 状态: Backlog

作为 **终端用户**,
我想要 在进入应用时看到清晰的页面导航,并能方便地在数据分析与预测功能之间切换,
以便 无需记住 URL 路径即可使用全部功能。

验收标准:
- AC1: Given 应用已启动,When 用户访问根路径,Then 自动重定向或默认显示数据分析页面。
- AC2: Given 用户在任意页面,When 通过侧边栏导航切换,Then 页面平滑切换到目标功能,无刷新闪烁。
- AC3: Given 应用运行中,When 请求 `/_stcore/health`,Then 返回 200 状态码(由 Streamlit 内置端点提供)。
- AC4: Given 数据文件缺失,When 应用启动,Then 首页显示明确的错误提示并指引用户检查 `data/` 目录。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑(数据加载、预处理、模型训练、预测推理)必须有单元测试;覆盖率 ≥ 80%。
- **可部署**:部署后健康检查通过;容器内端口 8501 固定,主机端口 8004(预留回退段 8005-8010)。
- **模型质量**:AUC ≥ 0.70 作为模型门禁;训练脚本输出结构化指标供 CI 解析。
- **性能**:预测接口单次响应 < 3 秒(模型加载缓存后);数据页面首次加载 < 5 秒。
