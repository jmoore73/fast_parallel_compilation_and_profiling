import pandas as pd
import qiskit
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.qasm3 import QASM3ImporterError


def load_qasm(file):
    try:
        qc = qiskit.qasm3.load(file)
    except QASM3ImporterError as e:
        try:
            qc = QuantumCircuit.from_qasm_file(file)
        except QASM3ImporterError as e:
            print(e)
            exit(1)
    return qc


def get_final_permutation_from_swaps(circuit):
    perm = list(range(circuit.num_qubits))  # identity
    try:
        init_layout = list(circuit.layout.initial_layout._p2v.values())
        qasm=True
    except AttributeError as e:
        init_layout = list(range(circuit.num_qubits))
        qasm=False

    for instr, qargs, _ in circuit.data:
        if instr.name == "swap":
            if qasm:
                i = init_layout.index(qargs[0])
                j = init_layout.index(qargs[1])
            else:
                i = init_layout.index(qargs[0]._index)
                j = init_layout.index(qargs[1]._index)
            init_layout[i], init_layout[j] = init_layout[j], init_layout[i]
            perm[i], perm[j] = perm[j], perm[i]
    return perm


def add_measurements_logical_order(qc, final_perm):
    n = len(final_perm)
    cr = ClassicalRegister(n)
    qc.add_register(cr)
    for logical_bit, phys_qubit in enumerate(final_perm):
        qc.measure(phys_qubit, logical_bit)
    return qc


def remove_cregs(qc):
    qc_no_classical = QuantumCircuit()
    for qreg in qc.qregs:
        qc_no_classical.add_register(qreg)
    for instr, qargs, cargs in qc.data:
        if instr.name != "measure":
            qc_no_classical.append(instr, qargs, [])
    return qc_no_classical


def pad_counts(counts, width):
    return {
        bitstring.zfill(width): shots
        for bitstring, shots in counts.items()
    }


def plot_results(filename):
    df = pd.read_csv("fidelity_results.csv")
    df = df.sort_values(["Name", "Cores"])
    names = df["Name"].unique()
    cores = sorted(df["Cores"].unique())

    # Color-blind friendly palette https://siegal.bio.nyu.edu/color-palette/
    okabe_ito = [
        # "#000000",  # black
        "#E69F00",  # orange
        "#F0E442",  # yellow
        "#009E73",  # bluish green
        # "#0072B2",  # blue
        # "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
        "#56B4E9",  # sky blue

    ]

    core_colors = {c: okabe_ito[i % len(okabe_ito)] for i, c in enumerate(cores)}

    bar_width = 0.35
    group_gap = 1.0
    x_positions = []
    x_labels = []
    x = 0

    fig, ax = plt.subplots(figsize=(10, 5))

    for name in names:
        group_start = x
        subset = df[df["Name"] == name]

        for _, row in subset.iterrows():
            # Parallel Fidelity (solid bars)
            ax.bar(
                x,
                row["Parallel Fidelity"],
                bar_width,
                color=core_colors[row["Cores"]]
            )

            # Qiskit Fidelity (lined bars)
            ax.bar(
                x + bar_width,
                row["Qiskit Fidelity"],
                bar_width,
                color=core_colors[row["Cores"]],
                hatch="///",
                edgecolor="black"
            )

            x += bar_width * 2

        # Label once per group
        group_end = x - bar_width
        x_positions.append((group_start + group_end) / 2)
        x_labels.append(name)
        x += group_gap

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel("Fidelity")
    ax.set_ylim(0.9, 1.001)
    ax.grid(True, alpha=0.5)
    ax.set_title("Parallel vs Qiskit Fidelity")

    core_legend = [Patch(facecolor=core_colors[c], label=f"{c} cores") for c in cores]
    fidelity_legend = [Patch(facecolor="gray", label="Parallel Fidelity"),
                       Patch(facecolor="gray", hatch="///", edgecolor="black", label="Qiskit Fidelity")]

    legend1 = ax.legend(handles=core_legend, title="Cores", loc="lower left")
    legend2 = ax.legend(handles=fidelity_legend, title="Fidelity Type", loc="upper right")
    ax.add_artist(legend1)
    plt.tight_layout()
    plt.savefig("../results/icrc_r_pdf/fidelity_results.pdf")
    plt.show()



