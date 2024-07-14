from quantum_computer import QuantumComputer, CCode

q = QuantumComputer()
ccode = CCode("palindrome4")

q.new_qubit("B1", "B2", "B3", "B4")
q.hadamard()
q.if_f_then_minus(ccode, "B1", "B2", "B3", "B4")
q.hadamard()
q.print_state()
d = q.extract()
print(d)