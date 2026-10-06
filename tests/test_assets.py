import unittest
from shortforge_assets import compile_manifest, MEDIA_PROVIDER_CONTRACT
SB={"kind":"ShortForgeStoryboard","profile":"retro","format":"9:16","duration_seconds":20,"beats":[{"start":0,"end":6,"voiceover":"Hook","caption":"Hook","asset_prompt":"Opening"},{"start":6,"end":12,"voiceover":"Develop","caption":"Develop","asset_prompt":"Middle"},{"start":12,"end":20,"voiceover":"Payoff","caption":"Payoff","asset_prompt":"End"}]}
class TestAssets(unittest.TestCase):
    def test_manifest(self):
        m=compile_manifest(SB)
        self.assertEqual(m["kind"],"ShortForgeAssetManifest")
        self.assertEqual(len(m["assets"]),11)
        self.assertEqual(m["assets"][0]["id"],"beat-01-visual")
        self.assertEqual(m["assets"][0]["constraints"]["aspect_ratio"],"9:16")
        self.assertIn("visual",MEDIA_PROVIDER_CONTRACT)
        self.assertIn("voice",MEDIA_PROVIDER_CONTRACT)
    def test_ids_are_deterministic(self):
        self.assertEqual(compile_manifest(SB),compile_manifest(SB))
    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError): compile_manifest({"kind":"Other"})
if __name__=="__main__": unittest.main()
