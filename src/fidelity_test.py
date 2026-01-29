import csv
import qiskit
from qiskit.quantum_info import hellinger_fidelity
from qiskit_aer import AerSimulator

from fidelity_helper import load_qasm, remove_cregs, get_final_permutation_from_swaps, \
    add_measurements_logical_order, plot_results
from src.fidelity_helper import pad_counts

SHOTS = 1024
DEBUG = False
RERUN = False

data=[
    ("mlp4_245", 2), ("mlp4_245", 4), ("mlp4_245", 6), ("mlp4_245", 8),
    ("urf2_277", 2), ("urf2_277", 4), ("urf2_277", 6), ("urf2_277", 8),
    ("hwb8_113", 2), ("hwb8_113", 4), ("hwb8_113", 6), ("hwb8_113", 8),
    ("shor_15_4_nativegates_ibm_qiskit_opt0_18", 2), ("shor_15_4_nativegates_ibm_qiskit_opt0_18", 4),
    ("shor_15_4_nativegates_ibm_qiskit_opt0_18", 6), ("shor_15_4_nativegates_ibm_qiskit_opt0_18", 8),
    ("shor_9_4_nativegates_ibm_qiskit_opt0_18", 2), ("shor_9_4_nativegates_ibm_qiskit_opt0_18", 4),
    ("shor_9_4_nativegates_ibm_qiskit_opt0_18", 6), ("shor_9_4_nativegates_ibm_qiskit_opt0_18", 8),
    ("dist_223", 2), ("dist_223", 4), ("dist_223", 6), ("dist_223", 8),
    ("grover-noancilla_nativegates_ibm_qiskit_opt0_9", 2), ("grover-noancilla_nativegates_ibm_qiskit_opt0_9", 4),
    ("grover-noancilla_nativegates_ibm_qiskit_opt0_9", 6), ("grover-noancilla_nativegates_ibm_qiskit_opt0_9", 8),
    ("alu-v2_32", 2), ("alu-v2_32", 4), ("alu-v2_32", 6), ("alu-v2_32", 8),
    ("mod5adder_127", 2), ("mod5adder_127", 4), ("mod5adder_127", 6), ("mod5adder_127", 8),
    ("qft_16", 2), ("qft_16", 4), ("qft_16", 6), ("qft_16", 8),
    ("grover-noancilla_indep_qiskit_4", 2), ("grover-noancilla_indep_qiskit_4", 4), ("grover-noancilla_indep_qiskit_4", 6),
    ("4gt12-v0_87", 2), ("4gt12-v0_87", 4), ("4gt12-v0_87", 6), ("4gt12-v0_87", 8),
]


if __name__ == "__main__":

    if RERUN:
        with open("fidelity_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Cores", "Depth", "Width", "Parallel Fidelity", "Qiskit Fidelity"])  # header

        for BASE_NAME, cores in data:
            qc_uncompiled = remove_cregs(load_qasm(f"../qasm/{BASE_NAME}.qasm"))
            qc_compiled = load_qasm(f"../qasm/{cores}cores/{BASE_NAME}_transpiled.qasm")
            qc_qiskit = load_qasm(f"../qasm/{cores}cores/{BASE_NAME}_qiskit.qasm")

            final_perm = get_final_permutation_from_swaps(qc_compiled)

            # Add measurements
            qc_uncompiled_meas = qc_uncompiled.measure_all(inplace=False) # trivial order due to no swaps
            qc_compiled_meas = add_measurements_logical_order(qc_compiled, final_perm)

            # Get counts from simulator
            backend = AerSimulator()
            counts_uncompiled = backend.run(qc_uncompiled_meas, shots=SHOTS).result().get_counts()
            counts_compiled = backend.run(qc_compiled_meas, shots=SHOTS).result().get_counts()

            if qc_uncompiled.num_qubits % 2 == 1:
                counts_uncompiled = pad_counts(counts_uncompiled, (qc_uncompiled.num_qubits+1) )

            if DEBUG:
                print(counts_uncompiled)
                print(counts_compiled)

            fidelity = hellinger_fidelity(counts_uncompiled, counts_compiled)
            print(f"{cores} {BASE_NAME} Parallel Fidelity: {fidelity:.6f}")
            if fidelity < 0.5 and not DEBUG:
                print(counts_uncompiled)
                print(counts_compiled)

            try:
                final_perm = get_final_permutation_from_swaps(qc_qiskit)
                qc_qiskit_meas = add_measurements_logical_order(qc_qiskit, final_perm)
                counts_qiskit = backend.run(qc_qiskit_meas, shots=SHOTS).result().get_counts()
                if qc_qiskit_meas.num_qubits % 2 == 1:
                    counts_qiskit = pad_counts(counts_qiskit, (qc_qiskit_meas.num_qubits + 1))
                q_fidelity = hellinger_fidelity(counts_uncompiled, counts_qiskit)
                if DEBUG:
                    print(counts_qiskit)
                print(f"{cores} {BASE_NAME} Qiskit Fidelity: {q_fidelity:.6f}")
                if q_fidelity < 0.5 and not DEBUG:
                    print(counts_uncompiled)
                    print(counts_qiskit)
            except qiskit.circuit.exceptions.CircuitError as e:
                print(f"{cores} {BASE_NAME} Qiskit Fidelity: err")
                continue

            with open("fidelity_results.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([BASE_NAME, cores, qc_uncompiled.depth(), qc_uncompiled.num_qubits, fidelity, q_fidelity])

    plot_results("fidelity_results.csv")
