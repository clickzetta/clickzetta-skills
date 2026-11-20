# 连接、提交与共享维护

## 地址和身份

```text
中文 SSH:  ssh://<USERNAME>@gerrit.clickzetta-inc.com:29418/clickzetta-docs
中文 HTTP: http://<USERNAME>@gerrit.clickzetta-inc.com/a/clickzetta-docs
中文 Web:  https://gerrit.clickzetta-inc.com/admin/repos/clickzetta-docs
英文 SSH:  ssh://<USERNAME>@gerrit.clickzetta-inc.com:29418/singdata-docs-en
英文 HTTP: http://<USERNAME>@gerrit.clickzetta-inc.com/a/singdata-docs-en
英文 Web:  https://gerrit.clickzetta-inc.com/admin/repos/singdata-docs-en
```

两个 Gerrit 项目各自使用 `main`；旧 TopThink 仓库仍使用 `master` 并承担常规提交，地址及双份提交流程见 [新旧仓库双份提交](dual-remote.md)。分别 clone 到不同本地目录，用 `config --language cn/en --username <USERNAME> --repo <PATH>` 保存各自新库路径；更新一种语言不覆盖另一种语言路径。历史配置的 `repo` 字段只指中文，新版另用 `repositories.cn` / `repositories.en` 保存独立路径。常规提交使用 `push-plan --language cn/en --target both`；不得对旧中文 Gerrit 仓库内的英文目录继续推送。用户要求同步旧内容时按参考说明导入，并精确比较 tree。

SSH 为默认；HTTP 地址也必须保留。若实例支持 HTTPS Git，可配置 `https`。用户名由协作者首次提供并保存在其用户目录。既存 origin 中的其他人用户名不是新协作者身份。Git 作者邮箱不能从 Gerrit 用户名推测。

推荐为这个项目维护一个仓库本地的 `docs-gerrit` remote，地址来自配置工具输出；创建或修改此命名 remote 前检查是否已经指向其他用途。也可以所有网络操作直接使用配置地址，不改 origin。网络操作前核对项目名。

同步示例（URL 必须换为当前个人配置的值）：

```bash
git fetch <个人URL> refs/heads/main
git rev-parse FETCH_HEAD
git merge-base FETCH_HEAD HEAD
```

记录 fetch 的 main commit，后续 rebase、检查和验证使用同一明确 commit。FETCH_HEAD 会被下一次 fetch 改写，不能长时间依赖其隐含值。检查器 `--base` 使用与最新 main 的 merge-base；若需要 rebase，先保护工作区，再解决冲突，不丢失原始改动。

## Change-Id hook

Gerrit 要求的 commit-msg hook 可从同一服务器获取。先检查 `git rev-parse --git-path hooks/commit-msg` 和 `core.hooksPath`，已有 hook 时先检查其用途，不直接覆盖。下载到临时文件、检查内容后再安装到 Git 实际使用的 hooks 目录；不配置全局 hooksPath。SSH 获取方式：

```bash
scp -O -P 29418 <USERNAME>@gerrit.clickzetta-inc.com:hooks/commit-msg <临时文件>
```

HTTP / HTTPS 用户可使用该实例 Gerrit Download 页面给出的同站点 hook 下载链接。维护者为这两个项目明确提供的 hook 下载地址是 `http://39.105.45.133:8084/hooks/commit-msg`，也可使用该地址；同样先下载、检查内容再安装并赋予执行权限。除此之外不要照搬页面里其他旧 IP 或不同主机的地址。HTTP 密码交给 Git 凭据管理器，不写进 clone URL、配置 JSON 或提交消息。

安装后确保 hook 可执行。为已有提交补 Change-Id 时，仅 amend 这次尚未共享的提交；已有 review 更新应保留原 Change-Id。

## 默认 Jira 前缀

使用维护者指定的默认 `#CZEE-121`，例如：

```text
#CZEE-121 Update Chinese ingestion guide

Describe the documentation change and validation.

Change-Id: I...
```

不因缺少专门工单就阻塞用户，也不把这个约定说成服务端验证豁免。实际服务器规则变化时报告拒绝。用户指定其他编号时覆盖默认值。

## 图片兼容

- 新图片集中在对应语言的 `assets/`，Markdown 引用相对于该 Markdown 文件。
- 历史 `.topwrite/assets/`、`asset/`、根目录图片保留，不批量移动。
- `.topwrite/assets/** -filter -diff -merge -text` 仍保留。新 assets 不配置 LFS；检查 `git check-attr filter -- <新图片>`，若从全局 attributes 继承 LFS，为所选语言的 `assets/**` 添加明确的 `-filter -diff -merge -text` 并一并审阅。
- 文档下沉到子目录后要调整相对图片引用及 SUMMARY；正文链接尽量核对，给可选建议。
- 解析代码示例时忽略 fenced code / inline code。标准 Markdown、引用式图片、HTML img 和 TopWrite 宽度后缀都需识别。
- 历史错误与本次新增错误分别呈现；被本次删除或移动的图片仍有引用时必须修复，其他文档的入站链接按可选建议处理。
- Gerrit 存储和评审不等价于网站发布。旧平台居中 / 宽度语法在新网站如何展示取决于网站渲染器，skill 不承诺官网渲染效果。

## 安装与更新共享 skill

四个仓库根的整个 `skills/clickzetta-doc-submit/` 是相同的可分发包，没有个人配置。使用者拉取对应 Gerrit `main` 或旧库 `master` 后即可直接使用；缺少全局安装时提醒用户按需安装，完整引导见 [仓库入口与安装](agent-bootstrap.md)。Codex 默认 `~/.codex/skills/clickzetta-doc-submit/`，Claude Code 使用 `~/.claude/skills/clickzetta-doc-submit/`，兼容运行时可用 `~/.agents/skills/clickzetta-doc-submit/`。安装脚本尊重 `CODEX_HOME`。

使用 `python3 <skill>/scripts/install_skill.py --runtime codex`（或 `claude` / `agents`）。相同版本保持原样；不同版本先比较本地定制，用户选择更新后加 `--update`，备份放在运行时的 `skill-backups/`，不在技能发现目录内。重启会话或刷新技能列表后由运行时发现；当前会话继续使用仓库内版本。配置文件位于 skill 目录之外，升级不会要求再次填写账号。

维护者修改本 skill 时先跑本地行为测试，再创建独立 Gerrit review。共享变更不属于中文或英文产品页面，不需要注册 SUMMARY；按代码检查和共享 skill 的评审流程提交。

## 验证边界

检查器验证 Git index 或 `--revision` 指定 commit 与基准间的文件变化，不自动 fetch、stage、commit 或 push。它不验证 SQL 执行结果、网站构建、远程图片永久可访问性，也不能替代使用者对语言和目标的确认。支持文件名（README/AGENTS/CLAUDE 等）不会强制注册到产品导航；如果确实要对外展示这些页面，由作者明确加入目录。
