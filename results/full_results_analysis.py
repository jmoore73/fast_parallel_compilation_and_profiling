import os

from refined_plots import plot_lines_icrc_paper


if __name__ == '__main__':

    for dataset in ["benchmark_sabre", "random_sabre", "random_basic", "benchmark_basic",
                    "benchmark_pytket", "random_pytket"]:
        if "benchmark" in dataset:
            source_diffs = ["10k_100k"]
        elif dataset == "random_sabre":
            source_diffs = ["full", "0.2_20q"]
        else:
            source_diffs = ["full"]

        plot_folder = "icrc_pdf"
        os.makedirs(plot_folder, exist_ok=True)
        plot_lines_icrc_paper(plot_folder, source_diffs, dataset)
