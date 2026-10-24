# Drill 1: variables and arithmetic
rate = 800.0 #messages per second
service_ms = 1.0 #milliseconds per verification
capacity = 1000 / service_ms
print(rate, capacity, rate / capacity)

# Drill 2: lists
waits = [3, 1, 4]
waits.append(1)
print(waits, len(waits), waits[0], waits[-1], sorted(waits))

# Drill 3: dictionaries
costs = {"sig": 1.0, "chain": 2.0}
costs["kem"] = 0.5
print(costs["chain"], list(costs))

# Drill 4: loops and if
total = 0
for w in waits:
    if w > 1:
        total += w
print(total)

# Drill 5: functions
def utilization(rate_hz, service_ms):
    return rate_hz * service_ms / 1000
print(utilization(800, 1.0), utilization(1500, 1.0))

# Drill 6: f-strings
print(f"load is {utilization(800, 1.0):.0%} and {utilization(1500, 1.0):.2f}")

# Drill 7: a dataclass is a labelled budle of values
from dataclasses import dataclass

@dataclass
class Message:
    id: int
    arrival: float
m = Message(7, 0.25)
print(m, m.arrival)

# Drill 8: tuples compare left to right
print(( 0, 2, 1, "DONE") < (0.5, 0, "ARRIVAL"), (0.5, 0, "A") < (0.5, 1, "B"))

# Drill 9: seeded random numbers repeat
import random 
r1, r2 = random.Random("42:a"), random.Random("42:a")
print([round(r1.random(), 3) for _ in range(3)], [round(r2.random(), 3) for _ in range(3)])

# Drill 10: heapq always gives the smallest item first
import heapq
events = []
heapq.heappush(events, (0.5, "ARRIVAL"))
heapq.heappush(events, (0.2, "DONE"))
print(heapq.heappop(events), heapq.heappop(events))


