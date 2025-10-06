import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def fig_1(results_dir, names):
    fig, axes = plt.subplots(2, 1, figsize=(6, 12))  # side-by-side
    ax1, ax2 = axes

    # --- Subplot (a): Scatter plot ---
    colors = sns.color_palette('bright', n_colors=len(results_dir))
    cmap = dict(zip(results_dir, colors))
    nmap = dict(zip(results_dir, names))

    for results_file in results_dir:
        file_name = results_file.replace("_stats_v2.csv", '')
        df = pd.read_csv("stats/" + results_file)
        df.columns = df.columns.str.strip()
        df.plot(
            kind='scatter',
            y='depth',
            x='width',
            ax=ax1,
            label=nmap[results_file] + f" ({len(df['density'])} circuits)",
            color=cmap[results_file],
            alpha=0.7
        )

    ax1.set_title("(a) Benchmark Suites Statistics", fontsize=10)
    ax1.set_xlabel("Width (Number of Qubits)", fontsize=10)
    ax1.set_ylabel("Circuit Depth (Gates)", fontsize=10)
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax1.grid()
    ax1.legend(fontsize=8)

    # --- Subplot (b): Boxplot with density counts ---
    all_data = []
    all_labels = []
    for results_file in results_dir:
        df = pd.read_csv("stats/" + results_file)
        df.columns = df.columns.str.strip()
        all_data.append(df['density'])
        # Add count of densities to label
        label_with_count = f"{nmap[results_file]}\n({len(df['density'])} circuits)"
        all_labels.append(label_with_count)

    bp = ax2.boxplot(
        all_data,
        labels=all_labels,
        patch_artist=True
    )

    # Fill boxes in purple
    for patch in bp['boxes']:
        patch.set_facecolor("plum")
    for median in bp['medians']:
        median.set_color("black")

    ax2.set_title("(b) Density Distribution per Benchmark Suite", fontsize=10)
    ax2.set_ylabel("Density", fontsize=10)
    ax2.grid(axis='y')
    ax2.tick_params(axis="x", rotation=45)

    plt.subplots_adjust(bottom=0.25, wspace=0.3)  # better spacing
    plt.savefig("plots/combined_figure_1.pdf", bbox_inches='tight')
    plt.show()

