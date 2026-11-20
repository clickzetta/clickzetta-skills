---
name: clickzetta-doc-submit
description: Use when contributors preview, submit, upload, review or synchronize ClickZetta Chinese or Singdata English product documentation. Includes local HTML previews with TopWrite image sizing and alignment, and submissions across the active legacy TopThink and matching Gerrit repositories.
---

# ClickZetta / Singdata 文档提交

## 本地预览

用户说“预览这个文档”“打开 Markdown 看看效果”，或需要验证 HTML 表格、图片宽度、居中时，使用本 skill 的本地预览工具。仅预览时不 fetch、不暂存、不提交，也不要求配置 Gerrit 账号。预览原文不改写磁盘文件。

```bash
python3 <skill>/scripts/preview_docs.py <Markdown文件的绝对路径>
```

自动推断包含 `SUMMARY.md` 或 `.topwrite/` 的文档根目录，启动或复用 `127.0.0.1` 服务并用默认浏览器打开。Agent 运行后应返回实际 URL；已打开不代表完成视觉验证，能使用浏览器工具时检查显示结果，无法验证时如实说明。不能因仅预览而触发下文提交流程。

手动使用：macOS 双击 skill 目录中的 `preview.command`，选择文档目录，再在页面拖入该目录内的 `.md`；也可在左侧搜索选择。跨目录文档请重新用其完整路径启动，以免图片目录绑定错误。完整使用方式、停止服务和兼容边界见 [本地预览说明](references/preview.md)。

## 提交与同步

当前尚未切换文档主仓库：常规文档提交仍走旧 TopThink 仓库的 `master`，同时必须向对应 Gerrit 仓库提交一份。旧库和新库的提交、基准与路径各自独立。Gerrit 默认创建评审；用户要求直接合入或明确完成远端主分支内容同步时直接推送 `main`。用户已经明确本次语言、范围及同步目标时继续执行，不反复请求同一授权。完整地址、映射及同步方法见 [新旧仓库双份提交](references/dual-remote.md)。

## 仓库与固定约定

| 项目 | 值 |
| --- | --- |
| 旧中文远端 / 分支 | `git@k.topthink.com:4v2dmg3x2e/k7pl9zonpy.git` / `master` |
| 旧英文远端 / 分支 | `git@k.topthink.com:4v2dmg3x2e/xgr3vwqg2j.git` / `master` |
| 中文项目 / 主分支 | `clickzetta-docs` / `main` |
| 中文 SSH 地址 | `ssh://<使用者用户名>@gerrit.clickzetta-inc.com:29418/clickzetta-docs` |
| 中文 HTTP 地址 | `http://<使用者用户名>@gerrit.clickzetta-inc.com/a/clickzetta-docs` |
| 英文项目 / 主分支 | `singdata-docs-en` / `main` |
| 英文 SSH 地址 | `ssh://<使用者用户名>@gerrit.clickzetta-inc.com:29418/singdata-docs-en` |
| 英文 HTTP 地址 | `http://<使用者用户名>@gerrit.clickzetta-inc.com/a/singdata-docs-en` |
| ClickZetta 中文 | `clickzetta-doc-cn/`，索引 `clickzetta-doc-cn/SUMMARY.md` |
| Singdata 英文 | `singdata-doc-en/`，索引 `singdata-doc-en/SUMMARY.md` |
| 新图片 | 中文 `clickzetta-doc-cn/assets/`；英文 `singdata-doc-en/assets/` |
| 默认提交标题 | `#CZEE-121 <本次修改说明>` |
| 默认送审目标 | `HEAD:refs/for/main` |
| 明确要求直接合入 | `HEAD:refs/heads/main` |

中英文使用两个独立 Git 仓库。英文提交必须进入 `singdata-docs-en`，不能提交到中文仓库中历史遗留的 `singdata-doc-en/`。用户选择两种语言时，分别获取基准、检查、提交及推送；不能用一次 `--language both` 检查或一次推送代替两个仓库的流程。

旧库文档位于仓库根目录；Gerrit 中文位于 `clickzetta-doc-cn/`，独立英文仓库内位于 `singdata-doc-en/`。图片、SUMMARY 和 LLM 索引都遵循同一前缀映射。检查器当前要求 Gerrit 语言前缀，不能直接对旧库根目录使用；常规编辑按参考说明将对应暂存快照映射到隔离的 Gerrit 检查环境。本次纯镜像同步用 Git tree 一致性验证，不将全部历史内容当作新写文档修复。

