# Data Analysis Plotting

面向学术出版的数据分析绘图核心库。它提供数据质量审查、局部出版样式、常用统计图和多格式导出，同时避免静默过滤数据、全局屏蔽警告和隐式统计聚合。

## 核心能力

- `audit_dataframe()`：报告缺失值、重复值、无穷值和分组样本量。
- `figure_size()`：生成单栏、双栏或自定义毫米宽度的画布尺寸。
- `publication_style()`：通过上下文管理器应用局部样式，不污染全局配置。
- `create_scatter_plot()`：散点图和可选线性拟合。
- `create_bar_plot()`：显式汇总方法、误差线和原始观测点。
- `create_distribution_plot()`：箱线图或小提琴图，并可保留原始点。
- `create_line_plot()`：默认不聚合重复 X 值。
- `create_heatmap()`：Pearson、Spearman 等相关性热图。
- `save_figure()`：默认仅导出 600 DPI PNG；仅在明确传入 `formats` 时导出 PDF、SVG 或 TIFF。

## 快速示例

```python
from pathlib import Path
import pandas as pd
from scripts.plotting_functions import (
    audit_dataframe,
    create_scatter_plot,
    save_figure,
)

df = pd.read_csv("data.csv")
print(audit_dataframe(df, group_cols=["group"]))

fig, ax = create_scatter_plot(
    df,
    x_col="x",
    y_col="y",
    hue_col="group",
    regression=True,
    x_label="Predictor (unit)",
    y_label="Response (unit)",
)
save_figure(fig, Path("outputs/scatter"))
```

未指定格式时始终只生成 PNG。需要其他格式时显式请求：

```python
save_figure(fig, Path("outputs/scatter"), formats=("png", "pdf"))
```

## 验证

```powershell
python -m unittest -v test_skill.py
python demo.py
```

测试会真实渲染所有核心图形，并验证数据审查、路径导出、错误输入和示例语法。
