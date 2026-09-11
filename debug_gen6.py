import itertools

def leet_mutations(word: str) -> list[str]:
    replacements = {'a': ['a', '4'], 'e': ['e', '3'], 'i': ['i', '1'], 'o': ['o', '0'], 's': ['s', '5'], 't': ['t', '7'], 'g': ['g', '9'], 'b': ['b', '8'], 'A': ['A', '4'], 'E': ['E', '3'], 'I': ['I', '1'], 'O': ['O', '0'], 'S': ['S', '5'], 'T': ['T', '7'], 'G': ['G', '9'], 'B': ['B', '8']}
    options = []
    for c in word:
        if c in replacements:
            options.append(replacements[c])
        else:
            options.append([c])
            
    muts = []
    # don't explode memory if word is extremely long
    if len(options) > 15:
        # fallback
        res = ""
        for c in word:
            res += replacements.get(c, [c])[1] if len(replacements.get(c, [c])) > 1 else c
        muts.append(res)
    else:
        for combo in itertools.product(*options):
            muts.append("".join(combo))
    
    final_muts = []
    for m in list(dict.fromkeys(muts)):
        final_muts.append(m)
        final_muts.append(m.capitalize())
        final_muts.append(m.upper())
            
    return list(dict.fromkeys(final_muts))

print(leet_mutations("circuit"))
