"""Publication-oriented plotting helpers built on pandas, matplotlib, and seaborn."""

from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

MM_PER_INCH = 25.4
PUBLICATION_WIDTHS_MM = {"single": 89, "double": 180}
DEFAULT_PALETTE = "colorblind"


def _validate_dataframe(df, columns=(), numeric_columns=()):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        raise ValueError("df must not be empty")

    missing = [column for column in columns if column and column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    non_numeric = [
        column
        for column in numeric_columns
        if column and not pd.api.types.is_numeric_dtype(df[column])
    ]
    if non_numeric:
        raise ValueError(f"Columns must be numeric: {', '.join(non_numeric)}")


def audit_dataframe(df, group_cols=None):
    """Return a compact, serializable data-quality report without modifying data."""
    _validate_dataframe(df)
    group_cols = list(group_cols or [])
    _validate_dataframe(df, columns=group_cols)

    numeric = df.select_dtypes(include=[np.number])
    infinity_counts = {
        column: int(np.isinf(numeric[column].to_numpy()).sum())
        for column in numeric.columns
    }
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values": {column: int(value) for column, value in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "infinite_values": infinity_counts,
        "group_counts": {
            column: {
                str(level): int(count)
                for level, count in df[column].value_counts(dropna=False).items()
            }
            for column in group_cols
        },
    }


def figure_size(width="single", aspect=0.75, width_mm=None):
    """Return a publication figure size in inches."""
    if width_mm is None:
        if width not in PUBLICATION_WIDTHS_MM:
            choices = ", ".join(PUBLICATION_WIDTHS_MM)
            raise ValueError(f"width must be one of: {choices}")
        width_mm = PUBLICATION_WIDTHS_MM[width]
    if width_mm <= 0 or aspect <= 0:
        raise ValueError("width_mm and aspect must be positive")
    width_inches = width_mm / MM_PER_INCH
    return width_inches, width_inches * aspect


@contextmanager
def publication_style(font_size=8, palette=DEFAULT_PALETTE):
    """Apply a compact publication style without leaking global matplotlib state."""
    rc = {
        "font.size": font_size,
        "axes.labelsize": font_size,
        "axes.titlesize": font_size,
        "xtick.labelsize": font_size - 1,
        "ytick.labelsize": font_size - 1,
        "legend.fontsize": font_size - 1,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
    }
    with plt.rc_context(rc), sns.axes_style("ticks"), sns.color_palette(palette):
        yield


def setup_nature_style():
    """Compatibility helper returning the default colorblind-safe palette."""
    return sns.color_palette(DEFAULT_PALETTE)


def _finish_axis(ax, x_label=None, y_label=None, title=None):
    if x_label is not None:
        ax.set_xlabel(x_label)
    if y_label is not None:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title, pad=6)
    sns.despine(ax=ax)
    ax.figure.tight_layout()


def create_scatter_plot(
    df,
    x_col,
    y_col,
    hue_col=None,
    title=None,
    figsize=None,
    regression=False,
    ci=95,
    palette=DEFAULT_PALETTE,
    x_label=None,
    y_label=None,
):
    """Create a scatter plot, optionally with a linear fit and confidence interval."""
    _validate_dataframe(df, [x_col, y_col, hue_col], [x_col, y_col])
    with publication_style(palette=palette):
        fig, ax = plt.subplots(figsize=figsize or figure_size("single", 0.8))
        scatter_kwargs = {
            "data": df,
            "x": x_col,
            "y": y_col,
            "s": 24,
            "alpha": 0.8,
            "edgecolor": "white",
            "linewidth": 0.35,
            "ax": ax,
        }
        if hue_col:
            scatter_kwargs.update(hue=hue_col, palette=palette)
        else:
            scatter_kwargs["color"] = sns.color_palette(palette)[0]
        sns.scatterplot(**scatter_kwargs)
        if regression:
            sns.regplot(
                data=df,
                x=x_col,
                y=y_col,
                scatter=False,
                ci=ci,
                color="0.25",
                line_kws={"linewidth": 1.0},
                ax=ax,
            )
        _finish_axis(ax, x_label or x_col, y_label or y_col, title)
    return fig, ax


def create_bar_plot(
    df,
    x_col,
    y_col,
    hue_col=None,
    title=None,
    figsize=None,
    estimator="mean",
    errorbar=("ci", 95),
    show_points=True,
    palette=DEFAULT_PALETTE,
    x_label=None,
    y_label=None,
):
    """Create an explicitly summarized bar plot, optionally retaining raw observations."""
    _validate_dataframe(df, [x_col, y_col, hue_col], [y_col])
    with publication_style(palette=palette):
        fig, ax = plt.subplots(figsize=figsize or figure_size("single", 0.8))
        kwargs = {
            "data": df,
            "x": x_col,
            "y": y_col,
            "estimator": estimator,
            "errorbar": errorbar,
            "capsize": 0.12,
            "err_kws": {"linewidth": 0.8},
            "ax": ax,
        }
        if hue_col:
            kwargs.update(hue=hue_col, palette=palette)
        else:
            kwargs["color"] = sns.color_palette(palette)[0]
        sns.barplot(**kwargs)
        if show_points:
            point_kwargs = {
                "data": df,
                "x": x_col,
                "y": y_col,
                "color": "0.15",
                "size": 2.5,
                "alpha": 0.65,
                "jitter": False,
                "ax": ax,
            }
            if hue_col:
                point_kwargs.update(hue=hue_col, dodge=True, palette=palette, legend=False)
                point_kwargs.pop("color")
            sns.stripplot(**point_kwargs)
        ax.set_ylim(bottom=0)
        _finish_axis(ax, x_label or x_col, y_label or y_col, title)
    return fig, ax


