import numpy as np
import random

class QuantumComputer:
    def __init__(self) -> None:
        self.qubits = []
        self.state = np.ones(1)

    # Qubit creation and deletion
    def new_qubit(self, *args):
        for qubit in args:
            self.qubits.append(qubit)
            self.state = np.kron(self.state, np.array([1.0, 0.0]))
 
    def extract(self, *args):
        if len(args) == 0: # extract all
            probs = self.state * self.state 
            r = random.random()
            cum_prob = 0
            for i in range(probs.shape[0]):
                p = probs[i]
                if cum_prob <= r < cum_prob + p:
                    output = self.index_to_basic_state(i)
                    #print(f"Measurement of {''.join(self.qubits)}: {output}")
                    break
                cum_prob += p

            self.qubits = []
            self.state = np.ones(1)
            return output
        output = "" 
        for qubit in args:
            probs = self.state * self.state 
            r = random.random()
            i = self.qubits.index(qubit)
            res_0, res_1 = 0.0, 0.0
            for j in range(len(self.state)):
                basic = self.index_to_basic_state(j)
                if basic[i] == "0": res_0 += probs[j]
                else: res_1 += probs[j]
            final = r < res_0 # measurement is 0

            new_state = np.zeros(len(self.state)//2)
            index = 0
            # conidition on measurement
            for j in range(len(self.state)):
                basic = self.index_to_basic_state(j)
                if (basic[i] == "0" and final) or (basic[i] == "1" and not final):
                    new_state[index] = self.state[j]
                    index += 1
            # normalize
            factor = np.math.sqrt(np.sum(new_state * new_state))
            new_state /= factor
            self.state = new_state
            self.qubits.remove(qubit)

            #if final: print(f"Measurement of {qubit}: 0")
            #else: print(f"Measurement of {qubit}: 1")
            output += ("0" if final else "1")

        return output

    # Hadamard    
    def hadamard(self, *qubits):
        if len(qubits) == 0:
            qubits = self.qubits
        for qubit in qubits:
            self.hadamard_single(qubit)

    def hadamard_single(self, qubit):
        n = len(self.qubits)
        i = n - 1 - self.qubits.index(qubit)
        d = 1 << i
        new_state = np.zeros_like(self.state)
        for j in range(2**(n-1)):
            index = ((j >> i) << (i + 1)) + (j % d)
            a, b = self.state[index], self.state[index + d]
            new_state[index], new_state[index + d] = a + b, a - b
        self.state = new_state / np.math.sqrt(2)

    def hadamard_all_matrix(self):
        hadamard = np.array([[1, 1], [1, -1]]) / np.math.sqrt(2)
        matrix = hadamard
        for _ in range(1, len(self.qubits)):
            matrix = np.kron(matrix, hadamard)
        self.state = matrix @ self.state

    def hadamard_single_matrix(self, qubit):
        hadamard = np.array([[1, 1], [1, -1]]) / np.math.sqrt(2)
        self.single_qubit_op(qubit, hadamard)

    ### Classical Reversible ###
    # Single qubit operations
    def pauli_X(self, qubit):
        self.NOT(qubit)
    
    def toggle(self, qubit):
        self.NOT(qubit)

    def NOT(self, qubit):
        i = self.qubits.index(qubit)
        new_state = np.zeros_like(self.state)
        for j in range(len(self.state)):
            n = len(self.qubits)
            bit = ((j >> (n - 1 - i)) % 2)
            add = 1 << (n - 1 - i)
            k = j + (add if bit == 0 else -add)
            new_state[j] = self.state[k]
        self.state = new_state

    def rotate(self, qubit, angle):
        sin = np.math.sin(angle / 180 * np.math.pi)
        cos = np.math.cos(angle / 180 * np.math.pi)
        rotation = np.array([[cos, -sin], [sin, cos]])
        self.single_qubit_op(qubit, rotation)   

    def single_qubit_op(self, qubit, op):
        identity = np.array([[1, 0], [0, 1]])
        matrix = None
        for q in self.qubits:
            if q == qubit:
                if matrix is None:
                    matrix = op 
                else:
                    matrix = np.kron(matrix, op)
            else:
                if matrix is None:
                    matrix = identity
                else:
                    matrix = np.kron(matrix, identity)
        self.state = matrix @ self.state

    # Multi-qubit operations
    def CNOT(self, A, B):
        i1, i2 = self.qubits.index(A), self.qubits.index(B)
        new_state = np.zeros_like(self.state)
        for i in range(len(self.state)):
            basic = self.index_to_basic_state(i)
            if basic[i1] == "1":
                target = basic[:i2] + ("1" if basic[i2] == "0" else "0") + basic[i2+1:]
                new_state[i] = self.state[self.basic_state_to_index(target)]
            else:
                new_state[i] = self.state[i]
        self.state = new_state

    def if_A_then_toggle_B(self, A, B):
        self.CNOT(A, B)
        
    def CCNOT(self, A, B, C):
        i1, i2, i3 = self.qubits.index(A), self.qubits.index(B), self.qubits.index(C)
        new_state = np.zeros_like(self.state)
        for i in range(len(self.state)):
            basic = self.index_to_basic_state(i)
            if basic[i1] == "1" and basic[i2] == "1":
                target = basic[:i3] + ("1" if basic[i3] == "0" else "0") + basic[i3+1:]
                new_state[i] = self.state[self.basic_state_to_index(target)]
            else:
                new_state[i] = self.state[i]
        self.state = new_state
    
    def if_A_and_B_then_toggle_C(self, A, B, C):
        self.CCNOT(A, B, C)

    # Extra functions
    def swap(self, A, B):
        i1, i2 = self.qubits.index(A), self.qubits.index(B)
        new_state = np.zeros_like(self.state)
        for i in range(len(self.state)):
            basic = self.index_to_basic_state(i)
            target = basic
            target[i1] = basic[i2]
            target[i2] = basic[i1]
            new_state[i] = self.state[self.basic_state_to_index(target)]
        self.state = new_state
    
    def if_A_or_B_then_toggle_C(self, A, B, C):
        self.toggle(A)
        self.toggle(B)
        self.if_A_and_B_then_toggle_C(A, B, C)
        self.toggle(C)
        self.toggle(B)
        self.toggle(A)

    def if_not_A_then_toggle_B(self, A, B):
        self.toggle(A)
        self.if_A_then_toggle_B(A, B)
        self.toggle(A)
    
    # Utils
    def print_state(self):
        print(self.state)

    def index_to_basic_state(self, index):
        state = ""
        for _ in range(len(self.qubits)):
            if index % 2 == 0:
                state = "0" + state
            else:
                state = "1" + state
            index = index // 2
        return state
    
    def basic_state_to_index(self, basic):
        index = 0
        for c in basic:
            index *= 2
            if c == "1":
                index += 1
        return index

         
