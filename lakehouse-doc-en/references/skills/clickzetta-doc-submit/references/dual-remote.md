# 新旧文档仓库与双份提交

## 现行状态与映射

旧 TopThink 仓库仍承担常规提交，尚未切换；同一文档变更也要提交到对应 Gerrit。不要把旧仓库当作停用地址，也不要只在 Gerrit 提交后就报告任务完成。

| 语言 | 旧远端（master，文档位于根目录） | 新 Gerrit 项目（main） | 新库文档目录 |
| --- | --- | --- | --- |
| 中文 | `git@k.topthink.com:4v2dmg3x2e/k7pl9zonpy.git` | `ssh://<USERNAME>@gerrit.clickzetta-inc.com:29418/clickzetta-docs` | `clickzetta-doc-cn/` |
| 英文 | `git@k.topthink.com:4v2dmg3x2e/xgr3vwqg2j.git` | `ssh://<USERNAME>@gerrit.clickzetta-inc.com:29418/singdata-docs-en` | `singdata-doc-en/` |

例如旧中文 `SUMMARY.md` 对应新中文 `clickzetta-doc-cn/SUMMARY.md`；旧英文 `assets/example.png` 对应新英文 `singdata-doc-en/assets/example.png`。内部相对链接无需因为增加外层目录而重写。四个仓库根的 `skills/clickzetta-doc-submit/` 是协作工具，始终在各自仓库根同步，不映射为产品语言子目录里的 `skills/`。旧中文 Gerrit 内残留的英文目录属于历史副本，后续英文提交进入独立英文项目，不顺带删除历史目录。

本机个人路径保存在 `~/.config/clickzetta-doc-submit/config.json`，不写进共享包。`repositories` 是新 Gerrit 路径；`legacy_repositories` 和 `legacy_remotes` 按 `cn` / `en` 记录旧库路径和 origin，`legacy_branch` 为 `master`。初次记录时用 `git remote get-url origin` 核对；不要照抄英文 AGENTS 中可能遗留的中文地址。

`config` 命令保存新库路径；旧库字段目前通过编辑个人 JSON 增加，保留文件中其余键及私有权限。示例新增字段（路径换为当前使用者的真实路径）：

```json
{
  "legacy_repositories": {"cn": "<旧中文仓库绝对路径>", "en": "<旧英文仓库绝对路径>"},
  "legacy_remotes": {
    "cn": "git@k.topthink.com:4v2dmg3x2e/k7pl9zonpy.git",
    "en": "git@k.topthink.com:4v2dmg3x2e/xgr3vwqg2j.git"
  },
  "legacy_branch": "master"
}
```

## 常规编辑与提交

1. 明确语言和本次文件范围，检查新旧两份仓库的暂存区和工作区。分别 fetch 旧 `master`、新 `main`，记录明确基准 commit；保护既有修改，不自动混入其他任务。
2. 在旧库最新内容上编辑本次文档、图片及导航；检查 LLM 索引并给出可选建议，用户明确选择更新时才将索引纳入本次范围，跳过不阻断提交。遵循旧库的分支工作流。旧根路径映射到上表的新库前缀。新库本来已有独立修改时先对比并解决，不能无差别覆盖。
3. 将本次选定的新增、修改、删除、移动映射到隔离的新库暂存区，确保两份内容相同。SUMMARY 本次错误须修复；其他文档引用的轻量扫描及 LLM 索引均为可选建议，选择修复后把相同范围映射到两端。`check` 和 `add-image` 工具当前只识别有语言前缀的新库；不能直接对旧库根目录运行并称其通过。可将旧库的基准和本次暂存快照按前缀放入临时检查仓库，以它们作为检查基准和 Git index，避免把旧库全部历史视作新增。
4. 旧库提交到 `master`；Gerrit 使用独立提交和 Change-Id，默认送审。提交消息记录 `Legacy-Commit: <旧库提交SHA>` 以便追溯。`#CZEE-121` 是 Gerrit 默认前缀，不要求批量重写旧库历史。
5. 用 `push-plan --language <cn或en> --target both` 检查两份目的地，分别从对应仓库执行。不要向 Gerrit 推入旧 TopThink 整段历史，不共用一个 HEAD 向两端推送，不 force push。
6. fetch 验证旧 master 已包含该提交；验证 Gerrit 的实际评审或 main。返回两端结果。若 Gerrit 仅送审，明确“旧库已合入，Gerrit 已送审”，不能称主分支内容完全同步。一端失败时保留成功端及本地提交，补失败端，不回滚已成功的一端。

