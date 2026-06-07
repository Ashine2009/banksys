# PROGRESS · banksys 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**:`PR 已发起,等待 CI 与人工 Review`
- **上一步完成**:PR #1 已创建,等待 CI 运行。
- **下一步 (TODO 第一条)**:人类 Review PR #1 → 确认 CI 全绿 → 人工合并 main。
- **阻塞项**:`等待人类 Review 与 Merge(本地部署无需 Secrets)`

---

## 待办清单 (TODO,按优先级)

- [x] **第①步**:创建 GitHub 仓库 — https://github.com/Ashine2009/banksys ✅
- [x] **第②步**:开 feature 分支 `feature/1-project-init` ✅
- [x] **第③步-模块1**:项目骨架 — 目录结构、依赖、Dockerfile、CI/CD、README ✅
- [x] **第③步-模块2**:数据加载模块 — `app/utils.py` + 10 tests ✅
- [x] **第③步-模块3**:数据分析页面 — `app/pages/1_📊_数据分析.py` + 10 tests ✅
- [x] **第③步-模块4**:模型训练 — `model/train.py` (AUC 0.98) + 12 tests ✅
- [x] **第③步-模块5**:模型预测 — `model/predict.py` + 17 tests ✅
- [x] **第③步-模块6**:在线预测页面 — `app/pages/2_🔮_在线预测.py` ✅
- [x] **第③步-模块7**:应用入口 — `app/main.py` + 导航 ✅
- [x] **第④步**:本地 CI 自检 — ruff ✅ | pytest 49/49 ✅ | coverage 94% ✅ | AUC 0.98 ✅
- [x] **第⑤步**:PR #1 已创建 — https://github.com/Ashine2009/banksys/pull/1
- [ ] **第⑥步**:等待人工 Review → 人工 Merge → CD 自动部署 → 验证 `http://localhost:8004/_stcore/health`

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
| 2026-06-07 | test.csv 不含 subscribe 列 | 原始测试数据无目标列,训练脚本自动检测并跳过测试集评估 |

---

## 已知坑 (GOTCHAS)

- **Windows GBK/CP936 编码**:`pip install` 或 `python` 输出含特殊字符时可能报 `UnicodeDecodeError: 'gbk'`;解决:命令前加 `PYTHONUTF8=1` 或 `chcp 65001`。
- **pandas EmptyDataError**:空 CSV 文件直接触发 `pd.errors.EmptyDataError` 而非返回空 DataFrame;`load_csv` 已 catch 并转为 `ValueError`。

---

## 里程碑 (DONE)

- [x] 编写并填充 `standards/00-project-context.md`(项目上下文)
- [x] 编写并填充 `standards/01-requirements.md`(5 个用户故事 + 验收标准)
- [x] 初始化 `standards/PROGRESS.md`(第一批 TODO + ADR)
- [x] 创建 GitHub 仓库并推送 main
- [x] 实现 7 个模块,49 个测试,94% 覆盖率
- [x] 本地 CI 自检全绿(ruff + pytest + coverage + AUC)
- [x] 发起 PR #1
