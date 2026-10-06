import unittest
from unittest.mock import patch
from shortforge_qualify import qualify_video
DATA={"streams":[{"codec_type":"video","codec_name":"h264","width":1080,"height":1920,"avg_frame_rate":"30/1"},{"codec_type":"audio","codec_name":"aac"}],"format":{"duration":"2.000"}}
class TestQualify(unittest.TestCase):
    @patch("shortforge_qualify.probe_video",return_value=DATA)
    def test_pass(self,_):
        self.assertTrue(qualify_video("x.mp4",2)["passed"])
    @patch("shortforge_qualify.probe_video",return_value={"streams":[],"format":{"duration":"1"}})
    def test_fail(self,_):
        q=qualify_video("x.mp4",2); self.assertFalse(q["passed"]); self.assertIn("missing video stream",q["errors"])
if __name__=="__main__": unittest.main()
