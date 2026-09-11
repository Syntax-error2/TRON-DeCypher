import itertools
pool = ["Cyb3r", "D3f3ns3"]
for combo in itertools.product(pool, repeat=2):
    print(combo)
