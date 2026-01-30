import argparse
import os
from pathlib import Path

import pytket
from pytket.passes import RoutingPass
from pytket.placement import place_with_map
from pytket.qasm import circuit_from_qasm, circuit_to_qasm

from parallel_create_transpile_permute import initialise_square_lattice, initialise_grid_lattice


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

    if "con2random_circuit" not in CIRCUIT_NAME:
        qasm_dir = os.path.join(qasm_dir, "mod")

    if DEBUG:
        print(CIRCUIT_NAME)
        print(qasm_dir)

    path = os.path.join(qasm_dir, CIRCUIT_NAME + ".qasm")
    if not os.path.isfile(path):
        print(f"Qasm file {path} does not exist")
        exit(1)

    test_circuit = circuit_from_qasm(path, maxwidth=201)

    if test_circuit.n_qubits % 2 != 0:  # If odd, add an ancilla qubit
        ancilla_index = test_circuit.n_qubits
        ancilla_qubit = pytket.Qubit(ancilla_index)
        test_circuit.add_qubit(ancilla_qubit)

    # set up the lattice/processor layout for the given test circuit (depends on num qubits)
    if SHAPE == "square":
        initial_layout, coupling_map = initialise_square_lattice(test_circuit.num_qubits)
    elif SHAPE == "[2xm]":
        initial_layout, coupling_map, coupling_graph = initialise_grid_lattice(test_circuit)
    else:
        print("Unknown shape")
        exit(1)

    place_with_map(test_circuit, initial_layout)
    RoutingPass(coupling_map).apply(test_circuit)

    if DEBUG:
        print(f"Transpiled {CIRCUIT_NAME} from {path}")

    qasm_file = f"{CIRCUIT_NAME}_qiskit.qasm"
    if "cores" not in str(qasm_dir):
        core_part = f"{NUM_CORES}cores"
        qasm_dir = qasm_dir.joinpath(core_part)
    path = os.path.join(qasm_dir, qasm_file)
    if DEBUG:
        print("Saved circuit to ", os.path.join(qasm_dir, qasm_file))
    if not os.path.exists(qasm_dir):
        os.makedirs(qasm_dir)
    circuit_to_qasm(test_circuit, path, maxwidth=201)

    exit(0)
