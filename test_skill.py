"""真实渲染测试：验证出版级绘图核心库。"""

import importlib.util
import tempfile
import unittest
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"

import sys

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(EXAMPLES))

from plotting_functions import (
    audit_dataframe,
    create_bar_plot,
    create_box_plot,
    create_distribution_plot,
    create_heatmap,
    create_line_plot,
    create_scatter_plot,
    create_violin_plot,
    figure_size,
    publication_style,
    save_figure,
    save_plot,
)
from plotting_examples import (
    example_bar_plot,
    example_heatmap,
    example_scatter_plot,
    generic_plot_template,
)


class PublicationPlottingTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "group": ["A", "A", "A", "B", "B", "B"],
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1.0, 2.2, 2.8, 1.5, 2.6, 3.4],
            }
        )

    def tearDown(self):
        plt.close("all")

    def test_required_files_exist(self):
        for relative in (
            "SKILL.md",
            "README.md",
            "scripts/plotting_functions.py",
            "examples/plotting_examples.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_audit_dataframe_reports_quality_signals(self):
        dirty = pd.concat([self.df, self.df.iloc[[0]]], ignore_index=True)
        dirty.loc[1, "y"] = np.nan
        report = audit_dataframe(dirty, group_cols=["group"])
        self.assertEqual(report["rows"], 7)
        self.assertEqual(report["duplicate_rows"], 1)
        self.assertEqual(report["missing_values"]["y"], 1)
        self.assertEqual(report["group_counts"]["group"]["A"], 4)

    def test_figure_size_supports_publication_widths(self):
        single = figure_size("single", aspect=0.75)
        double = figure_size("double", aspect=0.5)
        self.assertAlmostEqual(single[0], 89 / 25.4)
        self.assertAlmostEqual(double[0], 180 / 25.4)
        self.assertAlmostEqual(single[1], single[0] * 0.75)

    def test_publication_style_does_not_leak_global_state(self):
        original = plt.rcParams["font.size"]
        with publication_style(font_size=7):
            self.assertEqual(plt.rcParams["font.size"], 7)
        self.assertEqual(plt.rcParams["font.size"], original)

    def test_plot_functions_render_without_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            warnings.filterwarnings(
                "ignore",
                message="vert: bool will be deprecated",
                category=PendingDeprecationWarning,
            )
            figures = [
                create_scatter_plot(self.df, "x", "y", hue_col="group")[0],
                create_bar_plot(self.df, "group", "y", show_points=True)[0],
                create_distribution_plot(self.df, "group", "y", kind="box")[0],
                create_box_plot(self.df, "group", "y")[0],
                create_violin_plot(self.df, "group", "y")[0],
                create_line_plot(self.df, "x", "y", hue_col="group", estimator=None)[0],
                create_heatmap(self.df[["x", "y"]])[0],
            ]
        self.assertTrue(all(fig.axes for fig in figures))

    def test_missing_column_has_clear_error(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            create_scatter_plot(self.df, "missing", "y")

    def test_save_figure_exports_png_and_pdf(self):
        fig, _ = create_scatter_plot(self.df, "x", "y")
        with tempfile.TemporaryDirectory() as tmp:
            outputs = save_figure(fig, Path(tmp) / "figure", formats=("png", "pdf"))
            self.assertEqual({path.suffix for path in outputs}, {".png", ".pdf"})
            self.assertTrue(all(path.stat().st_size > 0 for path in outputs))

            legacy = Path(tmp) / "legacy.png"
            save_plot(fig, legacy)
            self.assertGreater(legacy.stat().st_size, 0)

    def test_save_figure_defaults_to_png_only(self):
        fig, _ = create_scatter_plot(self.df, "x", "y")
        with tempfile.TemporaryDirectory() as tmp:
            outputs = save_figure(fig, Path(tmp) / "default-output.pdf")
            self.assertEqual([path.suffix for path in outputs], [".png"])
            self.assertTrue(outputs[0].is_file())
            self.assertFalse((Path(tmp) / "default-output.pdf").exists())

    def test_examples_are_nonempty_and_compile(self):
        for code in (example_scatter_plot(), example_bar_plot(), example_heatmap()):
            self.assertTrue(code.strip())
            compile(code, "<plot-example>", "exec")
        self.assertEqual(generic_plot_template("unknown")["title"], "散点图模板")


if __name__ == "__main__":
    unittest.main(verbosity=2)
