import unittest
from shortforge_cli import validate, score, rank_variants
P={"version":"0.1","kind":"ShortForgeProject","id":"x","title":"X","format":{"duration_target_seconds":10},"timeline":[{"start":0,"end":2,"functions":["hook"],"caption":"x"},{"start":2,"end":10,"functions":["payoff","loop"],"caption":"y"}]}
V={"version":"0.1","kind":"ShortForgeVariantSet","id":"v","source_project":"x","variants":[{"id":"complete","hook":"A clear hook that lands immediately.","angle":"A useful comic angle","payoff":"A clear payoff that resolves the setup."},{"id":"partial","hook":"Short hook","angle":"","payoff":""}]}
class TestShortForge(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(P),[])
    def test_score(self): self.assertEqual(score(P)["scores"]["hook"],100)
    def test_rank_is_deterministic(self):
        r=rank_variants(V); self.assertEqual(r["selected"],"complete"); self.assertEqual(r["ranking"][0]["rank"],1); self.assertGreater(r["ranking"][0]["scores"]["overall"],r["ranking"][1]["scores"]["overall"])
    def test_empty_set(self):
        r=rank_variants({"kind":"ShortForgeVariantSet","id":"empty","variants":[]}); self.assertIsNone(r["selected"])
if __name__=="__main__": unittest.main()
