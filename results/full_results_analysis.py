import os

from refined_plots import plot_lines_icrc_paper, generate_single_heatmap, generate_multiple_heatmaps, \
    generate_full_heatmap

plot_folder = "icrc_r_pdf"
heatmaps = True


if __name__ == '__main__':

    os.makedirs(plot_folder, exist_ok=True)
    os.makedirs("heatmaps", exist_ok=True)

    if not heatmaps:
        for dataset in ["benchmark_sabre", "random_sabre",
                        "random_basic", "benchmark_basic",
                        "benchmark_pytket", "random_pytket",
                        "linear_proc", "qiskit2"
                        ]:
            if "benchmark" in dataset:
                source_diffs = ["10k_100k"]
                if dataset == 'benchmark_sabre':
                    source_diffs = ["10k_100k", "vqe"]
            elif dataset == "random_sabre":
                source_diffs = ["full", "0.2_20q"]
            else:
                source_diffs = ["full"]

            print(dataset)

            plot_lines_icrc_paper(plot_folder, source_diffs, dataset)

    if heatmaps:
        generate_single_heatmap("all_random_sabre_results_full.csv",
                                "random_sabre_single_heatmap",
                                "heatmaps",
                                COMPONENT="SWAP Overhead", DENSITY=1.0, CORES=16,
                                SAME_SCALE=False, ANNOTATE=True, SAVE=True)

        generate_multiple_heatmaps(
            "all_random_sabre_results_full.csv",
            "random_sabre_dual_heatmap",
            "heatmaps",
            COMPONENT="SWAP Overhead", DENSITY=1.0, CORES_LIST=[4,16],
            SAME_SCALE=True, ANNOTATE=True, SAVE=True
        )

        generate_multiple_heatmaps(
            "all_random_sabre_results_full.csv",
            "random_sabre_triple_heatmap",
            "heatmaps",
            COMPONENT="SWAP Overhead", DENSITY=1.0, CORES_LIST=[4, 10, 16],
            SAME_SCALE=True, ANNOTATE=True, SAVE=True
        )

        generate_full_heatmap(
            "all_random_sabre_results_full.csv",
            "random_sabre_full_heatmap",
            "heatmaps",
            SAME_SCALE=False, ANNOTATE=True, SAVE=True
        )

    exit(0)
