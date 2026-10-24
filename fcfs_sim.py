'''
Date: 10/2026
Author: Lylah Clark
Description: First-come-first-serve simple python simulation

Glossary:
rate = messages p/s
mean_service_s = avg time to verify message (s)
end_s = how long to simulate
event = tuple of time,counter,kind(ARRIVAL/DONE),if done, then when message arrived 
'''

import heapq, itertools, random

def run(rate, mean_service_s, end_s, seed=1):
    rng = random.Random(f"{seed}:Part1")      # seeding the RNG for reproducibility
    events, seq = [], itertools.count()        # the to-do list of future events
    queue = []                                # the arrival times of each waiting message
    busy = False                              # says whether the server is working
    delays = []                               # collecting the result

    def schedule(t, kind, arrival=None):
        heapq.heappush(events, (t, next(seq), kind, arrival))

    schedule(rng.expovariate(rate), "ARRIVAL")

    now = 0.0
    while events:                                     # Each time around the loop:
        now, _, kind, arrival = heapq.heappop(events)  # Remove the earliest event
        if now > end_s:                                # stop when clock passes the end
            break

        if kind == "ARRIVAL":
            queue.append(now)                           # join the back of the queue
            schedule(now + rng.expovariate(rate), "ARRIVAL")  # keep the arrivals coming
            if not busy:
                busy = True
                a = queue.pop(0)                        # remove and return first item of list
                schedule(now + rng.expovariate(1 / mean_service_s), "DONE", a)
        else:  # DONE
            delays.append(now - arrival)                # waiting + verifying
            if queue:                                  # if someone is waiting, start on them
                a = queue.pop(0)
                schedule(now + rng.expovariate(1 / mean_service_s), "DONE", a)
            else:                                     # otherwise go idle
                busy = False

    return delays


if __name__ == "__main__":
    lam, mu = 800.0, 1000.0
    d = run(lam, 1 / mu, end_s=300)
    sim = sum(d) / len(d)
    theory = 1 / (mu - lam)         # mean time in system for M/M/1
    print(f"messages: {len(d)} simulated mean delay: {sim * 1000:.2f} ms theory: {theory * 1000:.2f} ms")

    