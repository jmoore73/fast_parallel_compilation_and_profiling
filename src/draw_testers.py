import os
import qiskit.qasm3
from qiskit import QuantumCircuit
from qiskit.qasm3 import QASM3ImporterError

if __name__ == '__main__':

    for core_dir in os.listdir("../qasm"):
        if core_dir.endswith("cores"):
            for file in os.listdir(f"../qasm/{core_dir}"):
                if file.endswith(".qasm"):
                    qasm_file = f"../qasm/{core_dir}/{file}"
                    print(f"Drawing {qasm_file}")
                    try:
                        circuit = qiskit.qasm3.load(qasm_file)
                    except QASM3ImporterError as e:
                        print(f"Failed to load the QASM 3 file: {e}")
                        circuit = QuantumCircuit.from_qasm_file(qasm_file)
                    diagram_filename = (qasm_file.split("/")[-1]).replace('.qasm', '.png')
                    diagram_dir = f"diagrams/{core_dir}"
                    os.makedirs(diagram_dir, exist_ok=True)
                    circuit.draw(output="mpl", filename=os.path.join(diagram_dir, diagram_filename))
                    print(f"Saved the diagram of {diagram_filename}")

    exit(0)