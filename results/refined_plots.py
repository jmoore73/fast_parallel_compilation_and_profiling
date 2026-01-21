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
                    colors = ['#009E73' if val < 1 else '#CC79A7' for val in df[component]]
                    line_colors = ['#009E73', '#CC79A7', 'black']
                else:
                    colors = ['orange' if val > 0 else 'blue' for val in df[component]]
                    line_colors = ['blue', 'orange', 'black']

                if (source_d == "10k_100k") and (dataset == "benchmark_basic") and (variable == "Depth"):
                    # ax.tick_params(axis='x', rotation=45)
                    ax.set_xticks([25000, 50000, 75000, 100000])

                # Scatter plot
                scatter = ax.scatter(df[variable], df[component], color=colors, alpha=0.5)
                ax.set_title(f'{variable} vs {component}')
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.grid(True)

                # Group and plot min, max, avg lines
                grouped = df.groupby(variable)[component].agg(['min', 'max', 'mean'])
                avg_line, = ax.plot(grouped.index, grouped['mean'], color=line_colors[2], linestyle='-', label='Average')
                avg_line_handle = avg_line
                if component == 'Speedup':
                    speedup_min_line_handle, = ax.plot(grouped.index, grouped['min'], color=line_colors[0],
                                                       linestyle='dashdot', label='Speedup Min')
                    speedup_max_line_handle, = ax.plot(grouped.index, grouped['max'], color=line_colors[1],
                                                       linestyle='--', label='Speedup Max')
                else:
                    min_line_handle, = ax.plot(grouped.index, grouped['min'], color=line_colors[0],
                                                       linestyle='dashdot', label='Overheads Min')
                    max_line_handle, = ax.plot(grouped.index, grouped['max'], color=line_colors[1],
                                                       linestyle='--',label='Overheads Max')

            # Add legend to last used subplot
            if avg_line_handle:
                fig.legend(handles=[speedup_min_line_handle, speedup_max_line_handle, avg_line_handle, min_line_handle, max_line_handle],
                           loc='upper center', ncol=3, bbox_to_anchor=(0.5, 0.03))

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
                colors = ["black", "white", "darkviolet"]
                nodes = [0.0, (1 - vmin) / (vmax - vmin), 1.0]
            else:
                vmin = 1
                colors = ["white", "darkviolet"]
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


def generate_multiple_heatmaps(CSV_FILE, FILE_NAME_PREPEND, PLOT_DIR,
                               DENSITY=1.0, COMPONENT="Speedup",
                               CORES_LIST=[4, 8, 16],
                               SAME_SCALE=False, ANNOTATE=True, SAVE=True):
    # Load data once
    big_df = pd.read_csv(CSV_FILE)
    big_df = big_df[big_df['Density'] == DENSITY]

    # Compute shared scale if SAME_SCALE is True
    if SAME_SCALE:
        vmin = big_df[COMPONENT].min()
        vmax = big_df[COMPONENT].max()
    else:
        vmin = vmax = None

    # Create figure with subplots horizontally
    fig, axes = plt.subplots(1, len(CORES_LIST), figsize=(4 * len(CORES_LIST), 4), sharey=True)

    if len(CORES_LIST) == 1:
        axes = [axes]  # ensure iterable

    for i, cores in enumerate(CORES_LIST):
        df_core = big_df[big_df['Cores'] == cores]

        # Drop missing and pick max per (Width, Depth)
        subset_cleaned = df_core.dropna(subset=["Gate Overhead"])
        subset_cleaned = subset_cleaned.loc[
            subset_cleaned.groupby(['Width', 'Depth'])[COMPONENT].idxmax()
        ]

        # Pivot for heatmap
        heatmap_data = subset_cleaned.pivot(index='Width', columns='Depth', values=COMPONENT)
        heatmap_data = heatmap_data.sort_index(ascending=True)
        heatmap_data = heatmap_data.sort_index(axis=1, ascending=True)
        heatmap_data = heatmap_data.iloc[::-1]

        # Determine color scale
        if not SAME_SCALE:
            vmin = heatmap_data.min().min()
            vmax = heatmap_data.max().max()

        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap, vmin = custom_cmap(COMPONENT, vmax, vmin)

        # Plot heatmap
        sns.heatmap(
            heatmap_data,
            ax=axes[i],
            annot=ANNOTATE,
            fmt=".1f",
            cmap=cmap,
            norm=norm,
            vmin=vmin,
            vmax=vmax,
            cbar=(i == len(CORES_LIST) - 1)  # show colorbar only on last heatmap
        )

        if i == len(CORES_LIST) - 1:
            if "Overhead" in COMPONENT:
                unit = " (%)"
            else:
                unit = ""
            # Get the colorbar from the figure
            cbar = axes[i].collections[0].colorbar
            cbar.set_label((COMPONENT + unit), rotation=90, labelpad=15)

        axes[i].set_title(f"{COMPONENT} - {cores} Cores")
        axes[i].set_xlabel("Depth (Gates)")
        if i == 0:
            axes[i].set_ylabel("Width (Qubits)")
        else:
            axes[i].yaxis.set_visible(False)

        axes[i].tick_params(axis='x', rotation=45)
        axes[i].tick_params(axis='y', rotation=0)

    plt.tight_layout()

    if SAVE:
        plt.savefig(f"{PLOT_DIR}/{FILE_NAME_PREPEND}_multi_{COMPONENT}_{DENSITY}.pdf")
    else:
        plt.show()


