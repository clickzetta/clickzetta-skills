# LLM 索引维护（可选）

## 提交时先建议，按需更新

普通文档提交会只读检查索引，发现问题时说明建议操作、涉及文件及本次新增 / 历史差异。**更新属于可选项**：用户明确要求或接受建议时才修改，未选择时保持原文件并继续文档提交，不等待额外确认。新旧两端都适用；不能以索引遗漏、空摘要或未核实摘要为由阻断普通提交。仅预览 Markdown 不运行索引检查。

本规则整合了独立 `lakehouse-llms-index` skill 中的增量维护方法，可独立分发，不要求同事安装个人 skill。用户明确要求完整维护索引时，以所选语言的 SUMMARY 已注册页面为范围；普通提交不自动扩大为全量重建。

## 文件职责和 URL

中英文在各自仓库独立维护：旧库位于仓库根目录；新中文位于 `clickzetta-docs` 的 `clickzetta-doc-cn/`，新英文位于 `singdata-docs-en` 的 `singdata-doc-en/`。选择更新后，同一语言的新旧两端按此映射同步；两种语言分别依据各自 SUMMARY 和正文生成，不能直接互相复制。

| 文件 | 内容 | 文档提交时的处理 |
| --- | --- | --- |
| `llms.txt` | 品牌定义和章节子索引入口 | 章节入口变化时建议调整路由，保留品牌定义 |
| `llms-<section>.txt` | 本章节已注册页面的官网 URL、一句话摘要和关键词元数据 | 本次 SUMMARY 条目或文档内容变化时建议维护 |
| `llms-full.txt` | 品牌定位、实体事实、FAQ | 普通文档提交不改；需要事实更新时作为明确任务审阅 |

| 语言 | 文档 URL 前缀 | 子索引 URL 前缀 |
| --- | --- | --- |
| 中文 | `https://www.yunqi.tech/documents/` | `https://www.yunqi.tech/` |
| 英文 | `https://singdata.com/documents/` | `https://singdata.com/` |

英文 `llms.txt`、`llms-full.txt` 和 `llms-<section>.txt` 均发布于网站根目录，例如 `https://singdata.com/llms-quickstart.txt`；它们之间的入口和回链也使用该前缀。`/documents/` 仅用于正文页面 URL，不能用于 LLM 文件 URL。

文档 URL 使用相对于语言根的 Markdown 路径，去掉 `.md`，保留目录和大小写，必要时 URL 编码。例如 `clickzetta-doc-cn/guides/Example.md` 对应 `https://www.yunqi.tech/documents/guides/Example`。不能加入 `clickzetta-doc-cn/` 或 `singdata-doc-en/`。Gerrit 提交不代表官网已发布，新页面尚未上线的 HTTP 404 不作为送审失败。

## 根索引的 Markdown 格式

`llms.txt` 保留文件名和品牌介绍，使用独立二级标题组织内容；章节入口写成 Markdown 链接列表，不能把标题和裸 URL 拼成 `## 章节 → URL`。中文使用 `## 品牌与事实` 和 `## 文档索引`，英文使用 `## Entity and facts` 和 `## Documentation`。品牌事实文件入口也使用链接列表，与章节入口分开；章节顺序沿用 SUMMARY。

```markdown
## Entity and facts

- [Full entity & facts for AI](https://singdata.com/llms-full.txt)

## Documentation

- [Quick Start](https://singdata.com/llms-quickstart.txt)
- [User Guide](https://singdata.com/llms-guide.txt)
```

检查器读取文档索引区的链接列表，忽略品牌事实区和代码块；旧的箭头标题格式仍可识别，但会产生可选的 `llms_root_format` 转换提示。

## 章节映射

两种语言的完整映射也维护在 `scripts/docs_submit.py` 的 `LLMS_SECTIONS` 中。选择维护新增或重命名章节时，同步维护该配置与本表；遇到未识别章节，报告建议补充映射，不能猜测文件名写入索引。未选择索引维护时可保留该提示继续提交。

| 中文章节 | 英文章节 | 子索引文件 |
| --- | --- | --- |
| 快速入门 | Quick Start | `llms-quickstart.txt` |
| 使用指南 | User Guide | `llms-guide.txt` |
| AI指南 | AI Guide | `llms-ai.txt` |
| SQL参考手册 | SQL Manual | `llms-sql.txt` |
| 开发手册 | Development Manual | `llms-dev.txt` |
| 实践教程 | Practice Tutorials | `llms-tutorials.txt` |
| 使用场景 | Use Cases | `llms-scenarios.txt` |
| 产品更新 | Release Notes | `llms-updates.txt` |
| 其它 | Other | `llms-others.txt` |

## 选择更新后，按本次变化同步

