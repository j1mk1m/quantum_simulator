# Unique ID for Qubits
counter = 0

keywords = ["all"]

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
