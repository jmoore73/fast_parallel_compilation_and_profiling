import argparse
import os
import time
from pathlib import Path

import networkx as nx
import qiskit.qasm3
from qiskit import transpile, QuantumCircuit, QuantumRegister
from qiskit.qasm3 import QASM3ImporterError
from qiskit.transpiler import CouplingMap

import math

ROUTING = "sabre"
LAYOUT = "trivial"
OPT_LEVEL = 0

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--debug', type=str, default="False")
    parser.add_argument('--qasm_dir', type=str, default="qasm_output")
    parser.add_argument('--qasm_file', type=str, default=None)
    parser.add_argument('--num_cores', type=int, default=1)
    parser.add_argument('--proc', type=str, default="[2xm]")

    args = parser.parse_args()
    DEBUG = args.debug
    QASM_DIR = args.qasm_dir
    CIRCUIT_NAME = args.qasm_file
    NUM_CORES = args.num_cores
    SHAPE = args.proc

    if CIRCUIT_NAME is None:
        print("No circuit name!")
        exit(1)

    if DEBUG == "True":
        DEBUG = True
    else:
        DEBUG = False

    return (DEBUG, QASM_DIR, CIRCUIT_NAME, NUM_CORES, SHAPE)


def initialise_square_lattice(num_qubits):
    map = CouplingMap()
    for q in range(num_qubits):
        map.add_physical_qubit(q)
    m = int(math.sqrt(num_qubits))
    map = map.from_grid(m, m, bidirectional=True)
    initial_layout = []
    for q in range(num_qubits):
        initial_layout.append(q)
    return initial_layout, map


def initialise_grid_lattice(test_circuit):
    num_qubits = test_circuit.num_qubits
    if ((num_qubits % 2) != 0): num_qubits = num_qubits + 1
    map = CouplingMap()
    for q in range(num_qubits):
        map.add_physical_qubit(q)
    map = map.from_grid(2, int(num_qubits / 2), bidirectional=True)
    initial_layout = []
    for q in range(num_qubits):
        initial_layout.append(q)
    return initial_layout, map


def initialise_line_lattice(num_qubits):
    map = CouplingMap()
    for q in range(num_qubits):
        map.add_physical_qubit(q)
    map = map.from_line(num_qubits, bidirectional=True)
    initial_layout = []
    for q in range(num_qubits):
        initial_layout.append(q)
    return initial_layout, map


def transpile_and_insert_permute(subcircuit, coupling_map, qubit_list, qregs, barriers, debug, ROUTING, LAYOUT,
                                 OPT_LEVEL):
    transpile_start_time = time.time_ns()
    if debug:
        print(ROUTING, LAYOUT, OPT_LEVEL)
    transpiled_subcircuit = transpile(circuits=subcircuit,
                                      routing_method=ROUTING,
                                      coupling_map=coupling_map,
                                      initial_layout=None,
                                      layout_method=LAYOUT,
                                      optimization_level=OPT_LEVEL)
    transpile_end_time = time.time_ns()
    if "_final" not in subcircuit.name:
        if debug:
            print("Appending permutation circuit to subcircuit", subcircuit.name)
        transpiled_subcircuit = insert_permutation_circuit(coupling_map, qubit_list, qregs, transpiled_subcircuit, barriers)
        if debug:
            print("Appended permutation circuit to subcircuit", subcircuit.name)
    perm_circuit_end_time = time.time_ns()

    return transpiled_subcircuit, transpile_start_time, transpile_end_time, perm_circuit_end_time


def find_missing_number(short_list, full_list):
    n = len(full_list) - 1  # Since short_list is missing 1 element
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(short_list)
    return expected_sum - actual_sum


def insert_permutation_circuit(coupling_map, qubit_list, qregs, transpiled_subcircuit, barriers) -> QuantumCircuit:
    initial_layout = list(range(len(coupling_map.physical_qubits)))
    final_layout = find_final_layout(transpiled_subcircuit, len(qubit_list))
    if len(final_layout) != len(initial_layout):
        missing = find_missing_number(final_layout, initial_layout)
        final_layout.append(missing)
    swaps = swap_algorithm(final_layout, initial_layout, layout_to_graph(initial_layout, coupling_map))
    permutation_circuit = QuantumCircuit()
    for n, qreg in enumerate(qregs):
        permutation_circuit.add_register(qreg)
    permutation_circuit.name = "perm"
    for i, j in swaps:
        qubit1 = qubit_list[i]
        qubit2 = qubit_list[j]
        permutation_circuit.swap(qubit1, qubit2)
    if barriers:
        transpiled_subcircuit.barrier()
        transpiled_subcircuit &= permutation_circuit
        transpiled_subcircuit.barrier()
        return transpiled_subcircuit
    else:
        return transpiled_subcircuit.compose(permutation_circuit)


