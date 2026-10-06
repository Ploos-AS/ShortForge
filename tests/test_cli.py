import unittest
from shortforge_cli import validate, score

P={"version":"0.1","kind":"ShortForgeProject","id":"x","title":"X","format":{"duration_target_seconds":10},"timeline":[{"start":0,"end":2,"functions":["hook"],"caption":"x"},{"start":2,"end":10,"functions":["payoff","loop"],"caption":"y"}]}

class TestShortForge(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(P),[])
    def test_score(self): self.assertEqual(score(P)["scores"]["hook"],100)
if __name__=="__main__": unittest.main()
