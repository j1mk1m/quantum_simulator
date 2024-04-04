import numpy as np
import random

# Unique ID for Qubits
counter = 0

class Qubit:
    def __init__(self, name):
        global counter
        self.name = name
        self.id = counter
        counter += 1

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id 

    def __hash__(self) -> int:
        return hash(self.id)

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
    def hadamard(self, qubit=None):
        hadamard = np.array([[1, 1], [1, -1]]) / np.math.sqrt(2)
        if qubit is None: # hadamard all
            matrix = hadamard
            for _ in range(1, len(self.qubits)):
                matrix = np.kron(matrix, hadamard)
            self.state = matrix @ self.state
        else:
            self.single_qubit_op(qubit, hadamard)

    ### Classical Reversible ###
    # Single qubit operations
    def pauli_X(self, qubit):
        self.toggle(qubit)

    def toggle(self, qubit):
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

        
    def parse(self, a, args, cargs):
        a = a.strip()
        if a in cargs:
            return args[cargs.index(a)]
        return a

    def ccmd_to_qcmd(self, ccmd, args, cargs):
        w, code = ccmd.split(":=")
        w = w.strip()
        if "AND" in code:
            a, b = code.split("AND")
            a, b = self.parse(a, args, cargs), self.parse(b, args, cargs)
            self.if_A_and_B_then_toggle_C(a, b, w)
        elif "NOT" in code:
            a = code.split("NOT")[1].strip()
            a = self.parse(a, args, cargs)
            self.if_not_A_then_toggle_B(a, w)
        elif "OR" in code:
            a, b = code.split("OR")
            a, b = self.parse(a, args, cargs), self.parse(b, args, cargs)
            self.if_A_or_B_then_toggle_C(a, b, w)
        else:
            a = self.parse(code.strip(), args, cargs)
            self.if_A_then_toggle_B(a, w)

    def toggle_f_onto_Cs(self, ccode, *args):
        name, cargs, retvals, ancillas, lines = ccode.get_parsed()
        assert len(args) == len(cargs) + len(retvals)

        self.new_qubit(*ancillas)
        
        for line in lines:
            self.ccmd_to_qcmd(line, args, cargs)

        for i in range(len(retvals)):
            rval = retvals[i]
            self.if_A_then_toggle_B(rval, args[len(cargs) + i])
        
        for i in range(len(lines)-1, -1, -1):
            self.ccmd_to_qcmd(lines[i], args, cargs)
        
        self.extract(*ancillas)
    
    def if_f_then_toggle_C(self, ccode, *args):
        self.toggle_f_onto_Cs(ccode, *args)

    def if_f_then_minus(self, ccode, *args):
        self.new_qubit('new')
        self.toggle("new")
        self.hadamard("new")
        self.if_f_then_toggle_C(ccode, *args, "new")
        self.hadamard("new")
        self.toggle("new")
        self.extract("new")

    def if_perp_then_minus(self, U, U_undo, *args):
        U_undo()
        or4 = CCode("or4")
        self.if_f_then_minus(or4, *args)
        U()

    def if_A_then_minus(self, A):
        new_state = np.zeros_like(self.state)
        i = self.qubits.index(A)
        for j in range(len(self.state)):
            basic = self.index_to_basic_state(j)
            if basic[i] == "1":
                new_state[j] = -self.state[j]
            else:
                new_state[j] = self.state[j]
        self.state = new_state


class CCode:
    """
    Represent function f : {0, 1}^n --> {0, 1}^m
    - file_name: name of AND/OR/NOT classical code
    """
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.parse_ccode()

    def parse_ccode(self):
        lines = []
        with open(self.file_name + ".ccode", 'r') as file:
            for line in file:
                lines.append(line)
        header, footer = lines[0], lines[-1]
        self.name, args = header.split("(")
        args = args.split(")")[0].split(',')
        self.args = [a.strip() for a in args]
        self.retvals = footer.split("return")[1].strip().split(',')
        self.lines = lines[1:-1]
        self.ancillas = set(map(lambda x: x.split(":=")[0].strip(), self.lines))

    def get_parsed(self):
        return self.name, self.args, self.retvals, self.ancillas, self.lines

