import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix P55
patch_p55 = '''
        # P55: Word Combinations (Depth 2)
        if self.config.max_combination_depth >= 2:
            pool = []
            for w in high_priority_base[:50]:
                pool.append(w.capitalize())
                pool.append(w.lower())
                if self.config.enable_leetspeak:
                    pool.extend(self.leet_mutations(w.capitalize()))
                    pool.extend(self.leet_mutations(w.lower()))
            pool = list(dict.fromkeys(pool))
'''
content = re.sub(r'        # P55: Word Combinations \(Depth 2\)\n(?:.*\n){2,15}?            pool = list\(dict\.fromkeys\(pool\)\)', patch_p55.strip('\n'), content)

# Fix P50
patch_p50 = '''
        # P50: Word Combinations (Depth 3)
        if self.config.max_combination_depth >= 3:
            small_pool = []
            for w in high_priority_base[:12]: 
                small_pool.append(w.capitalize())
                small_pool.append(w.lower())
                if self.config.enable_leetspeak:
                    small_pool.extend(self.leet_mutations(w.capitalize()))
            small_pool = list(dict.fromkeys(small_pool))
'''
content = re.sub(r'        # P50: Word Combinations \(Depth 3\)\n(?:.*\n){2,15}?            small_pool = list\(dict\.fromkeys\(small_pool\)\)', patch_p50.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
