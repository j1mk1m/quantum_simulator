from quantum_computer import QuantumComputer, CCode
import numpy as np

q = QuantumComputer()
and4 = CCode("and4")

def R():
    q.if_f_then_minus(and4, "B1", "B2", "B3", "B4")
    q.if_perp_then_minus(q.hadamard, q.hadamard, "B1", "B2", "B3", "B4")

q.new_qubit("B1", "B2", "B3", "B4")
q.hadamard()
for t in range(3):
    R()
out = q.extract()
print(out)