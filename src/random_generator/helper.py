import argparse
import math
import random
from urllib.error import HTTPError

def boolean_string(s):
    if s not in {'False', 'True'}:
        raise ValueError('Not a valid boolean string')
    return s == 'True'


def parse_arguments():
    global GATE_SET, DRAW, COMBINE, \
        MIN_WIDTH, MAX_WIDTH, WIDTH_STEP, \
        MIN_DEPTH, MAX_DEPTH, DEPTH_STEP, \
        MIN_DENSITY, MAX_DENSITY, DENSITY_STEP
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--gate_set', type=str, default=["H", "S", "X", "T", "CX"])
    parser.add_argument('--combine', type=boolean_string, default=False)
    parser.add_argument('--draw', type=boolean_string, default=False)

    parser.add_argument('--min_density', type=float, default=0.5)
    parser.add_argument('--max_density', type=float, default=1.0)
    parser.add_argument('--density_step', type=float, default=0.1)

    parser.add_argument('--min_width', type=int, default=10)
    parser.add_argument('--max_width', type=int, default=16)
    parser.add_argument('--width_step', type=int, default=2)

    parser.add_argument('--min_depth', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=500)
    parser.add_argument('--depth_step', type=int, default=100)

    args = parser.parse_args()
    GATE_SET = args.gate_set
    MIN_DENSITY = args.min_density
    MAX_DENSITY = args.max_density
    DENSITY_STEP = args.density_step
    MIN_WIDTH = args.min_width
    MAX_WIDTH = args.max_width
    WIDTH_STEP = args.width_step
    MIN_DEPTH = args.min_depth
    MAX_DEPTH = args.max_depth
    DEPTH_STEP = args.depth_step
    COMBINE = args.combine
    DRAW = args.draw

    return (GATE_SET, DRAW, COMBINE,
            MIN_WIDTH, MAX_WIDTH, WIDTH_STEP,
            MIN_DEPTH, MAX_DEPTH, DEPTH_STEP,
            MIN_DENSITY, MAX_DENSITY, DENSITY_STEP)


def remove_ops_for_given_density(circuit, density, draw=False):
    if density == 1.0:
        return circuit
    if draw:
        draw_circuit(circuit, "../circuit_diagrams/" + circuit.name + "_before.png")

    max_ops = circuit.num_qubits * circuit.depth()
    ops_to_remove = max_ops - math.ceil(max_ops * density)

    if ops_to_remove > (max_ops - circuit.depth()):
        print("***** Cannot make circuit density that low and maintain depth *****")
        return None

    removal_gates, safe_qubit = validate_removal_numbers(circuit, ops_to_remove, max_ops)
    try:
        print("Validated gate removal numbers: ", removal_gates, " from ", len(circuit.data))
    except Exception as e:
        print(e)
        return None

    unsafe_qubits_circuit = remove_safe_qubit_from_circuit(circuit, safe_qubit)

    final_num_ops = len(circuit.data) - removal_gates[0] - removal_gates[1]
    ops_removed = 0
    print("Starting removal...")

    while removal_gates[1] > 0 or removal_gates[0] > 0:
        remove_loc = random.randint(0, len(unsafe_qubits_circuit)-1)
        instr = unsafe_qubits_circuit[remove_loc]
        gate_to_remove = None

        if safe_qubit not in instr.qubits:
            if len(instr.qubits) == 1 and removal_gates[0] > 0:
                gate_to_remove = instr
                removal_gates[0] -= 1
                ops_removed += 1
            elif len(instr.qubits) == 2 and removal_gates[1] > 0:
                gate_to_remove = instr
                removal_gates[1] -= 1
                ops_removed += 2
            if gate_to_remove is not None:
                circuit.data.remove(gate_to_remove)
                unsafe_qubits_circuit.remove(gate_to_remove)
        else:
            print("safe_qubit in instr.qubits")

    assert ops_removed == ops_to_remove
    assert len(circuit.data) == final_num_ops
    print("Gates removed!")

    if draw:
        draw_circuit(circuit, "../circuit_diagrams/" + circuit.name + "_after.png")
    return circuit


def remove_safe_qubit_from_circuit(circuit, safe_qubit):
    instructions = circuit.data.copy()
    updated_instructions = circuit.data.copy()
    for instr in instructions:
        if safe_qubit in instr.qubits:
            updated_instructions.remove(instr)
    return updated_instructions


def count_x_qubit_gates(circuit, qubit=None):
    try:
        counts = [0, 0]
        checksum = 0

        # Loop through all gates in circuit and update gate qubit counts
        for instr in circuit.data:
            if qubit is None or qubit in instr.qubits:
                num_qubits = len(instr.qubits)
                counts[num_qubits - 1] = counts[num_qubits - 1] + 1

        circ_gates = dict(circuit.count_ops())
        total = 0

        for g in circ_gates:
            total = total + circ_gates.get(g)

        if qubit is None:
            for c in counts:
                checksum = checksum + c
            if checksum != total:
                raise Exception("Incorrect gate counting")

    except IndexError as indexError:
        print(circuit.name, "- not basis gates -", indexError)
        return [math.nan, math.nan, math.nan]
    return counts


def validate_removal_numbers(circuit, ops_to_remove, max_ops):
    qubit_idx = random.randint(0, circuit.num_qubits - 1)
    safe_qubit = circuit.qubits[qubit_idx]  # to maintain the depth
    gate_counts = count_x_qubit_gates(circuit)
    safe_counts = count_x_qubit_gates(circuit, safe_qubit)
    qubits = list(range(circuit.num_qubits))

    # randomly choose a safe qubit until one is chosen that has gate
    # counts that enable the density wanted
    while max_ops - ops_to_remove < safe_counts[0] + 2*safe_counts[1]:
        print("WARNING - Impossible to reduce density with this safe qubit")
        qubits.remove(qubit_idx)
        qubit_idx = random.choice(qubits)
        safe_qubit = circuit.qubits[qubit_idx]
        safe_counts = count_x_qubit_gates(circuit, safe_qubit)

    removal_counts = [0, random.randint(0, min(gate_counts[1], int(ops_to_remove / 2)))]
    removal_counts[0] = ops_to_remove - 2 * removal_counts[1]

    if safe_counts[1] + removal_counts[1] > gate_counts[1]:
        extra_1q = -2 * (gate_counts[1] - safe_counts[1] - removal_counts[1])
        removal_counts[0] += extra_1q
        removal_counts[1] -= (extra_1q/2)

    if removal_counts[0] > gate_counts[0]:
        extra_2q = removal_counts[0] - gate_counts[0]
        if extra_2q % 2 != 0:
            extra_2q += 1
        removal_counts[1] += (extra_2q/2)
        removal_counts[0] -= extra_2q

    assert removal_counts <= gate_counts
    assert removal_counts + safe_counts <= gate_counts
    assert ((removal_counts[1] * 2) + removal_counts[0]) == ops_to_remove
    return removal_counts, safe_qubit


def calculate_gate_density(circuit):
    gate_counts = count_x_qubit_gates(circuit)
    if gate_counts == [math.nan, math.nan, math.nan]:
        return math.nan
    gates = gate_counts[0] + (2 * gate_counts[1])
    density = gates / (circuit.depth() * circuit.num_qubits)
    return density


def draw_circuit(qc, file=None, wire_order=None):
    try:
        plt_qc = qc.draw(output='mpl', filename=file, wire_order=wire_order)
        plt_qc.show()
    except HTTPError:
        print(qc)
