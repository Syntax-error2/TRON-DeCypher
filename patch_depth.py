import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make Depth 2 use a smaller pool (e.g., top 1000 words instead of all high_priority_base)
patch = '''
        # P55: Word Combinations (Depth 2)
        if self.config.max_combination_depth >= 2:
            pool = []
            for w in high_priority_base[:100]: # drastically reduce pool for depth 2
                pool.append(w.capitalize())
                pool.append(w.lower())
                if self.config.enable_leetspeak:
                    pool.extend(self.leet_mutations(w.capitalize()))
            pool = list(dict.fromkeys(pool))
            
            for combo in itertools.product(pool, repeat=2):
'''
content = re.sub(r'        # P55: Word Combinations \(Depth 2\)\n(?:.*\n){2,15}?            for combo in itertools\.product\(pool, repeat=2\):', patch.strip('\n'), content)

# Make Depth 3 use an even smaller pool (e.g., top 20 words instead of 200)
patch3 = '''
        # P50: Word Combinations (Depth 3)
        if self.config.max_combination_depth >= 3:
            small_pool = []
            for w in high_priority_base[:20]: # drastically reduce pool for depth 3
                small_pool.append(w.capitalize())
                if self.config.enable_leetspeak:
                    small_pool.extend(self.leet_mutations(w.capitalize()))
            small_pool = list(dict.fromkeys(small_pool))
            
            for combo in itertools.product(small_pool, repeat=3):
'''
content = re.sub(r'        # P50: Word Combinations \(Depth 3\)\n(?:.*\n){2,15}?            for combo in itertools\.product\(small_pool, repeat=3\):', patch3.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
