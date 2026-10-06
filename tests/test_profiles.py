import unittest
from shortforge_profiles import get_profile, profile_info
from shortforge_providers import GenerationRequest, DeterministicProvider, OpenAICompatibleProvider

class TestProfiles(unittest.TestCase):
    def test_profile_catalog(self):
        info=profile_info()
        self.assertIn("retro",info); self.assertIn("educational",info); self.assertIn("comedy",info)
    def test_profile_recorded_in_output(self):
        out=DeterministicProvider().generate_variants(GenerationRequest("Amiga launch",2,None,"retro"))
        self.assertEqual(out["profile"],"retro")
    def test_profile_reaches_network_prompt(self):
        seen={}
        def transport(_url,_headers,payload):
            seen["prompt"]=payload["messages"][1]["content"]
            return {"choices":[{"message":{"content":'{"variants":[{"id":"x","hook":"Strong retro opening hook","angle":"authentic machine detail","payoff":"The old feature becomes the punchline."}]}'}}]}
        OpenAICompatibleProvider(transport=transport).generate_variants(GenerationRequest("Amiga",1,None,"retro"))
        self.assertIn("retro-computing enthusiasts",seen["prompt"])
        self.assertIn("avoid fake technical claims",seen["prompt"])
    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError): get_profile("missing")
if __name__=="__main__": unittest.main()
