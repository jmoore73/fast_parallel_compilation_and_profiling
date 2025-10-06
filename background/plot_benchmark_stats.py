import os

from background.helper import fig_1

results_dir = [
    "feynman_stats_v2.csv",
    "mqtbench_stats_v2.csv",
    "qasmbench_stats_v2.csv",
    "red_queen_stats_v2.csv",
    "veri-q_stats_v2.csv"
]

names = ["Feynman", "MQTBench", "QASMBench", "Red Queen", "Veri-Q"]

if __name__ == '__main__':

    os.makedirs("plots", exist_ok=True)
    fig_1(results_dir, names)
