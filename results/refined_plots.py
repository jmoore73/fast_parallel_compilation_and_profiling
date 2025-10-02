import os
import pandas as pd
from matplotlib import pyplot as plt

def plot_lines_icrc_paper(folder, source_diff, dataset):
    for source_d in source_diff:
        source = f"all_{dataset}_results_{source_d}.csv"
        file_name_prepend = f"refined_{source_d}_{dataset}_icrc"
        df = pd.read_csv(source)

        variables = ["Cores", "Width", "Depth", "Density"]
        components = ["Speedup", "Gate Overhead", "Depth Overhead", "SWAP Overhead"]

        for variable in variables:
            if variable == "Cores":
                x_label = "Number of Cores"
            elif variable == "Width":
                x_label = "Width (Qubits)"
            elif variable == "Depth":
                x_label = "Depth (Gates)"
            elif variable == "Density":
                x_label = "Gate Density (%)"

            fig, axes = plt.subplots(2, 2, figsize=(6, 4), sharey=False)
            axes = axes.flatten()

            avg_line_handle = None

            for i, component in enumerate(components):
                if component == "Speedup":
                    y_label = "Speedup Factor"
                else:
                    y_label = f"{component} (%)"

                ax = axes[i]  # Get the current subplot

                # Set color and line colors based on component
                if component == 'Speedup':
                    colors = ['red' if val < 1 else 'green' for val in df[component]]
                    line_colors = ['red', 'green', 'black']
                else:
                    colors = ['red' if val > 0 else 'green' for val in df[component]]
                    line_colors = ['green', 'red', 'black']

                # Scatter plot
                scatter = ax.scatter(df[variable], df[component], color=colors, alpha=0.1)
                ax.set_title(f'{variable} vs {component}')
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.grid(True)

                # Group and plot min, max, avg lines
                grouped = df.groupby(variable)[component].agg(['min', 'max', 'mean'])
                min_line, = ax.plot(grouped.index, grouped['min'], color=line_colors[0], linestyle='--', label='Min')
                max_line, = ax.plot(grouped.index, grouped['max'], color=line_colors[1], linestyle='--', label='Max')
                avg_line, = ax.plot(grouped.index, grouped['mean'], color=line_colors[2], linestyle='-', label='Avg')
                avg_line_handle = avg_line

            # Add legend to last used subplot
            if avg_line_handle:
                fig.legend(handles=[avg_line_handle], loc='upper center', ncol=1, bbox_to_anchor=(0.5, 0.03))

            plt.tight_layout()
            plt.savefig(f"{folder}/{file_name_prepend}_{variable}.pdf", bbox_inches='tight')
            # plt.show()
            plt.close(fig)  # Close the figure to prevent overlap

