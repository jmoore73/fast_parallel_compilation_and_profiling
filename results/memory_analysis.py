import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

SAVE = True
PLOT_DIR = "icrc_r_pdf"
DATA_CSV = "memory_summary.csv"

fixed_density = 1.0
fixed_width = 100
fixed_depth = 60000


if __name__ == "__main__":

    df = pd.read_csv(DATA_CSV)
    df["Aggregate Concurrent Memory"] = df["Parallel maxrss_kb"]*df["Cores"]

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

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Memory Usage for Parallel Compilation Against Qiskit")

    # plot 1: vary cores and multiple widths
    ax = axs[0,0]
    width_handles = []

    for i, width in enumerate([20, 100, 160, 200]):
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

        # one legend entry per width (color only)
        width_handles.append(Line2D([0], [0], color=cmap[i], lw=2, label=f"{width} qubits"))

    ax.set_xlabel("Cores")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Max RSS for Fixed Depth {fixed_depth} Gates", fontsize=12)
    ax.legend(handles=width_handles, title="Width", loc="upper center")
    ax.grid(True)

    # plot 2: vary cores and multiple depths lines
    ax = axs[0,1]
    depth_handles = []

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
        depth_handles.append(Line2D([0], [0], color=cmap[i], lw=2, label=f"{depth} gates"))

    ax.set_xlabel("Cores")
    ax.set_ylabel("Max RSS (KB)")
    ax.set_title(f"Max RSS for Fixed Width {fixed_width} Qubits", fontsize=12)
    ax.legend(handles=depth_handles, title="Depth", loc="upper center")
    ax.grid(True)

    # plot 3: vary cores and multiple widths
    ax = axs[1, 0]
    width_handles = []

    for i, width in enumerate([20, 100, 160, 200]):
        subset = df[
            (df["Depth"] == fixed_depth) &
            (df["Density"] == fixed_density) &
            (df["Width"] == width)
            ].sort_values("Cores")
        if subset.empty:
            continue

        ax.plot(subset["Cores"], subset["Aggregate Concurrent Memory"], marker="o", linestyle="-", color=cmap[i],
                label=f"Parallel {width} qubits")
        ax.plot(subset["Cores"], subset["Qiskit maxrss_kb"], marker="v", linestyle="--", color=cmap[i],
                label=f"Qiskit {width} qubits")

        # one legend entry per width (color only)
        width_handles.append(Line2D([0], [0], color=cmap[i], lw=2, label=f"{width} qubits"))

    ax.set_xlabel("Cores")
    ax.set_ylabel("Aggregate Concurrent Memory (KB)")
    ax.set_title(f"Aggregate Concurrent Memory for Fixed Depth {fixed_depth} Gates", fontsize=10)
    ax.legend(handles=width_handles, title="Width", loc="upper center")
    ax.grid(True)

    # plot 4: vary cores and multiple depths lines
    ax = axs[1, 1]
    depth_handles = []

    for i, depth in enumerate([20000, 60000, 100000]):
        subset = df[
            (df["Depth"] == depth) &
            (df["Density"] == fixed_density) &
            (df["Width"] == fixed_width)
            ].sort_values("Cores")
        if subset.empty:
            continue

        ax.plot(subset["Cores"], subset["Aggregate Concurrent Memory"], marker="o", linestyle="-", color=cmap[i],
                label=f"Parallel {depth} gates")
        ax.plot(subset["Cores"], subset["Qiskit maxrss_kb"], marker="v", linestyle="--", color=cmap[i],
                label=f"Qiskit {depth} gates")
        depth_handles.append(Line2D([0], [0], color=cmap[i], lw=2, label=f"{depth} gates"))

    ax.set_xlabel("Cores")
    ax.set_ylabel("Aggregate Concurrent Memory (KB)")
    ax.set_title(f"Aggregate Concurrent Memory for Fixed Width {fixed_width} Qubits", fontsize=10)
    ax.legend(handles=depth_handles, title="Depth", loc="upper center")
    ax.grid(True)


    style_handles = [
        Line2D([0], [0], color="black", lw=2, linestyle="-", label="Parallel"),
        Line2D([0], [0], color="black", lw=2, linestyle="--", label="Qiskit"),
    ]

    fig.legend(
        handles=style_handles,
        loc="lower center",
        ncol=2,
        frameon=True,
    )

    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    if SAVE:
        plt.savefig(f"{PLOT_DIR}/memory_analysis.pdf")
    plt.show()