`#CZEE-121` 是仓库维护者指定的默认提交前缀，已用于成功推送；**没有单独的 Jira 号时直接使用它，不要求使用者另外提供 Jira 号**。用户给出其他编号时按用户要求覆盖。它仍会经过服务器的 Jira 校验；若默认编号被服务器拒绝，原样概述拒绝原因并保留提交，不能编造工单、修改服务器规则或擅自改成其他编号。

旧库 `AGENTS.md` 的 `master` 工作流仍适用于旧库；新库使用本技能的 Gerrit `main` 流程。英文 AGENTS 中可能复制了中文旧地址，必须以本技能中明确的英文地址及实际 origin 为准，其余内容质量规范仍适用。

## 工具与首次使用

本 skill 随中文、英文的新旧文档仓库分发，位于仓库根的 `skills/clickzetta-doc-submit/`。从仓库 `AGENTS.md` / `CLAUDE.md` 进入且本地未安装时，先按 [仓库内发现与安装](references/agent-bootstrap.md) 直接使用仓库内版本，并提醒用户可选安装；不要为安装单独阻断维护工作。仓库内版本是当前协作约定，用户级安装版本不同时提示更新，不覆盖本地定制。

下文 `<skill>` 表示本技能目录的绝对路径；始终用解释器运行脚本。Python 3.10+、Git，依赖见 `requirements.txt`。若当前 Python 缺少依赖，在使用者本地虚拟环境安装：

```bash
python3 -m venv ~/.cache/clickzetta-doc-submit/venv
~/.cache/clickzetta-doc-submit/venv/bin/python -m pip install -r <skill>/requirements.txt
```

后续使用该环境的 Python 代替下面的 `python3`。不要把虚拟环境放进共享 skill。

1. 运行 `python3 <skill>/scripts/docs_submit.py config --language cn` 或 `config --language en` 读取对应仓库的个人配置。旧版单仓库配置仅作为中文配置兼容，英文缺少配置时停止生成推送计划，不回退到中文。
2. 仅在配置缺失或使用者要更换账号时，询问其 Gerrit 用户名；不能继承同事的 origin 用户名。仓库位置可从当前目录和 Git 根目录发现；无法确定再询问。
3. 默认 SSH，也支持 HTTP；HTTPS 在实例支持时可选。账号使用现有 SSH key / Git 凭据管理器，不记录密码、私钥或 HTTP token。遇到认证需要用户操作时告知具体步骤。
4. 保存设置：

```bash
python3 <skill>/scripts/docs_submit.py config --language cn --username <使用者用户名> --protocol ssh --repo <中文仓库绝对路径>
python3 <skill>/scripts/docs_submit.py config --language en --username <使用者用户名> --protocol ssh --repo <英文仓库绝对路径>
```

共享说明中的 `<使用者用户名>` 是占位符，不能固定成维护者账号。每位同事首次使用时保存自己的 Gerrit 用户名及本地仓库路径，后续脚本从其个人配置生成带本人用户名的 URL。旧库 SSH 地址中的 `git` 是服务账号，保持原样，实际权限由该同事的 SSH key 决定。

设置位于 `~/.config/clickzetta-doc-submit/config.json`，与共享包分离。`repositories.cn/en` 保存 Gerrit 本地路径，`legacy_repositories.cn/en`、`legacy_remotes.cn/en` 及 `legacy_branch: master` 保存旧库路径、地址及分支；首次配置时核对旧库实际 origin 后记录，不能把中文地址复用于英文。后续直接复用，不反复询问用户名。Git `user.name` / `user.email` 与 Gerrit 登录用户名分开处理；只在缺失或明显错误时补齐仓库本地身份，不修改全局身份。

新协作者没有仓库时，从对应语言的地址 clone 到自己选择的路径。核对 remote 的项目名和所选语言一致，不要求任一仓库同时包含两种语言目录。缺少文档内容时先报告现状；指向其他项目或处于尚未完成的合并时先解决问题。具体连接、hook、安装和更新方法见 [仓库与维护说明](references/repository.md)。

## 工作步骤

### 1. 获取最新基准并隔离本次变更

