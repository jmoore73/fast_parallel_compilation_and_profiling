import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def box_plots_depth_width_all_suites(results_dir, names):
    fig, (ax_depth, ax_width) = plt.subplots(1, 2, figsize=(6, 4), sharey=False)

    depth_all = []
    width_all = []

    # Collect depth and width from all suites
    for results_file in results_dir:
        df = pd.read_csv("stats/" + results_file)
        df.columns = df.columns.str.strip()
        depth_all.extend(df['depth'])
        width_all.extend(df['width'])

    # Depth boxplot
    bp_depth = ax_depth.boxplot(
        depth_all,
        labels=["Depth"],
        patch_artist=True,
    )
    for patch in bp_depth['boxes']:
        patch.set_facecolor("cyan")
    for median in bp_depth['medians']:
        median.set_color("black")

    ax_depth.set_yscale('log')
    ax_depth.set_ylabel("Depth (layers of gates)")
    ax_depth.grid(axis='y', which='both')

    # Width boxplot
    bp_width = ax_width.boxplot(
        width_all,
        labels=["Width"],
        patch_artist=True,
    )
    for patch in bp_width['boxes']:
        patch.set_facecolor("plum")
    for median in bp_width['medians']:
        median.set_color("black")

    ax_width.set_ylabel("Width (qubits)")
    ax_width.grid(axis='y', which='both')

    plt.suptitle("Depth and Width Characteristics (All Suites Combined)", fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # leave space for suptitle
    plt.savefig("plots/depth_width_boxplot_side_by_side.pdf", bbox_inches='tight')
    plt.show()


def box_plots_density_per_suite(results_dir, names):
    fig, ax = plt.subplots(figsize=(6, 4))
    nmap = dict(zip(results_dir, names))
    all_data = []
    all_labels = []
    for results_file in results_dir:
        df = pd.read_csv("stats/" + results_file)
        df.columns = df.columns.str.strip()
        all_data.append(df['density'])
        all_labels.append(nmap[results_file])
    # Create boxplot with means
    bp = ax.boxplot(
        all_data,
        labels=all_labels,
        patch_artist=True
    )
    # Fill boxes in purple
    for patch in bp['boxes']:
        patch.set_facecolor("plum")
    for median in bp['medians']:
        median.set_color("black")
    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.2)  # increase if necessary (0.2 -> 0.4)
    # plt.tight_layout()
    ax.set_title("Density Distribution per Benchmark Suite", fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.grid(axis='y')
    plt.savefig("plots/density_boxplot.pdf", bbox_inches='tight')
    plt.show()


def plot_suites_depth_width_scatter_density_coloured(results_dir, names):
    fig, ax = plt.subplots(figsize=(7, 4))
    for results_file in results_dir:
        file_name = results_file.replace("_stats_v2.csv", '')
        df = pd.read_csv("stats/" + results_file)
        df.columns = df.columns.str.strip()

        sc = ax.scatter(
            df['width'],
            df['depth'],
            c=df['density'],
            cmap="cividis",
            alpha=0.7,
        )
    # add colorbar for density scale
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Density")
    plt.title("Benchmark Suites Statistics", fontsize=10)
    plt.xlabel("Width", fontsize=10)
    plt.ylabel("Depth", fontsize=10)
    plt.xlim(left=0)  # , right=200)
    plt.ylim(bottom=0)  # , top=3e6)
    plt.grid()
    plt.savefig("plots/all_suites_denisty.pdf", bbox_inches='tight')
    plt.show()


def plot_suites_depth_width_scatter_colour_coded(results_dir, names):
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = sns.color_palette('bright', n_colors=len(results_dir))
    cmap = dict(zip(results_dir, colors))
    nmap = dict(zip(results_dir, names))
    for results_file in results_dir:
        file_name = results_file.replace("_stats_v2.csv", '')
        df = pd.read_csv("stats/" + results_file)
        print(df.head(3))
        print(file_name, df.shape)
        df.columns = df.columns.str.strip()
        df.plot(
            kind='scatter',
            y='depth',
            x='width',
            ax=ax,
            label=nmap[results_file],
            color=cmap[results_file]
        )
    plt.title("Benchmark Suites Statistics", fontsize=10)
    plt.xlabel("Width (Number of Qubits)", fontsize=10)
    plt.ylabel("Circuit Depth (Gates)", fontsize=10)
    plt.xlim(left=0)  # , right=200)
    plt.ylim(bottom=0)  # , top=1e6)
    plt.grid()
    plt.legend()
    plt.savefig("plots/all_suites.pdf", bbox_inches='tight')
    plt.show()
