import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

plot_folder = "dac_pdf"

variables = ["Cores", "Width", "Depth"]
components = ["Speedup", "Gate Overhead", "Depth Overhead", "SWAP Overhead"]

# Colour-blind friendly palette
colour_palette = {
    "sabre": "#FF9500",  # bright orange
    "basic": "#0077BB",  # vivid blue (stronger than #0072B2)
    "pytket": "#EE3377"  # bright pink / magenta
}


marker_style = {
    "sabre": "o",
    "basic": "s",
    "pytket": "^"
}

line_styles = {
    "sabre": "-",
    "basic": "--",
    "pytket": ":"
}

labels = {
    "sabre": "SabreSwap",
    "basic": "BasicSwap",
    "pytket": "PyTKET"
}


if __name__ == '__main__':

    os.makedirs(plot_folder, exist_ok=True)

    for data in ["benchmark", "random"]:
        source_d = "10k_100k" if data == "benchmark" else "full"
        datasets = ["sabre", "basic", "pytket"]
        dfs = {}

        # Load CSVs
        for dataset in datasets:
            source = f"all_{data}_{dataset}_results_{source_d}.csv"
            print(f"Loading {source} ...")
            df = pd.read_csv(source)
            if data == "random":
                df = df[df["Density"] == 1.0]
            dfs[dataset] = df

        # Plot each variable
        for variable in variables:
            fig, axes = plt.subplots(2, 2, figsize=(6, 4)) #figsize=(6, 4))
            axes = axes.flatten()

            for i, component in enumerate(components):
                ax = axes[i]

                for dataset in datasets:
                    df = dfs[dataset]
                    if variable in df.columns and component in df.columns:
                        # Scatter plot
                        if variable == "Depth":
                            jitter_strength = 1000  # adjust for spacing; depends on your x-axis scale
                        else:
                            jitter_strength = 5
                        ax.scatter(
                            df[variable],
                            # df[variable] + np.random.uniform(-jitter_strength, jitter_strength, size=len(df)),
                            df[component],
                            color=colour_palette[dataset],
                            marker=marker_style[dataset],
                            alpha=0.7,
                            s=20,
                            label=f"{dataset.capitalize()} points" if i == 0 else "_nolegend_"
                        )

                        # Average line
                        avg_df = (
                            df.groupby(variable, as_index=False)[component]
                            .mean()
                            .sort_values(by=variable)
                        )
                        ax.plot(
                            avg_df[variable],
                            avg_df[component],
                            color='k', #colour_palette[dataset],
                            linestyle=line_styles[dataset],
                            linewidth=2,
                            alpha=1.0,
                            label=f"{dataset.capitalize()} Average" if i == 0 else "_nolegend_"
                        )

                if variable == "Depth":
                    ax.set_xticks([25000, 50000, 75000, 100000])

                ax.set_title(component, fontsize=10)
                ax.set_xlabel(variable, fontsize=10)
                if "Overhead" in component:
                    component = component + " (%)"
                ax.set_ylabel(component, fontsize=10)
                ax.grid(True, linestyle="--", alpha=0.5)

            # Shared legend
            handles, labels = fig.axes[0].get_legend_handles_labels()
            fig.legend(
                handles, labels,
                loc="lower center",
                ncol=3,
                frameon=False,
                bbox_to_anchor=(0.5, -0.08)
            )

            # fig.suptitle(f"{data.capitalize()} Data — {variable}", fontsize=10, weight="bold")
            plt.tight_layout(rect=[0, 0, 1, 0.94])
            plt.savefig(f"{plot_folder}/{data}_{variable}_components.pdf", dpi=300, bbox_inches="tight")
            plt.show()
            plt.close()

    print("✅ All 2x2 plots updated with line styles, faded scatter points, and lower legend.")

