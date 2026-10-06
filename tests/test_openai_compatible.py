import json, unittest
from shortforge_providers import GenerationRequest, OpenAICompatibleProvider

class TestOpenAICompatibleProvider(unittest.TestCase):
    def test_request_and_parse(self):
        seen={}
        def transport(url,headers,payload):
            seen.update(url=url,headers=headers,payload=payload)
            variants=[{"id":"a","hook":"Immediate surprising hook","angle":"deadpan launch","payoff":"The tiny upgrade gets huge applause."},{"id":"b","hook":"Nobody expected this launch","angle":"benchmark parody","payoff":"The old machine wins the ridiculous benchmark."}]
            return {"choices":[{"message":{"content":json.dumps({"variants":variants})}}]}
        p=OpenAICompatibleProvider(base_url="http://local/v1",api_key="secret",model="test-model",transport=transport)
        out=p.generate_variants(GenerationRequest("Amiga launch",2))
        self.assertEqual(out["provider"],"openai-compatible")
        self.assertEqual(len(out["variants"]),2)
        self.assertEqual(seen["url"],"http://local/v1/chat/completions")
        self.assertEqual(seen["payload"]["model"],"test-model")
        self.assertEqual(seen["headers"]["Authorization"],"Bearer secret")
    def test_bad_count_rejected(self):
        def transport(*_): return {"choices":[{"message":{"content":"{\"variants\":[]}"}}]}
        with self.assertRaises(ValueError):
            OpenAICompatibleProvider(transport=transport).generate_variants(GenerationRequest("x",2))
    def test_malformed_response_rejected(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleProvider(transport=lambda *_: {"no":"choices"}).generate_variants(GenerationRequest("x",1))
if __name__=="__main__": unittest.main()
