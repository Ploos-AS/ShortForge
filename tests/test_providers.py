import unittest
from shortforge_providers import DeterministicProvider, GenerationRequest, get_provider

class TestProviders(unittest.TestCase):
    def test_deterministic_generation(self):
        p=DeterministicProvider()
        a=p.generate_variants(GenerationRequest("Amiga 9000",3,"sf-retro"))
        b=p.generate_variants(GenerationRequest("Amiga 9000",3,"sf-retro"))
        self.assertEqual(a,b)
        self.assertEqual(a["kind"],"ShortForgeVariantSet")
        self.assertEqual(len(a["variants"]),3)
        self.assertEqual(a["provider"],"deterministic")
    def test_count_guard(self):
        with self.assertRaises(ValueError):
            DeterministicProvider().generate_variants(GenerationRequest("x",0))
    def test_unknown_provider(self):
        with self.assertRaises(ValueError): get_provider("missing")
if __name__=="__main__": unittest.main()
