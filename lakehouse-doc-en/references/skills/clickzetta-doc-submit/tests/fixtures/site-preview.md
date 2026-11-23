# 官网样式预览样例

用于人工对照正文、**粗体**、*斜体*、~~删除线~~、[链接](#图片与尺寸) 和 `workspace.schema.table`。正文应保持 14px 字号、28px 行高。

## HTML 表格与格式

<table>
<thead><tr><th>类别</th><th>显示效果</th></tr></thead>
<tbody>
<tr><td rowspan="2">HTML</td><td><span style="color:#006bf8;font-weight:700">蓝色加粗</span>、<sup>上标</sup>、<sub>下标</sub></td></tr>
<tr><td style="background:#fffbe6">黄色背景、换行<br>第二行</td></tr>
<tr><td colspan="2" style="text-align:center">合并单元格并居中</td></tr>
</tbody>
</table>

<p style="font-size:18px;color:#e45b51;text-align:center">HTML 内联样式：18px 红色居中</p>

> **提示**：引用段落应显示为官网的蓝色提示框，内部的链接、文字和格式继续保留。

## 图片与尺寸

默认 Markdown 图片铺满正文：

![默认宽度](site-preview.svg)

TopWrite 居中、固定宽度 240px：

:-: ![居中固定宽度](site-preview.svg =240)

HTML 图片保留明确指定的 50% 宽度：

<img src="site-preview.svg" alt="HTML 百分比宽度" style="width:50%;margin-inline:auto">

## 列表与代码

- 第一项包含 `inline_code`
- 第二项
  - 嵌套列表

1. 有序列表第一项
2. 有序列表第二项

```sql
-- SQL 高亮；符号不会变成 HTML
SELECT id, 'Lakehouse' AS label
FROM example
WHERE id < 10;
```

```unknown-language
<script>这段代码应作为文字显示</script>
```
