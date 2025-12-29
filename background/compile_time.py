import qiskit.circuit.random
import os
import re
import time
import matplotlib.pyplot as plt
from qiskit import transpile
import qiskit.qasm3

# Parameters
num_qubits = 50
max_depth = 100000
depth_step = 2000
max_qubits = 2000
qubit_step = 50
fixed_depth = 500


if __name__ == '__main__':

    pattern = re.compile(r"random_circuit_([0-9.]+)_20q_1000g.qasm")
    transpile(qiskit.circuit.random.random_circuit(1, 50))

    p_values = []
    times = []

    # Loop over files in current directory
    for fname in os.listdir("random_bench_qasm_density_paper"):
        if fname.endswith(".qasm") and fname.startswith("random_circuit"):
            match = pattern.match(fname)
            if match:
                p_val = float(match.group(1))
                if 0.1 <= p_val <= 1.0:
                    print(f"Processing {fname} (p={p_val})")
                    qc = qiskit.qasm3.load(os.path.join("random_bench_qasm_density_paper",fname))

                    start = time.time()
                    transpile(qc, optimization_level=1)
                    end = time.time()

                    p_values.append(p_val)
                    times.append(end - start)

    p_values, times = zip(*sorted(zip(p_values, times)))

    # Depth scaling experiment
    depths = []
    times_depth = []

    for depth in range(depth_step, max_depth + 1, depth_step):
        print(f"Depth: {depth}")
        qc = qiskit.circuit.random.random_circuit(num_qubits, depth)
        start = time.time()
        transpile(qc, optimization_level=1)
        end = time.time()
        depths.append(depth)
        times_depth.append(end - start)

    # Width scaling experiment
    widths = []
    times_width = []

    for qubits in range(qubit_step, max_qubits + 1, qubit_step):
        print(f"Width: {qubits}")
        qc = qiskit.circuit.random.random_circuit(qubits, fixed_depth)
        start = time.time()
        transpile(qc, optimization_level=1)
        end = time.time()
        widths.append(qubits)
        times_width.append(end - start)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6, 15))

    # Depth scaling plot (left)
    ax1.plot(depths, times_depth, marker='o', color='blue')
    ax1.set_xlabel("Circuit Depth (gates)")
    ax1.set_xlim(0)
    ax1.set_ylim(0)
    ax1.set_ylabel("Compilation Time (s)")
    ax1.set_title(f"Depth Scaling ({num_qubits} qubits)")
    ax1.grid(True)

    # Width scaling plot (middle)
    ax2.plot(widths, times_width, marker='s', color='orange')
    ax2.set_xlabel("Circuit Width (qubits)")
    ax2.set_xlim(0)
    ax2.set_ylim(0)
    ax2.set_ylabel("Compilation Time (s)")
    ax2.set_title(f"Width Scaling ({fixed_depth} gates deep)")
    ax2.grid(True)

    # Density scaling plot (right)
    ax3.plot(p_values, times, marker='o', color='green')
    ax3.set_xlabel("Gate Density")
    ax3.set_xlim(0.2)
    ax3.set_ylabel("Compilation Time (s)")
    ax3.set_title("Density Scaling (20 qubits, 1000 gates deep)")
    ax3.grid(True)

    plt.tight_layout()
    plt.savefig("plots/all_comp_time_scaling_subplots.pdf")
    plt.show()

