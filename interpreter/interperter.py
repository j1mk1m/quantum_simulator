import sys
from qc_simulator import QuantumComputer
from qubit import Qubit

class CCode:
    """
    Represent function f : {0, 1}^n --> {0, 1}^m
    - file_name: name of AND/OR/NOT classical code
    """
    def __init__(self, arguments, ancillas, retvals, content) -> None:
        self.arguments = arguments
        self.ancillas = ancillas
        self.retvals = retvals
        self.content = content

    def get_line(self, num):
        return self.content[num]

    def end_file(self, num):
        return num >= len(self.content)

class QCode:
    def __init__(self, arguments, content) -> None:
        self.arguments = arguments
        self.content = content 
    
    def get_line(self, num):
        return self.content[num]
    
    def end_file(self, num):
        return num >= len(self.content)

class QuantumInterpreter:
    def __init__(self) -> None:
        self.qc = QuantumComputer()
        self.qcodes = {}
        self.ccodes = {}
        self.workspace = {}
        self.line_num = 0
        self.code = None
        self.stack = []
    
    def reset_hard(self):
        self.qcodes = {}
        self.ccodes = {}
        self.reset()
    
    def reset(self):
        self.qc = QuantumComputer()
        self.workspace = {}
        self.line_num = 0
        self.code = None
        self.stack = []

    # Parse files
    def parse(self, file_name):
        self.parse_qcode(file_name)
        assert "main" in self.qcodes
        self.code = self.qcodes["main"]
        for ccode in self.ccodes:
            self.ccode_to_qcode(ccode)

    def parse_qcode(self, file_name, code_name=None):
        if ".qcode" not in file_name:
            file_name += ".qcode"
        lines = self.get_lines(file_name)
        name, arguments, content = None, [], []
        for line in lines:
            if line.startswith("QCode"):
                qcodes = line[5:].strip().split(",")
                for qcode in qcodes:
                    c_name = qcode.split(":")[1].strip()
                    if c_name == "*": c_name = None
                    file_name = qcode.split(':')[0].strip()
                    self.parse_qcode(file_name, c_name)
            elif line.startswith("CCode"):
                ccodes = line[5:].strip().split(",")
                for ccode in ccodes:
                    c_name = ccode.split(":")[1].strip()
                    if c_name == "*": c_name = None
                    file_name = ccode.split(":")[0].strip()
                    self.parse_ccode(file_name, c_name)
            elif line.startswith("def"):
                if name is not None and (code_name is None or code_name == name):
                    self.qcodes[name] = QCode(arguments, content)
                name, arguments, content = None, [], []
                name = line.split("def")[1].split("(")[0].strip()
                arguments = [a.strip() for a in line.split("(")[1].split(")")[0].strip().split(',')]
            else:
                content.append(line)

        if code_name is None or code_name == name:
            self.qcodes[name] = QCode(arguments, content)                

    def parse_ccode(self, file_name, code_name=None):
        if ".ccode" not in file_name:
            file_name += ".ccode"
        lines = self.get_lines(file_name)
        name, arguments, ancillas, retvals, content = None, [], [], [], []
        for line in lines:
            if line.startswith("def"):
                if name is not None and (code_name is None or code_name == name):
                    self.ccodes[name] = CCode(arguments, ancillas, retvals, content)
                name, arguments, ancillas, retvals, content = None, [], [], [], []
                name = line.split("def")[1].split("(")[0].strip()
                arguments = [a.strip() for a in line.split("(")[1].split(")")[0].strip().split(',')]
            elif line.startswith("return"):
                retvals = [r.strip() for r in line.split("return")[1].split(",")]
            else:
                ancillas.append(line.split(":=")[0].strip())
                content.append(line)
        if name is not None and (code_name is None or code_name == name):
            self.ccodes[name] = CCode(arguments, ancillas, retvals, content)

    def get_lines(self, file_name):
        lines = []
        with open(file_name, 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"): continue
                lines.append(line)
        return lines

    def run(self):
        while not self.code.end_file(self.line_num):
            line = self.code.get_line(self.line_num)
            self.line_num += 1

            self.process_cmd(line)

            if self.code.end_file(self.line_num) and len(self.stack) > 0:
                frame = self.stack.pop()
                self.workspace = frame.workspace
                self.code = frame.code
                self.line_num = frame.line_num 

    def process_cmd(self, cmd):
        if cmd.startswith("new qubit"):
            qs = [q.strip() for q in cmd.split("new qubit")[1].split(",")]
            qbs = []
            for q in qs:
                qubit = Qubit(q)
                self.workspace[q] = qubit
                qbs.append(qubit)
            self.qc.new_qubit(*qbs)
        elif cmd.startswith("extract"):
            qs = [q.strip() for q in cmd.split("extract")[1].split(",")]
            if qs[0] == "all":
                qbs = self.workspace.values()
            else:
                qbs = [self.workspace[q] for q in qs]
            out = self.qc.extract(*qbs)
            print(f"Extracted {''.join(qs)}: {out}")
        elif cmd.startswith("call"):
            qcode = cmd.split("call")[1].split("(")[0].strip()
            arg_string = cmd.split("(")[1].split(")")[0]
            if len(arg_string) == 0:
                args = []
            else:
                args = [a.strip() for a in cmd.split("(")[1].split(")")[0].split(",")]

            # save current frame
            frame = Frame(self.workspace, self.code, self.line_num)
            self.stack.append(frame)

            # change frame to new qcode
            self.code = self.qcodes[qcode]
            self.line_num = 0
            new_ws = {}
            for i in range(len(args)):
                new_ws[self.code.arguments[i]] = self.workspace[args[i]]
            self.workspace = new_ws
        elif cmd.startswith("print"):
            self.qc.print_state()
        elif cmd.startswith("repeat"):
            pass
        elif cmd.startswith("end"):
            pass
        elif cmd.startswith("Hadamard"):
            qs = [q.strip() for q in cmd.split("Hadamard")[1].split(",")]
            if qs[0] == "all":
                qs = self.workspace.values()
            else:
                qs = [self.workspace[q] for q in qs]
            self.qc.hadamard(*qs)
        elif cmd.startswith("toggle"):
            q = cmd.split("toggle")[1].strip()
            self.qc.toggle(self.workspace[q])
        elif cmd.startswith("if perp"):
            code = cmd.split("if perp")[1].split("(")[0].strip()
            forward = self.qcodes[code]
            arg_string = cmd.split("(")[1].split(")")[0]
            if len(arg_string) == 0:
                args = []
            else:
                args = [a.strip() for a in cmd.split("(")[1].split(")")[0].split(",")]
            undo_code = self.undo_qcode(code)

            # TODO
        elif cmd.startswith("if"):
            cond = cmd.split("if")[1].split("then")[0].strip()
            if '(' in cond: # if f() then...
                ccode = cond.split("(")[0].strip()
                args_string = cond.split("(")[1].split(")")[0]
                if len(args_string) == 0:
                    args = []
                else:
                    args = [a.strip() for a in args_string.split(",")]
                
                if "minus" in cmd: # if f then minux
                    new_code = self.qcodes[f"if_{ccode}_then_minus"]
                else:
                    cs = [c.strip() for c in cmd.split("toggle")[1].strip().split(",")]
                    args += cs
                    if len(cs) == 1:
                        new_code = self.qcodes[f"if_{ccode}_then_toggle"]
                    else:
                        new_code = self.qcodes[f"if_{ccode}_then_toggle_onto"]

                # save frame
                frame = Frame(self.workspace, self.code, self.line_num)
                self.stack.append(frame)

                # change to new frame
                self.code = new_code
                self.line_num = 0
                new_ws = {}
                for i in range(len(args)):
                    new_ws[self.code.arguments[i]] = self.workspace[args[i]]
                self.workspace = new_ws
            else: # CNOT, CCNOT, etc
                conds = [c.strip() for c in cond.split(" ")]
                if len(conds) == 1: # if A then toggle B
                    A = self.workspace[conds[0]]
                    B = self.workspace[cmd.split("toggle")[1].strip()]
                    self.qc.if_A_then_toggle_B(A, B)
                elif len(conds) == 2: # if not A then toggle B
                    assert conds[0] == "NOT"
                    A = self.workspace[conds[1]]
                    B = self.workspace[cmd.split("toggle")[1].strip()]
                    self.qc.if_not_A_then_toggle_B(A, B)
                elif len(conds) == 3 and conds[1] == "AND":
                    A = self.workspace[conds[0]]
                    B = self.workspace[conds[2]]
                    C = self.workspace[cmd.split("toggle")[1].strip()]
                    self.qc.if_A_and_B_then_toggle_C(A, B, C)
                else:
                    assert len(conds) == 3 and conds[1] == "OR"
                    A = self.workspace[conds[0]]
                    B = self.workspace[conds[2]]
                    C = self.workspace[cmd.split("toggle")[1].strip()]
                    self.qc.if_A_or_B_then_toggle_C(A, B, C)
        else:
            raise ParseError

    def undo_qcode(self, name):
        if f"undo_{name}" not in self.qcodes:
            forward = self.qcodes[name]
            args, content = forward.arguments, forward.content
            self.qcodes[f"undo_{name}"] = QCode(args, content.reverse())
        return self.qcodes[f"undo_{name}"]

    def ccode_to_qcode(self, name):
        ccode = self.ccodes[name]
        cargs, retvals, ancillas, lines = ccode.arguments, ccode.retvals, ccode.ancillas, ccode.content
        rargs = [f"C{i}" for i in range(len(retvals))]
        args = cargs + rargs

        content = []

        content.append("new qubit " + ", ".join(ancillas))

        for line in lines:
            content.append(self.ccmd_to_qcmd(line, args, cargs))
        
        for i in range(len(retvals)):
            rv = retvals[i]
            cv = rargs[i]
            content.append(f"if {rv} then toggle {cv}")

        for i in range(len(lines)-1, -1, -1):
            line = lines[i]
            content.append(self.ccmd_to_qcmd(line, args, cargs))

        content.append(f"extract {', '.join(ancillas)}")

        qcode = QCode(args, content)
        if len(rargs) == 1: # if f then toggle C 
            self.qcodes[f"if_{name}_then_toggle"] = qcode
            # if f then minus
            content = ["new qubit C0", "toggle C0", "Hadamard C0"] + content + ["Hadamard C0", "toggle C0", "extract C0"]
            qcode = QCode(cargs, content)
            self.qcodes[f"if_{name}_then_minus"] = qcode
        else: # toggle f onto Cs
            self.qcodes[f"if_{name}_then_toggle_onto"] = qcode

    def ccmd_to_qcmd(self, ccmd, args, cargs):
        w, code = ccmd.split(":=")
        w = w.strip()
        if "AND" in code:
            a, b = code.split("AND")
            a, b = a.strip(), b.strip()
            return f"if {a} AND {b} then toggle {w}"
        elif "NOT" in code:
            a = code.split("NOT")[1].strip()
            return f"if NOT {a} then toggle {w}"
        elif "OR" in code:
            a, b = code.split("OR")
            a, b = a.strip(), b.strip()
            return f"if {a} OR {b} then toggle {w}"
        else:
            a = code.strip()
            return f"if {a} then toggle {w}"

class Frame:
    def __init__(self, workspace, code, line_num) -> None:
        self.workspace = workspace 
        self.code = code 
        self.line_num = line_num 

class ParseError(Exception):
    pass

if __name__=="__main__":
    file_name = sys.argv[1]

    interpreter = QuantumInterpreter()
    interpreter.parse(file_name)
    interpreter.run()