- 新增注册页面：在所属子索引按 SUMMARY 顺序增加 `- [导航标题](官网URL): 一句话摘要`。
- 删除已注册页面或明确取消注册：移除对应索引条目。
- 改名 / 移动：更新官网 URL；根据 Git 重命名关系复用原摘要，审阅是否仍准确。
- 跨章节移动：从原子索引移除，加入新子索引；复用有效摘要，不要求改写内容。
- 导航文案变化：同步子索引标题。仅正文标题变化且 SUMMARY 文案保留时，索引标题也保持导航文案。
- 调整导航顺序：相关子索引遵循新的 SUMMARY 顺序；检查器不验证顺序，代理在预览前核对。
- 仅修改正文：审阅对应摘要是否仍准确；实质改变能力、限制、步骤或页面用途时更新摘要，否则保留。
- 历史未注册页面：继续不注册，也不加入 LLM 索引。
- 章节新增 / 删除 / 改名：维护映射、对应子索引以及 `llms.txt` 的 `## 文档索引` / `## Documentation` 下的 `- [章节](子索引官网URL)` 入口。保持品牌定义和事实说明不变。

摘要使用对应语言，中文一句简洁介绍，英文约 30–50 词，忠于正文。已有摘要按原 URL 或明确的重命名关系复用；新 URL 不代表必须重写移动页面的摘要。不要仅凭文件名生成，不盲目截取前 100 行；先读简介、相关标题和实际修改内容，需要时扩展阅读范围。

## 逐篇文档的关键词元数据

维护或生成含文档描述的 `llms-<section>.txt` 时，在每条摘要的紧邻下一行添加标准 HTML 注释，缩进两个空格，使注释归属于同一个列表项：

```markdown
- [Dynamic Table（动态表）](https://www.yunqi.tech/documents/om-dynamic-table): 介绍动态表的增量计算原理和数据加工场景。
  <!-- keywords: 动态表, 增量计算, 数据加工 -->
```

- 固定使用小写 `keywords:`；一条记录至多一个注释，关键词用英文逗号加空格分隔。每篇最多 5 个，不凑数；有 1–4 个合适的就只写这些。没有可支持的关键词、空白/占位/纯导航页面省略整条注释，不输出空注释或虚构能力。
- 根据实际正文的主要对象、具体功能和应用场景提取短词或短语。先读简介、相关章节及必要正文；不能只按文件名、旧摘要或词频生成。函数页优先函数名和准确用途，不用“文档”“示例”“SQL”等泛词机械补齐。使用对应文档语言，保留产品名、函数名和必要英文术语；去除重复与无意义的同义词。
- 关键词本身不得包含英文/中文逗号、换行、HTML 注释分隔符或连续两个连字符。解析器从注释读取并按英文逗号拆分、去除首尾空白；忽略正文代码示例中的同名注释。
- 注释是独立元数据，**不得计入摘要**。读取摘要先排除 HTML 注释；即使有关键词，空摘要仍是空摘要。HTML 渲染后注释通常隐藏，应用应读取原始文本。无须重复写 type、URL 或标题；注释只关联紧邻上一条文档记录，不能跨空行/其他记录继承。
- 改名或移动时可复用仍准确的关键词；正文实质变化时同时审阅摘要和关键词。已选择索引维护的新增条目按此生成；历史遗漏只提示，不要求普通文档提交全量补齐。普通提交中的格式问题为可选 warning，不升级为阻断。
- 根 `llms.txt` 的 `## 关键词元数据` / `## Keyword metadata` 区说明此约定及最多 5 个、不凑数、无依据则省略的规则。根文件的章节路由本身不加逐篇关键词；`llms-full.txt` 品牌事实文件和正文 `.md` 不因本约定自动改写。

## 暂存检查与历史基准

`docs_submit.py check` 只读 Git index 与 `--base`，不生成摘要或改写文件。每个快照独立从自己的 SUMMARY 推导应有条目，再比较差异。遗漏、失效 URL、重复、错章节、标题不一致、空摘要、关键词注释格式和根索引路由问题全部作为 `warnings`，带 `optional: true`；基准已有问题为 `historical: true`，本次新增为 `false`。仅有索引建议时仍返回 `ok: true`、退出码 `0`，图片与 SUMMARY 等必需检查不受影响。`--allow-unlisted` 只用于导航例外，不需要为了跳过索引更新而设置。

正文修改会产生可选的 `llms_abstract_review` 提示，结构检查不验证摘要事实、品牌声明或网站部署。选择更新时，由代理依据正文核对语义；索引修改暂存后重新检查，工作区未暂存的改动不算已纳入提交。未选择更新时报告“本次未更新”及建议即可，不要求完成摘要审阅。历史遗漏单独提示，不顺带全库修复或把未注册文档补进导航。
