import random

x = 0
for j in range(0, 100):
  for i in range(0, 100):
    if random.random() < 0.10:
      x = x + 1
  
print(x/99)