import unittest
from shortforge_storyboard import ExpansionRequest, expand_variant

V={"id":"v1","hook":"Commodore just announced the impossible.","angle":"A deadpan launch of a tiny retro upgrade.","payoff":"The floppy drive gets the biggest applause."}
class TestStoryboard(unittest.TestCase):
    def test_expand_contract(self):
        out=expand_variant(ExpansionRequest("Amiga 9000",V,"retro"))
        self.assertEqual(out["kind"],"ShortForgeStoryboard")
        self.assertEqual(out["format"],"9:16")
        self.assertEqual(out["duration_seconds"],20)
        self.assertEqual([b["purpose"] for b in out["beats"]],["hook","develop","payoff"])
        self.assertEqual(out["beats"][-1]["end"],20)
        self.assertTrue(out["loop"]["enabled"])
        self.assertTrue(all(b["asset_prompt"] for b in out["beats"]))
    def test_educational_duration(self):
        out=expand_variant(ExpansionRequest("Explain RAM",V,"educational"))
        self.assertEqual(out["duration_seconds"],30)
    def test_bad_variant(self):
        with self.assertRaises(ValueError): expand_variant(ExpansionRequest("x",{"hook":"x"}))
if __name__=="__main__": unittest.main()