def layout_to_graph(layout, coupling_map):
    g = nx.Graph()
    relationships = coupling_map.get_edges()
    for edge in relationships:
        g.add_edge(layout[edge[0]], layout[edge[1]])
    return g


def swap_algorithm(permutation, target, relationship_graph) -> list:
    swap_list, sorted_layout = [], []
    for n in range(len(target)):
        sorted_layout.append(1)
    dists, paths = get_dists(permutation, target, relationship_graph)
    while dists != sorted_layout:
        index = dists.index(min(i for i in dists if i > 1))
        path = paths[index]
        counter = 0
        while counter < (len(path) - 1):
            i = path[counter]
            j = path[counter + 1]
            permutation[i], permutation[j] = permutation[j], permutation[i]
            swap_list.append((i, j))
            counter = counter + 1
        dists, paths = get_dists(permutation, target, relationship_graph)
    return swap_list


def find_final_layout(transpiled_subcircuit, num_qubits):
    layout = []
    p2v_layout = transpiled_subcircuit.layout.final_layout._p2v
    for q in range(num_qubits):
        layout.append(p2v_layout.get(q)._index)
    return layout


def get_dists(permutation, target, relationship_graph):
    dists, paths = [], []
    for qubit in target:
        pos = permutation.index(qubit)
        dist = nx.astar_path(relationship_graph, qubit, pos)
        dists.append(len(dist))
        paths.append(dist)
    return dists, paths


if __name__ == "__main__":
    start_time = time.time_ns()
    DEBUG, QASM_DIR, CIRCUIT_NAME, NUM_CORES, SHAPE = parse_arguments()
    qasm_dir = Path(QASM_DIR)
    subcirc_num = CIRCUIT_NAME.split("_")[-1]

    if DEBUG:
        barriers = True
    else:
        barriers = False

    path = os.path.join(qasm_dir, CIRCUIT_NAME + ".qasm")
    if not os.path.isfile(path):
        if DEBUG:
            print(f"Qasm file {path} does not exist")
        exit(1)

    # read full quantum test circuit from file
    try:
        quantum_subcircuit = qiskit.qasm3.load(path)
    except QASM3ImporterError as e:
        if DEBUG:
            print(f"Failed to load the QASM 3 file: {e}")
        try:
            quantum_subcircuit = QuantumCircuit.from_qasm_file(path)
        except:
            print(f"Failed to load the QASM 2 file: {path}")
            exit(1)
        if DEBUG:
            print(f"Loaded QASM 2 file: {path}")

    if quantum_subcircuit.num_qubits % 2 != 0:  # If odd, add an ancilla qubit
        ancilla = QuantumRegister(1, 'ancilla')
        quantum_subcircuit.add_register(ancilla)

    # set up the lattice/processor layout for the given test circuit (depends on num qubits)
    if SHAPE == "square":
        initial_layout, coupling_map = initialise_square_lattice(quantum_subcircuit.num_qubits)
    if SHAPE == "line":
        initial_layout, coupling_map = initialise_line_lattice(quantum_subcircuit.num_qubits)
    elif SHAPE == "[2xm]":
        initial_layout, coupling_map = initialise_grid_lattice(quantum_subcircuit)

    setup_time = time.time_ns()

    if int(subcirc_num) == NUM_CORES:
        quantum_subcircuit.name = quantum_subcircuit.name + "_final"

    transpiled_subcircuit, transpile_start_time, transpile_end_time, perm_circuit_end_time = transpile_and_insert_permute(
        quantum_subcircuit, coupling_map, quantum_subcircuit.qubits, quantum_subcircuit.qregs,
        barriers=barriers, debug=DEBUG, ROUTING=ROUTING, LAYOUT=LAYOUT, OPT_LEVEL=OPT_LEVEL
    )

    qasm = qiskit.qasm3.dumps(transpiled_subcircuit)
    qasm_file = f"{CIRCUIT_NAME}_transpiled.qasm"
    path = os.path.join(qasm_dir, qasm_file)
    if not os.path.exists(qasm_dir):
        os.makedirs(qasm_dir)
    with open(path, "w") as qasm_file:
        qasm_file.write(qasm)

    if DEBUG:
        print(f"Saved {transpiled_subcircuit.name} to {path}", flush=True)

    end_time = time.time_ns()

    print(f"Core {subcirc_num} Setup Start Time, {start_time}")
    print(f"Core {subcirc_num} Setup End Time, {setup_time}")
    print(f"Core {subcirc_num} Transpile Start Time, {transpile_start_time}")
    print(f"Core {subcirc_num} Transpile End Time, {transpile_end_time}")
    print(f"Core {subcirc_num} Permutation Start Time, {transpile_end_time}")
    print(f"Core {subcirc_num} Permutation End Time, {perm_circuit_end_time}")
    print(f"Core {subcirc_num} Parallel End Time, {end_time}")

    if DEBUG:
        print(f"Finished on core {subcirc_num} in {end_time - start_time}ns")

    exit(0)