用户只要求某一端或明确改变目标时按本次指示执行。用户已明确授权同一语言、范围和同步目标时不重复索要确认。

## 首次导入或整库内容同步

用户明确要求将旧库最新内容同步到新库时，先 fetch 旧 `master`，以远端已提交快照为源，不从未提交的工作区复制。

- 从 Gerrit 最新 `main` 建隔离提交，只替换对应语言子目录；保留其他目录及 Gerrit 自身文件。删除也按源文档快照精确同步。旧库根 `skills/` 单独同步到 Gerrit 根 `skills/`，不混入语言目录；需要更新新库根的 Agent 入口时单独维护。
- 用 Git tree/blob 复制已跟踪内容（包括隐藏文件、图片、文件权限和大小写不同的同名文件）。macOS 普通复制或 checkout 可能折叠大小写同名文件；必须用 Git 对象核验，不能只比较磁盘文件数。
- 新提交以 Gerrit main 为父，不引入旧库历史。通过正常 commit-msg hook 生成 Change-Id，并记录 `Legacy-Repository`、`Legacy-Commit`、`Legacy-Tree` 和 `Target-Directory`。存在根 `skills/` 时，`Legacy-Tree` 记录排除该协作工具目录后的文档 tree，并说明排除项；完整旧提交仍由 `Legacy-Commit` 追溯。
- 这是已有内容的镜像，不批量治理历史缺图、TopWrite 格式、导航遗漏或 LLM 摘要，不把历史图片都认定为新增图片错误。检查器用于实际新写内容，镜像验收以精确 tree 一致为准。
- 用户要求完成远端主分支内容同步时推送 `refs/heads/main`；仅要求评审时推送 `refs/for/main`。遵守服务器权限，无权限则保留提交并报告拒绝。

推送后重新 fetch 两端，验证：

```bash
# 在旧库不存在根 skills/ 时，源文档 tree 就是 root tree：
git rev-parse <旧master提交>^{tree}
# 在对应 Gerrit 仓库读取子 tree，必须与上述 SHA 相同：
git rev-parse <新main提交>:clickzetta-doc-cn
# 英文使用：
git rev-parse <新main提交>:singdata-doc-en
```

比较对象 SHA 会同时验证所有递归路径、blob 和文件模式。同步期间旧 master 又有新提交时，先报告或纳入新快照再复验，不能仍声称已经追平最新远端。

旧库已有根 `skills/` 时，在旧库用 Git 对象构造排除该目录的源文档 tree，不改变源提交或工作区；然后将结果与上面的 Gerrit 语言子 tree 比较：

```python
import subprocess

source = "<旧master提交>"
entries = subprocess.check_output(["git", "ls-tree", "-z", source]).split(b"\0")
document_entries = [entry for entry in entries if entry and entry.split(b"\t", 1)[1] != b"skills"]
document_tree = subprocess.check_output(
    ["git", "mktree", "-z"], input=b"\0".join(document_entries) + b"\0"
).decode().strip()
print(document_tree)
```

根 skill 的一致性另按包内文件内容及执行权限核对。语言目录内的 AGENTS / CLAUDE 指引以 Git 根定位 skill，避免因外层目录不同而产生失效引用。
