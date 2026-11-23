# 仓库内发现、使用与安装

维护、预览或提交本仓库文档前，定位 Git 根目录并读取其中的 `skills/clickzetta-doc-submit/SKILL.md`。本文件中的路径均相对于 Git 根目录，而不是当前 Markdown 所在目录。

## 本地没有安装时

skill 已随仓库 clone / pull 到本地，包含脚本、参考规则及预览工具；本次直接读取并使用仓库内这份即可，不额外 clone 文档库或要求全局安装后才能开始。告诉用户：“本仓库自带文档提交 skill，本次先使用仓库内版本；建议安装到当前 Agent 的技能目录，后续可直接调用。”只提醒一次，不等待安装回复，不把安装变成文档提交门槛。

用户选择安装时，从仓库根目录运行以下对应命令之一；不能因读取本说明就擅自写用户级配置或安装到所有运行时：

```bash
# Codex：CODEX_HOME/skills，未设置时为 ~/.codex/skills
python3 skills/clickzetta-doc-submit/scripts/install_skill.py --runtime codex
# Claude Code：~/.claude/skills
python3 skills/clickzetta-doc-submit/scripts/install_skill.py --runtime claude
# 兼容运行时：~/.agents/skills
python3 skills/clickzetta-doc-submit/scripts/install_skill.py --runtime agents
```

安装器只使用 Python 标准库，不联网，不安装 Python 依赖，不复制缓存或个人配置。已有相同版本时保持原样；已有不同版本时先说明差异，不覆盖本地定制。用户选择更新后加 `--update`，原目录会完整保留到运行时根目录下的 `skill-backups/`，带时间戳且位于 `skills/` 之外，避免备份被发现为同名技能。安装后刷新技能列表或开启新会话，当前会话仍可使用仓库内版本。

已安装时仍以当前仓库提交的 skill 作为本次协作约定；发现版本不同，提示按需更新，不自动覆盖安装目录。依赖环境只在运行相应工具时按 SKILL.md 配置；纯预览不要求 Gerrit 账号、不 fetch、不提交。

如果只有此入口而 skill 目录缺失，先检查是否处于旧分支、稀疏 checkout 或不完整工作副本。保护已有改动后从本仓库对应远端主分支获取缺少的 skill 文件，不切换 origin、不丢弃改动、不用维护者个人账号。无法获取时明确报告缺失及未完成的检查，不能声称已经按 skill 检查通过。

## 维护和提交规则

- 继续遵循原有内容质量与 SQL 验证规范；文档仓库路径、提交目标、图片、导航、引用检查及索引维护以仓库内 skill 的当前规则为准。
- SUMMARY 本次引入的失效链接、漏登记和重复等错误，以及图片完整性错误，需要修复后再提交。历史问题和明确的未注册例外按 skill 处理。
- 其他文档引用和 LLM 索引检查给可选建议；未选择修复不阻断文档提交，不全库重写，不改品牌事实文件。
- 旧中文 / 英文 TopThink 仍分别提交到自己的 `master`；常规文档变更还须提交到对应中文 `clickzetta-docs` / 英文 `singdata-docs-en` 的 Gerrit。两个 Gerrit 各自 `main`，默认送审；中文仓库历史英文目录不能作为新英文提交目标。
- 按用户本次授权范围操作，不因本入口而自动推送、改远端或扩大语言范围。仅阅读 / 预览不触发提交流程。
- Gerrit 用户名、仓库绝对路径等个人设置放在 `~/.config/clickzetta-doc-submit/config.json`，不写进共享 skill。

`AGENTS.md` 是跨 Agent 的入口。`CLAUDE.md` 为 Claude Code 保留兼容入口；新仓库根文件可用 `@AGENTS.md` 导入，已有长篇质量规范保留，只在开头导入本文件，避免再复制一份提交规则。这些 Agent 文件和 skill 都是协作支持文件，不加入产品 `SUMMARY.md` 或 LLM 页面索引。
