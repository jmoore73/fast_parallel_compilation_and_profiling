import os

import pandas as pd
import matplotlib.pyplot as plt

from refined_plots import plot_lines_icrc_paper, generate_single_heatmap, generate_multiple_heatmaps

plot_folder = "icrc_pdf"

if __name__ == '__main__':

    os.makedirs(plot_folder, exist_ok=True)

    variables = ["Cores", "Width", "Depth"]
    components = ["Speedup", "Gate Overhead", "Depth Overhead", "SWAP Overhead"]

    for data in ["benchmark", "random"]:
        if data == "benchmark":
            source_d = "10k_100k"
        else:
            source_d = "full"
        for dataset in ["sabre", "basic", "pytket"]:
            source = f"all_{data}_{dataset}_results_{source_d}.csv"
            print(source)
            df = pd.read_csv(source)
            if data == "random":
                df = df[df['Density'] == 1.0]
            print(df.head())

    exit(0)