- 检查分支、暂存区、工作区及本次目标文件。用户已有明确的中文/英文指示，先记录，最终在推送预览中确认。
- 分别获取旧远端 `master` 与对应 Gerrit `main`。常规编辑以旧远端最新内容为准；完成旧库提交后按已确认范围制作 Gerrit 副本，不要沿用其他人的远端账号。
- 旧库编辑以最新 `master` 创建工作分支，Gerrit 副本以最新 `main` 创建独立工作分支。有已有改动时先保护其暂存/未暂存状态再同步；不要自动 stash 后混入他人改动，不强制重置、不强制推送。
- Gerrit 副本用与最新远端 `main` 的 merge-base 作为检查基准；旧暂存快照在临时检查仓库中以映射后的旧基准检查。必须显式把对应基准 commit 传给检查器，不依赖可能过期或不适用的 `origin/main`。
- 只暂存本次任务文件。其他语言、其他任务和 skill 自身的改动不要夹带进文档提交。已暂存的不相关改动需要保持时，用独立 worktree 或隔离的暂存/提交方案；检查器本身只读，不会取消暂存。

### 2. 修复图片与 SUMMARY，建议维护正文引用和 LLM 索引

**图片**：新图复制到对应语言的 `assets/`，可按主题建子目录；用相对于当前 Markdown 文件的路径引用。不要写个人绝对路径、磁盘路径、Gerrit 网页地址或跨语言目录引用。协助复制并给出正确引用：

```bash
python3 <skill>/scripts/docs_submit.py add-image --repo <仓库> --language cn \
  --source <本机图片> --document clickzetta-doc-cn/guides/example.md \
  --name example/step-01.png
```

输出图片文件路径和 `../assets/example/step-01.png` 形式的引用。命名冲突且内容不同会停止，不能覆盖他人图片。复制后把图片和修改后的文档一起暂存。英文用 `--language en` 和 `singdata-doc-en/...`。

历史 `.topwrite/assets/` 图片继续保留；不要搬迁或重命名整个资源目录。保留现有 `.gitattributes`，不引入 LFS。TopWrite `:-:`、`=740`、以 `/` 开头及按书根解析的引用属于旧兼容语法；不全库转换。新引用用标准 Markdown。修正文档时若要改变已有显示尺寸或居中效果，先展示预期变化，再修改。远程图单独提示可访问性，不擅自下载替换。

**SUMMARY.md**：以上一次基准中的目录条目为准，只维护本次变化：

| 本次变化 | 处理 |
| --- | --- |
| 新增正式文档 | 按现有层级注册；用标题和相邻页面建议位置，不明确时让用户选位置 |
| 删除已注册页面 | 删除其入口；保留有效子条目，必要时询问新的归属 |
| 重命名 / 移动已注册页面 | 保留原条目位置，更新导航链接；修复受影响的图片引用，建议核对正文链接 |
| 只修改正文 | 保持有效注册；不因标题微调就强制改导航文案 |
| 修改或移动历史未注册页面 | 保持未注册状态，不要求补齐全库历史页面 |
| 用户明确要新增未列入导航的页面 / 取消导航 | 说明结果并记录具体路径；检查时仅对该路径使用 `--allow-unlisted` |

不重新生成整个 SUMMARY，不把 README、AGENTS、技能说明等支持文件当作正式页面，不自动删除未注册文档。

若历史未注册页面同时大幅改写并移动，Git 可能将其识别为删除加新增；核实旧路径和用户的移动意图后，仅对新路径使用 `--allow-unlisted`，保留其未注册状态，不要求用户重复决定。

**文档引用影响（可选建议）**：出现新增、改名、移动或删除时，建议核对相关页面的引用，详情见 [轻量依赖检查](references/dependencies.md)。沿用本地 Git 快照和 Markdown 解析；仅移除或移动目标时扫描同语言文档的入站引用，不依赖概念图谱、不更新 graphify、不访问官网。输出受影响文档、链接位置和已识别改名的替换建议；移动文档时也检查它自身的相对链接。普通正文改动不触发全目录扫描。

SUMMARY 的新增登记、失效路径、重复登记等本次错误仍须修复；**其他文档的链接问题为可选 warning，不阻断提交**。用户明确选择修复时再改这些正文引用，无法明确删除页面的替代文档时只列建议，不猜目标或批量替换。未选择修复时说明已发现的影响并继续，不等待额外确认；不能声称已保证所有引用正确。

**LLM 索引（可选建议）**：读取 [LLM 索引维护规则](references/llms-index.md)，结合本次 SUMMARY 和正文变化检查对应的 `llms.txt`、`llms-*.txt`，列出建议及涉及文件。新增 / 删除注册页面、改名 / 移动、跨章节移动、导航标题变化时建议同步条目；正文有实质变化时建议核对摘要。用户明确要求一并更新或已接受建议时再修改；否则保留索引、简要报告建议并继续提交，不为索引更新单独设置确认门槛或等待回复。跳过更新不影响文档检查通过及新旧仓库双份提交。

