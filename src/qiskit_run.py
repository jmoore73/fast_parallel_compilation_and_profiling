import argparse
import os
from pathlib import Path

import qiskit.qasm3
from qiskit import transpile, QuantumCircuit
from qiskit.qasm3 import QASM3ImporterError
from qiskit.transpiler.passes import RemoveBarriers

from parallel_create_transpile_permute import initialise_square_lattice, initialise_grid_lattice, ROUTING, LAYOUT, OPT_LEVEL


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--debug', type=str, default="False")
    parser.add_argument('--qasm_dir', type=str, default="qasm_output")
    parser.add_argument('--circ_name', type=str, default=None)
    parser.add_argument('--proc', type=str, default="[2xm]")
    parser.add_argument('--num_cores', type=int, default=1)

    args = parser.parse_args()
    DEBUG = args.debug
    QASM_DIR = args.qasm_dir
    CIRCUIT_NAME = args.circ_name
    SHAPE = args.proc
    NUM_CORES = args.num_cores

    if CIRCUIT_NAME is None:
        print("No circuit name!")
        exit(1)

    if DEBUG == "True":
        DEBUG = True
    else:
        DEBUG = False

    return (DEBUG, QASM_DIR, CIRCUIT_NAME, NUM_CORES, SHAPE)


if __name__ == "__main__":
    DEBUG, QASM_DIR, CIRCUIT_NAME, NUM_CORES, SHAPE = parse_arguments()
    qasm_dir = Path(QASM_DIR)

    path = os.path.join(qasm_dir, CIRCUIT_NAME + ".qasm")
    if not os.path.isfile(path):
        print(f"Qasm file {path} does not exist")
        exit(1)

    # read full quantum test circuit from file
    try:
        test_circuit = qiskit.qasm3.load(path)
    except QASM3ImporterError as e:
        if DEBUG:
            print(f"Failed to load the QASM 3 file: {e}")
        test_circuit = QuantumCircuit.from_qasm_file(path)

    test_circuit.remove_final_measurements()
    test_circuit = RemoveBarriers()(test_circuit)

    # set up the lattice/processor layout for the given test circuit (depends on num qubits)
    if SHAPE == "square" or SHAPE == "Square":
        initial_layout, coupling_map = initialise_square_lattice(test_circuit.num_qubits)
    elif SHAPE == "[2xm]":
        initial_layout, coupling_map = initialise_grid_lattice(test_circuit)

    transpiled_circuit = transpile(circuits=test_circuit,
                                   routing_method=ROUTING,
                                   coupling_map=coupling_map,
                                   initial_layout=None,
                                   layout_method=LAYOUT,
                                   optimization_level=OPT_LEVEL)

    if DEBUG:
        print(f"Transpiled {CIRCUIT_NAME} from {path}")

    qasm = qiskit.qasm3.dumps(transpiled_circuit)
    qasm_file = f"{CIRCUIT_NAME}_qiskit.qasm"
    if "cores" not in str(qasm_dir):
        core_part = f"{NUM_CORES}cores"
        qasm_dir = qasm_dir.joinpath(core_part)
    path = os.path.join(qasm_dir, qasm_file)
    if not os.path.exists(qasm_dir):
        os.makedirs(qasm_dir)
    with open(path, "w") as qasm_file:
        qasm_file.write(qasm)

    exit(0)
