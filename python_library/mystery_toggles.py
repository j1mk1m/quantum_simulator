from quantum_computer import QuantumComputer

q = QuantumComputer()

def MysteryToggles(A, B, C, D, ans):
    #q.if_A_then_toggle_B(A, ans)
    q.if_A_then_toggle_B(B, ans)
    #q.if_A_then_toggle_B(C, ans)
    q.if_A_then_toggle_B(D, ans)

def QuantumTogglesDetective():
    q.new_qubit("A", "B", "C", "D", "ans")
    q.toggle("ans")
    q.hadamard()
    MysteryToggles("A", "B", "C", "D", "ans")
    q.hadamard()
    out = q.extract()
    print(out)

QuantumTogglesDetective()