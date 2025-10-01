import re
import argparse

from qiskit.transpiler import CouplingMap

ROUTING = "sabre"
LAYOUT = "trivial"

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--sc_base', type=str, default=None)
    parser.add_argument('--t_circ', type=str, default=None)
    parser.add_argument('--cores', type=int, default=1)
    args = parser.parse_args()
    SC_BASE = args.sc_base
    T_CIRCUIT = args.t_circ
    CORES = args.cores

    header = []
    body = []
    header_captured = False
    gate_counter = 1

    for i in range(1, CORES + 1):
        input_file = f'{SC_BASE}{i}_transpiled.qasm'
        rename_map = {}

        with open(input_file, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                # Capture header only once
                if stripped_line.startswith(('OPENQASM', 'include', 'qubit', 'bit', 'qreg', 'creg')):
                    if not header_captured:
                        header.append(line)
                else:
                    # Rename gate definitions (e.g., 'gate bridge ...')
                    gate_def_match = re.match(r'gate (\w+)\b', stripped_line)
                    if gate_def_match:
                        gate_name = gate_def_match.group(1)
                        new_gate_name = f"{gate_name}_{gate_counter}"
                        rename_map[gate_name] = new_gate_name
                        line = line.replace(f"gate {gate_name}", f"gate {new_gate_name}")
                    else:
                        # Replace gate usage (only whole-word matches)
                        for old_name, new_name in rename_map.items():
                            line = re.sub(rf'\b{old_name}\b', new_name, line)

                    body.append(line)

        header_captured = True
        gate_counter += 1

    # Write merged file
    with open(T_CIRCUIT, 'w') as out:
        out.writelines(header)
        out.writelines(body)
