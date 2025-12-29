import networkx as nx
import matplotlib.pyplot as plt
from qiskit.converters import dag_to_circuit
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import CXGate
import random


def generate_dag_with_density(num_qubits, desired_density):
    qreg = QuantumRegister(num_qubits, 'q')
    dag = DAGCircuit()
    dag.add_qreg(qreg)

    max_possible_edges = num_qubits * (num_qubits - 1) // 2
    required_edges = int(desired_density * max_possible_edges)
    possible_edges = [(i, j) for i in range(num_qubits) for j in range(i + 1, num_qubits)]
    selected_edges = random.sample(possible_edges, required_edges)

    for (q1, q2) in selected_edges:
        dag.apply_operation_back(CXGate(), [qreg[q1], qreg[q2]], [])

    return dag


def visualize_dag_with_networkx(dag, desired_density):
    G = nx.DiGraph()  # Directed graph (DAG)

    # Extract qubit connections from the DAG
    for node in dag.topological_op_nodes():
        gate = node.op
        qubits = [q._index for q in node.qargs]
        if isinstance(gate, CXGate):
            G.add_edge(f"q[{qubits[0]}]", f"q[{qubits[1]}]")  # Add edge to the graph

    # Draw the graph using networkx and matplotlib
    pos = nx.spring_layout(G)  # Layout for positioning nodes
    nx.draw(G, pos, with_labels=True, node_color='lightblue', font_weight='bold', node_size=2000)
    plt.title("Circuit, density = {}".format(desired_density))
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    num_qubits = 7
    desired_density = 0.6

    dag = generate_dag_with_density(num_qubits, desired_density)
    visualize_dag_with_networkx(dag, desired_density)

    circuit = dag_to_circuit(dag)
    print(circuit)

    circuit.draw(output="mpl")
    plt.title("Circuit: density = %.2f, depth = %d " % (desired_density, circuit.depth()))
    plt.show()

