import unittest
from shortforge_production import get_production_profile, PRODUCTION_PROFILES
class TestProductionProfiles(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(set(PRODUCTION_PROFILES),{"generic-vertical","tiktok","reels","shorts"})
    def test_shorts_limit(self):
        self.assertEqual(get_production_profile("shorts")["max_duration"],180)
    def test_vertical_defaults(self):
        for p in PRODUCTION_PROFILES.values():
            self.assertEqual((p["width"],p["height"]),(1080,1920)); self.assertEqual(p["fps"],30)
    def test_unknown(self):
        with self.assertRaises(ValueError): get_production_profile("nope")
if __name__=="__main__": unittest.main()