选择更新时，以基准中的 SUMMARY 和现有索引为起点，保持 SUMMARY 顺序，保留有效摘要及历史未注册状态；历史遗漏 / 多余条目单独提示，不顺带全量重建或修复。章节入口变化时才调整 `llms.txt` 路由；根索引按 [LLM 索引维护规则](references/llms-index.md) 使用独立二级标题和 Markdown 链接列表（`- [章节](URL)`），品牌事实入口与文档索引分开，不使用 `## 章节 → URL`；`llms-full.txt` 是品牌事实文件，普通文档提交保持原样。使用官网 URL，不把 Gerrit 语言目录加进公开链接。英文正文页面使用 `https://singdata.com/documents/`；`llms.txt`、`llms-full.txt` 和所有 `llms-*.txt` 文件链接使用网站根目录 `https://singdata.com/`。摘要和关键词依据实际正文生成和审阅：每条文档摘要紧邻下一行以两个空格缩进添加 `<!-- keywords: 词语, 词语 -->`，每篇最多 5 个，不凑数，无依据或占位页省略；注释属于元数据，不计入描述。根 `llms.txt` 保留该元数据格式的简短说明。完整提取与解析规则见 [LLM 索引维护规则](references/llms-index.md)。检查器只能验证结构，不能判断事实准确性。选中的索引修改与相关文档一起暂存、预览，并同步到同一语言的新旧仓库。共享包已包含维护规则，不依赖个人的 `lakehouse-llms-index` skill。

### 3. 检查实际暂存版本

先逐项 `git add -- <明确路径>`，然后在对应仓库运行（中文 `cn`、英文 `en`；两种语言分别执行）：

```bash
python3 <skill>/scripts/docs_submit.py check --repo <仓库> --language cn --base <基准commit>
```

退出码：`0` 必需检查通过，可同时存在建议；`1` 本次引入的必需检查错误；`2` 使用或环境错误。返回 JSON 包括文件范围、错误和提示。必须处理 `errors` 后再提交；LLM 索引问题全部位于 `warnings`，带 `optional: true`，不改变通过状态或退出码，`historical` 区分基准已有与本次新增问题。工作区修正后重新暂存、重新检查；未暂存修正不算通过。检查不自动发布，也不等价于 SQL 示例实测。

必需检查：新增图片位置与真实文件、Git 路径大小写、图片引用、LFS 指针、SUMMARY 同步，以及移除图片后的入站引用。可选文档引用提示：`document_dependency_review` 建议核对增删改名的影响，`document_deleted_in_use` 列出仍指向被删除 / 改名页面的链接，`document_link_missing` 提示新增或移动后失效的正文链接。`dependency_reviews` 记录触发文件和扫描范围；链接提示带 `optional: true`，不会变成错误。

可选索引提示：遗漏 / 多余 / 重复条目、章节归属、标题、摘要非空、关键词注释格式和根索引路由。`llms_abstract_review` 建议人工核对语义；未选择索引维护时可直接保留，不能把结构检查通过当作摘要已核实。历史问题单独提示，不要求顺带治理所有旧文档。手工检查本次修改的标题、表格、代码块和旧平台显示语法；遵循对应目录的内容质量要求。

### 4. 展示双份提交结果与目标，然后提交

确认卡片包含：

- 当前 Gerrit 账号、中文 / 英文、旧库 master 与新库 main/review 的准确地址及目录；
- 本次文档、图片、SUMMARY 变更及检查结果；正文引用列出可选影响及本次修复范围；LLM 索引列出实际更新文件和摘要审阅结论，或注明“本次未更新”及简要建议，无需为跳过可选修复索要确认；
- 提交标题，默认 `#CZEE-121 <说明>`；
- 模式：默认送审，或使用者明确要求的直接合入。

语言、范围或目标未明确时准备完整预览后再询问；用户已明确本次要求时视为该范围授权，不重复确认。更换语言或扩大范围后重新确认。此前保存的语言偏好不能代替本次授权。

确认后以 UTF-8 文件保存提交消息，使用 `git commit -F <消息文件>`，不把用户文本拼进 shell 命令。Gerrit 提交用正常 `commit-msg` hook 生成 Change-Id；更新同一个评审时 amend 并保留原 Change-Id。旧 TopThink 提交沿用旧库规范，不强制添加 Gerrit 前缀或 Change-Id。Gerrit 默认标题可用工具生成：

