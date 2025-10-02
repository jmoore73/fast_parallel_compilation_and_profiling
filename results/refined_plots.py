import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.colors import Normalize, LinearSegmentedColormap

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
                    colors = ['orange' if val < 1 else 'blue' for val in df[component]]
                    line_colors = ['orange', 'blue', 'black']
                else:
                    colors = ['orange' if val > 0 else 'blue' for val in df[component]]
                    line_colors = ['blue', 'orange', 'black']

                if (source_d == "10k_100k") and (dataset == "benchmark_basic") and (variable == "Depth"):
                    # ax.tick_params(axis='x', rotation=45)
                    ax.set_xticks([25000, 50000, 75000, 100000])

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


def custom_cmap(component, vmax, vmin):
    if component == "Speedup" or component.__contains__("Overhead"):
        cmap = "custom"
    if cmap == "custom":
        if component == "Speedup":
            if vmin < 1:
                colors = ["black", "white", "purple"]
                nodes = [0.0, (1 - vmin) / (vmax - vmin), 1.0]
            else:
                vmin = 1
                colors = ["white", "purple"]
                nodes = [0.0, 1.0]
            cmap = LinearSegmentedColormap.from_list("CustomMap", list(zip(nodes, colors)))
        if component.__contains__("Overhead"):
            match component.split(" ")[0]:
                case "SWAP":
                    colour = "magenta"
                case "Depth":
                    colour = "orange"
                case "Gate":
                    colour = "blue"
            if vmin < 0:
                colors = [colour, "white", "black"]
                nodes = [0.0, (0 - vmin) / (vmax - vmin), 1.0]
            else:
                colors = [colour, "white"]
                nodes = [0.0, 1.0]
            cmap = LinearSegmentedColormap.from_list("CustomMap", list(zip(nodes, colors)))
    return cmap, vmin


def generate_single_heatmap(CSV_FILE, FILE_NAME_PREPEND, PLOT_DIR, DENSITY=1.0, COMPONENT="Speedup", CORES=16, SAME_SCALE=False, ANNOTATE=True, SAVE=True):
    big_df = pd.read_csv(CSV_FILE)

    big_df = big_df[big_df['Cores'] == CORES]
    big_df = big_df[big_df['Density'] == DENSITY]

    vavg = big_df[COMPONENT].mean()
    vmin = big_df[COMPONENT].min()
    vmax = big_df[COMPONENT].max()

    cmap, vmin = custom_cmap(COMPONENT, vmax, vmin)

    norm = Normalize(vmin=vmin, vmax=vmax)
    # Create a figure with a single subplot
    fig, ax = plt.subplots(figsize=(5, 4))

    # Process the data
    subset_cleaned = big_df.dropna(subset=["Gate Overhead"])
    subset_cleaned = subset_cleaned.loc[subset_cleaned.groupby(['Width', 'Depth'])[COMPONENT].idxmax()]

    # Create the heatmap data
    heatmap_data = subset_cleaned.pivot(index='Width', columns='Depth', values=COMPONENT)
    heatmap_data = heatmap_data.sort_index(ascending=True)  # Sort 'Width'
    heatmap_data = heatmap_data.sort_index(axis=1, ascending=True)  # Sort 'Depth'
    heatmap_data = heatmap_data.iloc[::-1]  # Reverse the order of rows for visual purposes

    # Create the heatmap
    sns.heatmap(
        heatmap_data,
        ax=ax,
        annot=ANNOTATE,
        fmt=".1f",
        cmap=cmap,
        norm=norm,
        vmin=vmin,
        vmax=vmax,
        cbar=True  # Directly include the colorbar
    )

    if "Overhead" in COMPONENT:
        unit = " (%)"
    else:
        unit = ""
    # Get the colorbar from the figure
    cbar = ax.collections[0].colorbar
    cbar.set_label((COMPONENT + unit), rotation=90, labelpad=15)

    plt.yticks(rotation=0)
    plt.xticks(rotation=45)

    # Set labels
    ax.set_xlabel('Depth (Gates)')
    ax.set_ylabel('Width (Qubits)')
    ax.set_title(f'Heatmap for {COMPONENT} using {CORES} Cores')

    # Adjust layout
    plt.tight_layout()

    # Save if needed
    if SAVE:
        plt.savefig(f"{PLOT_DIR}/{FILE_NAME_PREPEND}_{CORES}_{DENSITY}_{COMPONENT}.pdf")
    else:
        plt.show()


