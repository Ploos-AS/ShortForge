import unittest
from shortforge_captions import captions_to_srt
class TestCaptions(unittest.TestCase):
 def test_srt(self):
  m={"assets":[{"type":"caption","start":0.5,"end":2.25,"text":"Hello"}]}
  s=captions_to_srt(m)
  self.assertIn("00:00:00,500 --> 00:00:02,250",s); self.assertIn("Hello",s)
if __name__=="__main__": unittest.main()
