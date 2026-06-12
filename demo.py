"""Print a concise overview of the publication plotting core."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from plotting_functions import PUBLICATION_WIDTHS_MM, figure_size


def main():
    print("data-analysis-plotting: publication-grade core library")
    print("\nCore capabilities:")
    print("- audit DataFrames without silently modifying data")
    print("- render scatter, summary, distribution, line, and correlation plots")
    print("- use local publication styles and colorblind-safe defaults")
    print("- export only 600 DPI PNG by default; other formats require explicit requests")
    print("\nPublication widths:")
    for name, width_mm in PUBLICATION_WIDTHS_MM.items():
        width_inches, _ = figure_size(name)
        print(f"- {name}: {width_mm} mm ({width_inches:.2f} in)")
    print("\nRun verification with: python -m unittest -v test_skill.py")


if __name__ == "__main__":
    main()
