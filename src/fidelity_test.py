import argparse
import qiskit

from qiskit import QuantumCircuit
from qiskit.qasm3 import QASM3ImporterError
from qiskit.quantum_info import Statevector, state_fidelity


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--base_name', type=str, default=None)
    args = parser.parse_args()
    BASE_NAME = args.base_name

    bfpt_file = BASE_NAME + "_transpiled.qasm"
    qiskit_file = BASE_NAME + "_qiskit.qasm"

    ideal_parallel = Statevector.from_instruction(load_qasm(bfpt_file))
    ideal_serial = Statevector.from_instruction(load_qasm(qiskit_file))
    fidelity = state_fidelity(ideal_parallel, ideal_serial)
    print(f"{BASE_NAME} fidelity:", fidelity)

    # statevector permutation problem! ffs look at chatgpt to help babes

    fidelity = state_fidelity(ideal_parallel, ideal_serial)
    print(f"{BASE_NAME} fidelity:", fidelity)

