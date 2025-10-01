from qiskit import QuantumRegister, QuantumCircuit

from src.main.helper import remove_ops_for_given_density, draw_circuit
from src.main.random_generator import random_circuit

GATE_SET = ["H", "S", "X", "T", "CX"]
WIDTH = 2
DEPTH = 10
OPERANDS = 2
DENSITY = 0.75


if __name__ == '__main__':
    qc = random_circuit(WIDTH, DEPTH, gate_set=GATE_SET, max_operands=OPERANDS, measure=False, seed=7)
    qc.name = ("random_%dqubits_%ddepth_%sdens" % (WIDTH, DEPTH, str(DENSITY)))
    draw_circuit(qc, "../single_example_circuit_diagrams/" + qc.name + "_before.png")
    new_qc = remove_ops_for_given_density(qc, DENSITY, draw=False)
    if new_qc is None:
        print("No circuit created for %d qubits, %d depth, %s density \n" % (WIDTH, DEPTH, str(DENSITY)))
    else:
        draw_circuit(new_qc, "../single_example_circuit_diagrams/" + new_qc.name + "_after.png")

    qreg_q = QuantumRegister(2, 'q')
    circuit = QuantumCircuit(qreg_q)
    circuit.name = qc.name
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.s(qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.cx(qreg_q[0], qreg_q[1])
    circuit.h(qreg_q[1])
    circuit.s(qreg_q[1])
    circuit.t(qreg_q[1])
    circuit.x(qreg_q[1])
    draw_circuit(circuit, "../single_example_circuit_diagrams/" + circuit.name + "_after.png")

