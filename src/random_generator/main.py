import math
import time
import qiskit.qasm3
import os

from helper import remove_ops_for_given_density, calculate_gate_density, parse_arguments
from random_generator import random_circuit

MEASURE = False
SEED = 2

if __name__ == '__main__':
    (GATE_SET, DRAW, COMBINE,
     MIN_WIDTH, MAX_WIDTH, WIDTH_STEP,
     MIN_DEPTH, MAX_DEPTH, DEPTH_STEP,
     MIN_DENSITY, MAX_DENSITY, DENSITY_STEP) \
        = parse_arguments()

    if COMBINE:
        general_dir = "../random_circuit_qasm"
        if not os.path.exists(general_dir):
            os.makedirs(general_dir)

    print("***** Using gate set: ", GATE_SET)
    overall_counter = 0

    for width in range(MIN_WIDTH, MAX_WIDTH+1, WIDTH_STEP):
        counter = 0
        MIN_DENSITY = max(1/width, MIN_DENSITY)

        for density_100 in range(int(MIN_DENSITY*100), int((MAX_DENSITY*100)+1), int(DENSITY_STEP*100)):
            density = density_100 / 100
            if density < (1/width):
                print("***** WARNING ***** MIN_DENSITY must be greater than 1/WIDTH. "
                      "Skipping %d qubit circuits @ %s density." % (width, str(density)))
                continue

            for depth in range(MAX_DEPTH, MIN_DEPTH-1, -DEPTH_STEP):
                start_time = time.time()
                qasm_dir = ("qasm_files/density_%s/%d_qubits/" % (str(density), width))
                filename = ("random_circuit_%s_%dq_%dg.qasm" % (str(density), width, depth))

                if not os.path.exists(qasm_dir):
                    os.makedirs(qasm_dir)
                    print("Created directory %s" % qasm_dir)

                qc = random_circuit(width, depth, gate_set=GATE_SET, max_operands=2, measure=MEASURE, seed=SEED)
                qc.name = ("random_%dqubits_%ddepth_%sdens" % (width, depth, str(density)))
                print("Removing gates to obtain circuit of desired density. %d qubits, %d depth, %s dens" % (width, depth, str(density)))
                new_qc = remove_ops_for_given_density(qc, density, draw=DRAW)

                if new_qc is None:
                    print("No circuit created for %d qubits, %d depth, %s density \n" % (width, depth, str(density)))
                    continue

                calculated_density = calculate_gate_density(new_qc)
                assert math.isclose(calculated_density, density, rel_tol=DENSITY_STEP / 2)
                qasm = qiskit.qasm3.dumps(qc)
                counter += 1

                with open(os.path.join(qasm_dir, filename), "w") as qasm_file:
                    qasm_file.write(qasm)
                if COMBINE:
                    with open(os.path.join(general_dir, filename), "w") as qasm_file:
                        qasm_file.write(qasm)

                end_time = time.time()
                print("Wrote qasm file %s [circuit no. %d] in %d seconds\n" % (filename, overall_counter+1, (end_time-start_time)), flush=True)
                overall_counter += 1

        print("*** Created %d %d-qubit circuits *** \n\n" % (counter, width), flush=True)

