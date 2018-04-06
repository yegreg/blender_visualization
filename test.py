import random

N = 100000

covered = set()

for i in range(N):
    x = random.randint(0, N - 1)
    covered.add(x)

print(len(covered))
