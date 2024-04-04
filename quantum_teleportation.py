from quantum_computer import QuantumComputer
import random

q = QuantumComputer()

# Alice and Bob share EPR pair
q.new_qubit("A", "B")
q.hadamard("A")
q.CNOT("A", "B")

# Charlie creates qubit in some state
q2 = QuantumComputer()
q.new_qubit("C")
q2.new_qubit("C")
angle = random.randint(0, 359)
q2.rotate("C", angle)
q.rotate("C", angle)
print("Charlie's state: ", end="")
q2.print_state()

# Bob performs operations on B and C
q.if_A_then_toggle_B("C", "B")
q.hadamard("C")
b, c = q.extract("B", "C")

# Alice
if b == "0" and c == "0":
    pass
if b == "0" and c == "1":
    q.if_A_then_minus("A")
if b == "1" and c == "0":
    q.toggle("A")
if b == "1" and c == "1":
    q.toggle("A")
    q.if_A_then_minus("A")

# Alice should now have the same state as Charlie
print("Alice's state: ", end="")
q.print_state()