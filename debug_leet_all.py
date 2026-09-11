import itertools

def leet_mutations_all(word: str) -> list[str]:
    replacements = {'a': ['a', '4'], 'e': ['e', '3'], 'i': ['i', '1'], 'o': ['o', '0'], 's': ['s', '5'], 't': ['t', '7'], 'g': ['g', '9'], 'b': ['b', '8'], 'A': ['A', '4'], 'E': ['E', '3'], 'I': ['I', '1'], 'O': ['O', '0'], 'S': ['S', '5'], 'T': ['T', '7'], 'G': ['G', '9'], 'B': ['B', '8']}
    
    options = []
    for c in word:
        if c in replacements:
            options.append(replacements[c])
        else:
            options.append([c])
            
    muts = []
    for combo in itertools.product(*options):
        muts.append("".join(combo))
    return muts

print(leet_mutations_all("Defense"))
