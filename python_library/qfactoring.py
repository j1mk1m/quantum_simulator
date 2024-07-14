from quantum_computer import QuantumComputer

q = QuantumComputer()

"""
1. Find smallest L such that 2^L = 1 mod N
2. X = 2^{L/2} mod N
3. Output gcd(X-1, N) and gcd(X+1, N)
"""