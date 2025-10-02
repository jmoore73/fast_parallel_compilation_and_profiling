import os

from background.helper import box_plots_depth_width_all_suites, box_plots_density_per_suite, \
    plot_suites_depth_width_scatter_density_coloured, plot_suites_depth_width_scatter_colour_coded

results_dir = [
    "feynman_stats_v2.csv",
    "mqtbench_stats_v2.csv",
    "qasmbench_stats_v2.csv",
    "red_queen_stats_v2.csv",
    "supermarq_stats_v2.csv",
    "veri-q_stats_v2.csv"
]

names = ["Feynman", "MQTBench", "QASMBench", "Red Queen", "Supermarq", "Veri-Q"]

if __name__ == '__main__':

    os.makedirs("plots", exist_ok=True)

    plot_suites_depth_width_scatter_colour_coded(results_dir, names)
    plot_suites_depth_width_scatter_density_coloured(results_dir, names)
    box_plots_density_per_suite(results_dir, names)
    box_plots_depth_width_all_suites(results_dir, names)
