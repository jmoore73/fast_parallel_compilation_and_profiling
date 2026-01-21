import pandas as pd
from matplotlib import pyplot as plt

SAVE = True
PLOT_DIR = "icrc_pdf"
DATA_CSV = "memory_summary.csv"

fixed_density = 1.0
fixed_width = 100
fixed_depth = 40000


if __name__ == "__main__":

    df = pd.read_csv(DATA_CSV)
    # df["Parallel maxrss_kb"] = df["Parallel maxrss_kb temp"]*df["Cores"]

    cmap = [
        "#000000",  # black
        "#E69F00",  # orange
        "#56B4E9",  # sky blue
        "#009E73",  # bluish green
        "#F0E442",  # yellow
        "#0072B2",  # blue
        "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
    ]

    cores_list = sorted(df["Cores"].unique())

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Memory Usage for Parallel Compilation Against Qiskit")

    # plot 1: vary depth
    ax = axs[0,0]
    for i, cores in enumerate(cores_list):
        subset = df[
            (df["Width"] == fixed_width) &
            (df["Density"] == fixed_density) &
            (df["Cores"] == cores)
            ].sort_values("Depth")
        if subset.empty:
            continue

        ax.plot(subset["Depth"], subset["Parallel maxrss_kb"], color=cmap[i], marker="o", linestyle="-",
                label=f"{cores} Cores")

    ax.plot(subset["Depth"], subset["Qiskit maxrss_kb"], color="hotpink", marker="v", linestyle="--",
                label=f"Qiskit")

    ax.set_xlabel("Depth")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Varying Depth (Width={fixed_width})")
    ax.legend(fontsize="small", ncol=2)
    ax.grid(True)

    # plot 2: vary width
    ax = axs[1,0]
    for i, cores in enumerate(cores_list):
        subset = df[
            (df["Depth"] == fixed_depth) &
            (df["Density"] == fixed_density) &
            (df["Cores"] == cores)
            ].sort_values("Width")
        if subset.empty:
            continue

        ax.plot(subset["Width"], subset["Parallel maxrss_kb"], color=cmap[i], marker="o", linestyle="-",
                label=f"{cores} Cores")

    ax.plot(subset["Width"], subset["Qiskit maxrss_kb"], color="hotpink", marker="v", linestyle="--",
                label=f"Qiskit")

    ax.set_xlabel("Width")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Varying Width (Depth={fixed_depth})")
    ax.legend(fontsize="small", ncol=2)
    ax.grid(True)

    # plot 3: vary cores and multiple widths
    ax = axs[0,1]

    for i, width in enumerate([20, 100, 200]):
        subset = df[
            (df["Depth"] == fixed_depth) &
            (df["Density"] == fixed_density) &
            (df["Width"] == width)
            ].sort_values("Cores")
        if subset.empty:
            continue

        ax.plot(subset["Cores"], subset["Parallel maxrss_kb"], marker="o", linestyle="-", color=cmap[i],
                label=f"Parallel {width} qubits")
        ax.plot(subset["Cores"], subset["Qiskit maxrss_kb"], marker="v", linestyle="--", color=cmap[i],
                label=f"Qiskit {width} qubits")

    ax.set_xlabel("Cores")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Varying Cores (Depth={fixed_depth})")
    ax.legend()
    ax.grid(True)

    # plot 4: vary cores and multiple depths lines
    ax = axs[1,1]

    for i, depth in enumerate([20000, 60000, 100000]):
        subset = df[
            (df["Depth"] == depth) &
            (df["Density"] == fixed_density) &
            (df["Width"] == fixed_width)
            ].sort_values("Cores")
        if subset.empty:
            continue

        ax.plot(subset["Cores"], subset["Parallel maxrss_kb"], marker="o", linestyle="-", color=cmap[i],
                label=f"Parallel {depth} gates")
        ax.plot(subset["Cores"], subset["Qiskit maxrss_kb"], marker="v", linestyle="--", color=cmap[i],
                label=f"Qiskit {depth} gates")

    ax.set_xlabel("Cores")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Varying Cores (Width={fixed_width})")
    ax.legend()
    ax.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    if SAVE:
        plt.savefig(f"{PLOT_DIR}/memory_analysis.pdf")
    plt.show()

