# PROGRESS · banksys 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**:`初始化`
- **上一步完成**:项目上下文与需求文档已编写,待人类确认。
- **下一步 (TODO 第一条)**:人类确认需求后,执行第①步——确认/创建 GitHub 仓库(本地部署,无需 SSH Secrets)。
- **阻塞项**:`等待人类确认 00-project-context.md 与 01-requirements.md 内容无误`

---

## 待办清单 (TODO,按优先级)

- [ ] **第①步**:确认/创建 GitHub 仓库(`gh repo create`);本地部署无需 SSH Secrets。
- [ ] **第②步**:从 `main` 开 feature 分支 `feature/1-project-init`,完成项目骨架初始化。
- [ ] **第③步-模块1**:项目骨架 — 创建目录结构、`requirements.txt`、`requirements-dev.txt`、`.gitignore`、`Dockerfile`、`README.md`;更新 PROGRESS。
- [ ] **第③步-模块2**:数据加载模块 — `app/utils.py`:加载 CSV、基础统计;对应测试 `tests/test_data_loading.py`。
- [ ] **第③步-模块3**:数据分析页面 — `app/pages/1_📊_数据分析.py`:数据集概览、直方图、柱状图、散点图、热力图、筛选;对应测试 `tests/test_app.py`。
- [ ] **第③步-模块4**:模型训练 — `model/train.py`:预处理 Pipeline + LogisticRegression/RandomForest + 评估指标(AUC≥0.70) + 保存模型;对应测试 `tests/test_model_train.py`。
- [ ] **第③步-模块5**:模型预测 — `model/predict.py`:加载模型 + 推理函数;对应测试 `tests/test_model_predict.py`。
- [ ] **第③步-模块6**:在线预测页面 — `app/pages/2_🔮_在线预测.py`:输入表单 + 校验 + 预测结果展示;更新测试。
- [ ] **第③步-模块7**:应用入口 — `app/main.py`:多页面导航;健康检查确认。
- [ ] **第④步**:本地 CI 自检 — `ruff format --check .` + `ruff check .` + `pytest --cov --cov-fail-under=80` + 模型 AUC 门禁脚本;全绿后进入第⑤步。
- [ ] **第⑤步**:推送 feature 分支,`gh pr create` 创建 PR;盯 CI(含 `docker build`)全绿。
- [ ] **第⑥步**:等待人工 Review 与 Merge;合并后 CD 执行本地 `docker build` + `docker run`,验证 `http://localhost:8004/_stcore/health` 返回 200。

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-07 | 数据集直接入库(`data/*.csv`) | 公开数据,约 30k 行,体积小,方便 CI 直接使用 |
| 2026-06-07 | 端口采用 8004(回退 8005-8010) | 按用户要求;预留 7 个端口应对占用 |
| 2026-06-07 | 模型产物不入库(`model/artifacts/`) | 二进制文件,CI/CD 中由训练脚本生成;`.gitignore` 排除 |
| 2026-06-07 | 两功能合并在一个 Streamlit 多页面应用 | 避免多服务运维复杂度;Streamlit 原生支持多页面;用户在一个端口即可使用全部功能 |
| 2026-06-07 | 模型基线选 LogisticRegression + RandomForest | 可解释性强,适合教学;无需 GPU;scikit-learn 生态成熟 |
| 2026-06-07 | 本地部署,无远程服务器 | 用户确认无服务器;CD 退化为本地 docker build + run;无需 SSH Secrets;健康检查用 localhost |

---

## 已知坑 (GOTCHAS)

- _暂无(项目刚初始化,坑将在开发中记录)_

---

## 里程碑 (DONE)

- [x] 编写并填充 `standards/00-project-context.md`(项目上下文)
- [x] 编写并填充 `standards/01-requirements.md`(5 个用户故事 + 验收标准)
- [x] 初始化 `standards/PROGRESS.md`(第一批 TODO + ADR)
