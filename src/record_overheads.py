import argparse
import qiskit.qasm3
from qiskit import QuantumCircuit
from qiskit.qasm3 import QASM3ImporterError

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--base_name', type=str, default=None)
    args = parser.parse_args()
    BASE_NAME = args.base_name

    bfpt_file = BASE_NAME + "_transpiled.qasm"
    qiskit_file = BASE_NAME + "_qiskit.qasm"

    for file, name in zip([bfpt_file, qiskit_file], ["Parallel", "Serial"]):
        try:
            qc = qiskit.qasm3.load(file)
        except QASM3ImporterError as e:
            try:
                qc = QuantumCircuit.from_qasm_file(file)
            except QASM3ImporterError as e:
                print(e)
                exit(1)

        post_transpile_depth = qc.depth()
        gate_counts = qc.count_ops()
        num_swaps = gate_counts.get("swap")

        total_gates = 0
        for gate_count in gate_counts:
            total_gates += gate_counts[gate_count]

        print(f"{name} Swaps, {num_swaps}")
        print(f"{name} Post Transpile Depth, {post_transpile_depth}")
        print(f"{name} Post Transpile Gate Count, {total_gates}")