```bash
python3 <skill>/scripts/docs_submit.py subject "更新导入指南"
```

### 5. 推送并验证

本地提交完成后可复查真实 commit，无需依赖当前暂存区；推送前用此方式确认待推送版本的 SUMMARY 仍正确。显式保留本次修改前记录的基准，不能把新 HEAD 自己当作基准：

```bash
python3 <skill>/scripts/docs_submit.py check --repo <仓库> --language cn \
  --base <原基准commit> --revision HEAD
```

`snapshot: git-commit` 与 `revision` 标明实际检查的 commit；正文引用和 LLM 索引仍是可选建议。后续追加、amend 或 rebase 后以实际新 commit 复查，不把暂存区里尚未提交的修复当作已完成。

获取推送参数（仅输出参数，不执行）：

```bash
python3 <skill>/scripts/docs_submit.py push-plan --language cn --target both
python3 <skill>/scripts/docs_submit.py push-plan --language en --target both
```

`--target both` 返回两份计划：旧库 `HEAD:refs/heads/master` 和 Gerrit 默认 `HEAD:refs/for/main`。这两份 HEAD 必须在各自 `repo` 中准备和执行，不能把一个仓库的提交直接推到两个不同历史的仓库。旧 master 已包含本次提交时只需验证，不重复造提交。纯粹补同步已有旧库内容时旧库不需要新提交。

核对每份计划的 `repo`、`language`、`project` 和 `url`。用户要求直接合入或完成两端主分支同步时添加 `--mode direct`，Gerrit 改为 `HEAD:refs/heads/main`。`--target gerrit` 仅用于补交新库或独立维护 Gerrit，不能代替常规双份提交；省略 `--target` 为兼容旧工具仅返回 Gerrit 计划。未指定 `--language` 时只兼容旧中文流程，不能用于英文。如果账号无权限，报告服务器拒绝，不自动改权限或强制推送。

执行输出中的参数数组，或使用可靠 shell 引用。推送前确认各自 HEAD 包含刚检查的完整文件，所选文件没有遗漏的未提交修改，并确认所有待发送 Gerrit 提交的标题前缀和 Change-Id；旧库提交按旧库规范检查。新获取的远端变化如需 rebase，处理后重新检查。一次逻辑变更优先一个评审，避免夹带其他未合入提交。

- 旧库：重新 fetch master，验证其已包含本次旧库提交。送审：从服务器输出取得真实 Gerrit review URL，核对项目、分支、提交 / patchset，返回链接；不能把它报告为已合入。服务器没给可核对的评审结果时不能猜链接。
- 直接：重新 fetch `main`，验证提交已被远端包含，再报告合入结果。
- 如果服务端拒绝，保留本地提交、说明具体原因；认证 / 权限 / 默认编号拒绝等需要外部处理时停止重复推送。发生 non-fast-forward 可同步后修复，重新检查再重试。

旧库与 Gerrit 两份结果都验证后才报告双份提交完成；一边失败时分别说明成功端和待处理端，只补失败的一端。整库快照同步还须比较旧提交的根 tree 和新提交的语言子 tree，标明源 commit 与目标 commit。

## 安装、共享与维护

共享源：中文 Gerrit 仓库根的 `skills/clickzetta-doc-submit/`，相同版本同步到独立英文 Gerrit 和两个旧仓库根的同名目录。维护 skill 时同步四份并比较文件内容，不因英文产品翻译而翻译 skill 内规则或改写 Git 项目名。默认语言规则共用一份，不在产品目录内再嵌套拷贝 skill；镜像旧文档到 Gerrit 时保留根 skill，不把旧库根的 `skills/` 当作产品页面复制进语言子目录。

安装可使用 `python3 <skill>/scripts/install_skill.py --runtime codex`（Codex）、`--runtime claude`（Claude Code）或 `--runtime agents`（兼容运行时），已有不同版本先比较，明确选择更新后用 `--update` 保留备份。当前运行时不要安装多个同名版本。分发时排除 `__pycache__/`、`*.pyc`、虚拟环境及个人配置；个人配置留在 `~/.config/`，不上传、不打包。共享包中不保存任何真实个人账号或本地路径。

共享 skill 的修改单独验证、单独送审；不执行文档语言检查来强迫它注册到 SUMMARY。维护者运行：

```bash
python3 -m unittest discover -s <skill>/tests -v
```

可复用场景及验收条件见 [行为验证场景](tests/scenarios.md)。