def generate_full_heatmap(CSV_FILE, FILE_NAME_PREPEND, PLOT_DIR, DENSITY=1.0,
                          COMPONENTS=None, SAME_SCALE=False,ANNOTATE=True, SAVE=True):
    nrows = 3
    cmap = "custom"

    df = pd.read_csv(CSV_FILE)
    big_df = df[df['Density'] == DENSITY]

    if COMPONENTS is None:
        COMPONENTS = ["Speedup", "SWAP Overhead", "Depth Overhead", "Gate Overhead"]
    for component in COMPONENTS:
        print("*" * 20)
        print(component)
        vavg = big_df[component].mean()
        vmin = big_df[component].min()
        vmax = big_df[component].max()
        print("min: %.2f" % vmin)
        print("max: %.2f" % vmax)
        print("avg: %.2f" % vavg)

        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap, vmin = custom_cmap(component, vmax, vmin)

        core_counts = big_df['Cores'].unique()
        core_counts.sort()
        num_cores = len(core_counts)
        ncols = math.ceil(num_cores / nrows)
        if nrows * ncols < num_cores:
            raise ValueError("The grid dimensions are too small for the number of core counts.")

        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 4 * nrows), sharey=True)
        axes_flat = axes.flat

        for i, (ax, cores) in enumerate(zip(axes_flat, core_counts)):
            subset_ = big_df[big_df['Cores'] == cores]
            heatmap_data = subset_.pivot(index='Width', columns='Depth', values=component)
            heatmap_data = heatmap_data.sort_index(ascending=True)  # Sort 'Width'
            heatmap_data = heatmap_data.sort_index(axis=1, ascending=True)  # Sort 'Depth'
            heatmap_data = heatmap_data.iloc[::-1]
            sns.heatmap(
                heatmap_data, ax=ax, annot=ANNOTATE, fmt=".1f", cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cbar=False
            )
            ax.set_title(f'Cores: {cores}')
            ax.set_xlabel('Depth (Gates)')
            if i % ncols == 0:
                ax.set_ylabel('Width (Qubits)')
                ax.tick_params(axis='y', rotation=0)

        cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7])  # Adjust position and size as needed
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cbar = fig.colorbar(sm, cax=cbar_ax)
        cbar.set_label(component)

        for j in range(i + 1, nrows * ncols):
            fig.delaxes(axes_flat[j])

        fig.suptitle(f'Heatmaps for {component}', fontsize=16)

        plt.tight_layout(rect=[0, 0, 0.9, 0.95])
        if SAVE:
            plt.savefig(f"{PLOT_DIR}/{FILE_NAME_PREPEND}_{component}_{DENSITY}.png")
            plt.savefig(f"{PLOT_DIR}/{FILE_NAME_PREPEND}_{component}_{DENSITY}.pdf")
        else:
            plt.show()

