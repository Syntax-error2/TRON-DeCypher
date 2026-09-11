with open('tests/unit/test_hash_recovery_vectors.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("TRON{Ne0n_C1rcu1t_D3f3nse_2026}", "CTK{Ne0n_C1rcu1t_D3f3nse_2026}")
content = content.replace("TRON{Cyb3r_D3f3ns3_2026}", "CTK{Cyb3r_D3f3ns3_2026}")
content = content.replace("CTF{N3tw0rk_F0r3ns1cs_2026}", "CTK{N3tw0rk_F0r3ns1cs_2026}")

with open('tests/unit/test_hash_recovery_vectors.py', 'w', encoding='utf-8') as f:
    f.write(content)
