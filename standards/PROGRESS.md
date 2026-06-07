# PROGRESS · banksys 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by AI)

- **阶段**:`已上线(本地)`
- **上一步完成**:PR #1 合并 main,CD 通过,本地 Docker 部署完成。
- **下一步 (TODO 第一条)**:无——首个功能闭环已完成。后续功能按 01-requirements.md 新增 US。
- **阻塞项**:`无`

---

## 待办清单 (TODO,按优先级)

- [x] **第①步**:创建 GitHub 仓库 — https://github.com/Ashine2009/banksys ✅
- [x] **第②步**:开 feature 分支 `feature/1-project-init` ✅
- [x] **第③步-模块1**:项目骨架 ✅
- [x] **第③步-模块2**:数据加载模块 ✅
- [x] **第③步-模块3**:数据分析页面 ✅
- [x] **第③步-模块4**:模型训练 ✅
- [x] **第③步-模块5**:模型预测 ✅
- [x] **第③步-模块6**:在线预测页面 ✅
- [x] **第③步-模块7**:应用入口 ✅
- [x] **第④步**:本地 CI 自检 — ruff ✅ | pytest 49/49 ✅ | coverage 94% ✅ | AUC 0.98 ✅
- [x] **第⑤步**:PR #1 创建,CI 全绿 ✅
- [x] **第⑥步**:人类 Review + Merge ✅ | CD 通过 ✅ | 本地 Docker 部署 ✅

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-07 | 数据集直接入库(`data/*.csv`) | 公开数据,约 30k 行,体积小,方便 CI 直接使用 |
| 2026-06-07 | 端口采用 8004(回退 8005-8010) | 按用户要求 |
| 2026-06-07 | 模型产物不入库(`model/artifacts/`) | `.gitignore` 排除 `*.joblib` `*.pkl` `*.json` |
| 2026-06-07 | 两功能合并在一个 Streamlit 多页面应用 | 单端口,低运维复杂度 |
| 2026-06-07 | 模型基线选 LogisticRegression + RandomForest | 可解释性强;sklearn 成熟 |
| 2026-06-07 | 本地部署,无远程服务器 | CD 仅验证 docker build+run+health |
| 2026-06-07 | test.csv 不含 subscribe 列 | 训练脚本自动检测并跳过测试集评估 |

---

## 已知坑 (GOTCHAS)

- **Windows GBK/CP936 编码**:`pip install` 或 `python` 输出含特殊字符时可能报 `UnicodeDecodeError: 'gbk'`;解决:命令前加 `PYTHONUTF8=1` 或 `chcp 65001`。
- **pandas EmptyDataError**:空 CSV 文件直接触发 `pd.errors.EmptyDataError` 而非返回空 DataFrame;`load_csv` 已 catch 转 `ValueError`。
- **CI ruff 版本差异**:本地 ruff 与 CI runner 版本可能不一致导致 format check 结果不同;推送前确保 `ruff format .` 后再 `ruff format --check .` 确认。

---

## 里程碑 (DONE)

- [x] 编写项目上下文 + 需求文档(5 个用户故事)
- [x] 初始化 PROGRESS.md
- [x] 创建 GitHub 仓库
- [x] 实现 7 个模块,49 个测试,94% 覆盖率
- [x] 本地 CI 全绿(ruff + pytest + AUC)
- [x] PR #1 发起,CI 全绿,人工合并
- [x] CD 通过,本地 Docker 部署成功
- [x] 健康检查 `http://localhost:8004/_stcore/health` 返回 200
