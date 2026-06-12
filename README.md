# Data Analysis Plotting Skill

面向科研绘图与学术出版的 Codex Skill，同时提供可独立复用的 Python 绘图核心库。

它强调统计表达准确、原始数据可见、色盲友好配色和真实渲染验证，而不是简单套用所谓的 “Nature 风格”。未明确要求输出格式时，默认只生成一个 600 DPI PNG 文件。

## 主要能力

- 绘图前审查缺失值、重复值、无穷值和分组样本量。
- 使用单栏、双栏或自定义毫米宽度创建出版尺寸图形。
- 通过局部样式上下文避免污染 matplotlib 全局配置。
- 创建散点图、汇总比较图、分布图、折线图和相关性热图。
- 显式控制汇总方法、误差线、回归线和重复观测聚合。
- 默认使用色盲友好配色，并保留原始观测信息。
- 真实渲染测试覆盖绘图、错误输入、文件导出和示例语法。

## 仓库结构

```text
data-analysis-plotting-skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── test_skill.py
├── scripts/
│   └── plotting_functions.py
└── examples/
    └── plotting_examples.py
```

## 安装为 Codex Skill

将仓库克隆到个人 Skill 目录：

```powershell
git clone https://github.com/Asuka857/data-analysis-plotting-skill.git `
  "$HOME\.agents\skills\data-analysis-plotting-skill"
```

安装 Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

新建 Codex 线程后，使用类似请求触发：

```text
使用 data-analysis-plotting 绘制论文级科研图，并检查数据质量。
```

## 独立使用核心库

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

# 未指定 formats 时仅生成 outputs/scatter.png。
save_figure(fig, Path("outputs/scatter"))
```

只有明确需要其他格式时才传入 `formats`：

```python
save_figure(fig, Path("outputs/scatter"), formats=("png", "pdf"))
```

## 验证

```powershell
python -m unittest -v test_skill.py
```

测试会使用无界面的 matplotlib 后端真实渲染所有核心图形。

## 设计边界

该项目是紧凑的出版级绘图核心工具库，不负责自动选择图表、自动执行统计检验或替代完整的数据分析流程。使用者仍需根据研究问题、实验设计和数据结构判断统计方法是否合理。