def create_distribution_plot(
    df,
    x_col,
    y_col,
    hue_col=None,
    kind="box",
    title=None,
    figsize=None,
    show_points=True,
    palette=DEFAULT_PALETTE,
    x_label=None,
    y_label=None,
):
    """Create a box or violin distribution plot with optional raw observations."""
    _validate_dataframe(df, [x_col, y_col, hue_col], [y_col])
    if kind not in {"box", "violin"}:
        raise ValueError("kind must be 'box' or 'violin'")

    with publication_style(palette=palette):
        fig, ax = plt.subplots(figsize=figsize or figure_size("single", 0.8))
        kwargs = {"data": df, "x": x_col, "y": y_col, "ax": ax}
        if hue_col:
            kwargs.update(hue=hue_col, palette=palette)
        else:
            kwargs["color"] = sns.color_palette(palette)[0]
        if kind == "box":
            sns.boxplot(**kwargs, width=0.55, fliersize=0, linewidth=0.8)
        else:
            sns.violinplot(**kwargs, inner="box", cut=0, linewidth=0.8)
        if show_points:
            sns.stripplot(
                data=df,
                x=x_col,
                y=y_col,
                color="0.15",
                size=2.5,
                alpha=0.6,
                jitter=False,
                ax=ax,
            )
        _finish_axis(ax, x_label or x_col, y_label or y_col, title)
    return fig, ax


def create_box_plot(df, x_col, y_col, hue_col=None, title=None, figsize=None, **kwargs):
    """Compatibility wrapper for a box distribution plot."""
    return create_distribution_plot(
        df, x_col, y_col, hue_col, "box", title, figsize, **kwargs
    )


def create_violin_plot(df, x_col, y_col, hue_col=None, title=None, figsize=None, **kwargs):
    """Compatibility wrapper for a violin distribution plot."""
    return create_distribution_plot(
        df, x_col, y_col, hue_col, "violin", title, figsize, **kwargs
    )


def create_line_plot(
    df,
    x_col,
    y_col,
    hue_col=None,
    title=None,
    figsize=None,
    estimator=None,
    errorbar=None,
    units=None,
    palette=DEFAULT_PALETTE,
    x_label=None,
    y_label=None,
):
    """Create a line plot; raw observations are preserved unless estimator is explicit."""
    _validate_dataframe(df, [x_col, y_col, hue_col, units], [y_col])
    with publication_style(palette=palette):
        fig, ax = plt.subplots(figsize=figsize or figure_size("single", 0.7))
        kwargs = {
            "data": df,
            "x": x_col,
            "y": y_col,
            "estimator": estimator,
            "errorbar": errorbar,
            "units": units,
            "marker": "o",
            "markersize": 3,
            "linewidth": 1.0,
            "ax": ax,
        }
        if hue_col:
            kwargs.update(hue=hue_col, palette=palette)
        else:
            kwargs["color"] = sns.color_palette(palette)[0]
        sns.lineplot(**kwargs)
        _finish_axis(ax, x_label or x_col, y_label or y_col, title)
    return fig, ax


def create_heatmap(
    df,
    title=None,
    figsize=None,
    annot=True,
    method="pearson",
    mask_upper=True,
    cmap="vlag",
):
    """Create a correlation heatmap from numeric columns."""
    _validate_dataframe(df)
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        raise ValueError("df must contain at least two numeric columns")
    correlation = numeric_df.corr(method=method)
    mask = np.triu(np.ones_like(correlation, dtype=bool), k=1) if mask_upper else None
    with publication_style():
        fig, ax = plt.subplots(figsize=figsize or figure_size("single", 0.9))
        sns.heatmap(
            correlation,
            mask=mask,
            annot=annot,
            cmap=cmap,
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            fmt=".2f",
            linewidths=0.3,
            cbar_kws={"shrink": 0.75, "label": f"{method.title()} correlation"},
            ax=ax,
        )
        _finish_axis(ax, title=title)
    return fig, ax


def save_figure(fig, output_path, formats=None, dpi=600, transparent=False):
    """Save a PNG by default; export other formats only when explicitly requested."""
    output_path = Path(output_path)
    if formats is None:
        formats = ("png",)
    formats = tuple(str(fmt).lower().lstrip(".") for fmt in formats)
    supported = {"png", "pdf", "svg", "tif", "tiff"}
    unsupported = sorted(set(formats) - supported)
    if unsupported:
        raise ValueError(f"Unsupported formats: {', '.join(unsupported)}")

    base = output_path.with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for fmt in formats:
        path = base.with_suffix(f".{fmt}")
        fig.savefig(
            path,
            format=fmt,
            dpi=dpi if fmt in {"png", "tif", "tiff"} else None,
            bbox_inches="tight",
            transparent=transparent,
        )
        outputs.append(path)
    return outputs


def save_plot(fig, filename, format=None):
    """Backward-compatible export helper; defaults to PNG."""
    formats = (format,) if format else None
    return save_figure(fig, filename, formats=formats)[0]
