from quantum_computer import QuantumComputer
import random
import numpy as np

q = QuantumComputer()

angle = random.randint(0, 90)
print("MysteryRot:", angle)

def IsMedium(angle):
    count = 0
    for t in range(100):
        q.new_qubit("A")
        q.rotate("A", angle)
        a = q.extract()[0]
        if a == "1": count += 1
    return 20 <= count <= 80

def Factor2Estimate(angle):
    k_max = 2**10
    k = 2
    while k < k_max:
        if IsMedium(angle * k):
            return 45 / k
        k *= 2

#pred = Factor2Estimate(angle)
#print(pred)

def IntervalEstimate(angle):
    count = 0
    T = 120000
    for i in range(T):
        q.new_qubit("A")
        q.rotate("A", angle)
        a = q.extract()[0]
        if a == "1": count += 1
    qh = count / T
    theta = np.math.asin(np.math.sqrt(qh))
    return theta * 180 / np.math.pi

pred = IntervalEstimate(angle)
print("Predicted", pred)


def HadamardTest():
    q.new_qubit("D")
    q.hadamard("D")
    # if D then R on A1, ..., Am
    q.hadamard("D")
    d = q.extract("D")

C = 120000
def RotationEstimation(n, R, *As):
    for i in range(n):
        for _ in range(C):
            q.new_qubit("D")
            R("D")
            d = q.extract()[0]