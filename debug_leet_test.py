from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig()
g = CandidateGenerator(cfg)
print("neon ->", g.leet_mutations("neon"))
print("circuit ->", g.leet_mutations("circuit"))
print("defense ->", g.leet_mutations("defense"))
