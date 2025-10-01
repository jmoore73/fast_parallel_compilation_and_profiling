from qiskit.circuit.library import standard_gates


def get_gates(num_qubits, gate_set):
    gate_sets = [gates_1q, gates_2q, gates_3q, gates_4q]
    if gate_set is None:
        return list(gate_sets[num_qubits-1].values())
    else:
        limited_gate_set = []
        for gate in gate_set:
            if gate_sets[num_qubits-1].__contains__(gate):
                limited_gate_set.append(gate_sets[num_qubits-1][gate])
        return limited_gate_set


gates_1q = {
    "I" : (standard_gates.IGate, 1, 0),
    "SX" : (standard_gates.SXGate, 1, 0),
    "X" : (standard_gates.XGate, 1, 0),
    "RZ" : (standard_gates.RZGate, 1, 1),
    "R" : (standard_gates.RGate, 1, 2),
    "H" : (standard_gates.HGate, 1, 0),
    "P" : (standard_gates.PhaseGate, 1, 1),
    "RX" : (standard_gates.RXGate, 1, 1),
    "RY" : (standard_gates.RYGate, 1, 1),
    "S" : (standard_gates.SGate, 1, 0),
    "SDG" : (standard_gates.SdgGate, 1, 0),
    "SXDG" : (standard_gates.SXdgGate, 1, 0),
    "T" : (standard_gates.TGate, 1, 0),
    "TDG" : (standard_gates.TdgGate, 1, 0),
    "U" : (standard_gates.UGate, 1, 3),
    "U1" : (standard_gates.U1Gate, 1, 1),
    "U2" : (standard_gates.U2Gate, 1, 2),
    "U3" : (standard_gates.U3Gate, 1, 3),
    "Y" : (standard_gates.YGate, 1, 0),
    "Z" : (standard_gates.ZGate, 1, 0),
}

gates_2q = {
    "CX" : (standard_gates.CXGate, 2, 0),
    "DCX" : (standard_gates.DCXGate, 2, 0),
    "CH" : (standard_gates.CHGate, 2, 0),
    "CP" : (standard_gates.CPhaseGate, 2, 1),
    "CRX" : (standard_gates.CRXGate, 2, 1),
    "CRY" : (standard_gates.CRYGate, 2, 1),
    "CRZ" : (standard_gates.CRZGate, 2, 1),
    "CSX" : (standard_gates.CSXGate, 2, 0),
    "CU" : (standard_gates.CUGate, 2, 4),
    "CU1" : (standard_gates.CU1Gate, 2, 1),
    "CU3" : (standard_gates.CU3Gate, 2, 3),
    "CY" : (standard_gates.CYGate, 2, 0),
    "CZ" : (standard_gates.CZGate, 2, 0),
    "RXX" : (standard_gates.RXXGate, 2, 1),
    "RYY" : (standard_gates.RYYGate, 2, 1),
    "RZZ" : (standard_gates.RZZGate, 2, 1),
    "RZX" : (standard_gates.RZXGate, 2, 1),
    "XXMinusYY" : (standard_gates.XXMinusYYGate, 2, 2),
    "XXPlusYY" : (standard_gates.XXPlusYYGate, 2, 2),
    "ECR" : (standard_gates.ECRGate, 2, 0),
    "CS" : (standard_gates.CSGate, 2, 0),
    "CSDG" : (standard_gates.CSdgGate, 2, 0),
    "SWAP" : (standard_gates.SwapGate, 2, 0),
    "ISWAP" : (standard_gates.iSwapGate, 2, 0),
}
gates_3q = {
    "CCX" : (standard_gates.CCXGate, 3, 0),
    "CSWAP" : (standard_gates.CSwapGate, 3, 0),
    "CCZ" : (standard_gates.CCZGate, 3, 0),
    "RCCX" : (standard_gates.RCCXGate, 3, 0),
}
gates_4q = {
    "C3SX" : (standard_gates.C3SXGate, 4, 0),
    "RC3X" : (standard_gates.RC3XGate, 4, 0),
}