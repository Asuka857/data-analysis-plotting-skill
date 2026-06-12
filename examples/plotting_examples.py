"""Executable templates for the publication-oriented plotting core."""


def example_scatter_plot():
    return '''\
from pathlib import Path
import pandas as pd
from scripts.plotting_functions import audit_dataframe, create_scatter_plot, save_figure

df = pd.read_csv("your_data.csv")
print(audit_dataframe(df, group_cols=["category"]))

fig, ax = create_scatter_plot(
    df,
    x_col="variable_x",
    y_col="variable_y",
    hue_col="category",
    regression=True,
    x_label="Variable X (unit)",
    y_label="Variable Y (unit)",
)
save_figure(fig, Path("outputs/scatter"))
'''


def example_bar_plot():
    return '''\
from pathlib import Path
import pandas as pd
from scripts.plotting_functions import create_bar_plot, save_figure

df = pd.read_csv("your_data.csv")

# Bars show group means; error bars show 95% confidence intervals.
# Raw observations are retained to reveal sample size and distribution.
fig, ax = create_bar_plot(
    df,
    x_col="category",
    y_col="value",
    estimator="mean",
    errorbar=("ci", 95),
    show_points=True,
    x_label="Treatment",
    y_label="Response (unit)",
)
save_figure(fig, Path("outputs/group_comparison"))
'''


def example_heatmap():
    return '''\
from pathlib import Path
import pandas as pd
from scripts.plotting_functions import create_heatmap, save_figure

df = pd.read_csv("your_data.csv")

fig, ax = create_heatmap(
    df,
    method="spearman",
    mask_upper=True,
    title=None,
)
save_figure(fig, Path("outputs/correlation"))
'''


def generic_plot_template(plot_type):
    templates = {
        "scatter": {
            "title": "散点图模板",
            "description": "展示两个连续变量的关系，可选线性拟合与置信区间。",
            "code": example_scatter_plot(),
        },
        "bar": {
            "title": "汇总比较模板",
            "description": "明确展示均值、95% 置信区间和原始观测值。",
            "code": example_bar_plot(),
        },
        "heatmap": {
            "title": "相关性热图模板",
            "description": "展示数值变量的 Pearson 或 Spearman 相关结构。",
            "code": example_heatmap(),
        },
    }
    return templates.get(plot_type, templates["scatter"])


if __name__ == "__main__":
    for plot_type in ("scatter", "bar", "heatmap"):
        template = generic_plot_template(plot_type)
        print(f"\n## {template['title']}\n{template['code']}")
