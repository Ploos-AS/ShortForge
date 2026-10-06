import tempfile,time,unittest
from pathlib import Path
from shortforge_staging import FilesystemStager,HTTPSURLStager,validate_staged_url

class TestStaging(unittest.TestCase):
 def test_filesystem_staging_preserves_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); src=root/"short.mp4"; src.write_bytes(b"video")
   result=FilesystemStager().stage(src,destination=root/"stage"/"short.mp4")
   self.assertEqual(result["bytes"],5); self.assertIsNone(result["url"])
   self.assertEqual((root/"stage"/"short.mp4").read_bytes(),b"video")
   self.assertEqual(len(result["sha256"]),64)
 def test_https_url_adapter(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"short.mp4"; src.write_bytes(b"video")
   result=HTTPSURLStager().stage(src,url="https://cdn.example.test/token/video.mp4",expires_at=time.time()+300)
   self.assertTrue(result["temporary"]); self.assertEqual(result["url"],"https://cdn.example.test/token/video.mp4")
 def test_rejects_non_https_and_expired(self):
  with tempfile.TemporaryDirectory() as d:
   src=Path(d)/"short.mp4"; src.write_bytes(b"x")
   with self.assertRaises(ValueError): HTTPSURLStager().stage(src,url="http://example.test/a.mp4")
   with self.assertRaisesRegex(ValueError,"expired"): HTTPSURLStager().stage(src,url="https://example.test/a.mp4",expires_at=time.time()-1)

if __name__=="__main__": unittest.main()
