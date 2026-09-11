from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig()
g = CandidateGenerator(cfg)
print(g.leet_mutations("neon"))
