from quantum_computer import QuantumComputer

def EPR_pair():
    q = QuantumComputer()
    
    q.new_qubit("A")
    q.new_qubit("B")
    q.hadamard("A")
    q.CNOT("A", "B")
    q.print_state()
    q.extract()

def single_qubit():
    q = QuantumComputer()

    q.new_qubit("A")
    q.toggle("A")
    q.print_state()
    q.hadamard()
    q.print_state()
    q.hadamard()
    q.print_state()
    q.pauli_X("A")
    q.print_state()
    q.rotate("A", 180)
    q.print_state()
 
def ccode_translation():
    q = QuantumComputer()

    q.new_qubit("A", "B", "C", "D", 'ans')
    q.hadamard()
    q.print_state()
    #q.if_f_then_toggle_C("ccode.txt", "A", "B", "C", "D", "ans")
    q.if_f_then_minus("ccode.txt", "A", "B", "C", "D")
    q.hadamard()
    q.print_state()
    q.extract()
    
#EPR_pair()
#single_qubit()

ccode_translation()