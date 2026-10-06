import json, unittest
from shortforge_providers import GenerationRequest, OpenAIResponsesProvider, provider_info

class TestOpenAIResponsesProvider(unittest.TestCase):
    def test_request_parse_and_capabilities(self):
        seen={}
        def transport(url,headers,payload):
            seen.update(url=url,headers=headers,payload=payload)
            data={"variants":[{"id":"a","hook":"A strong opening hook","angle":"deadpan future launch","payoff":"The floppy drive gets a standing ovation."}]}
            return {"output":[{"type":"message","content":[{"type":"output_text","text":json.dumps(data)}]}]}
        out=OpenAIResponsesProvider(api_key="secret",model="test-model",transport=transport).generate_variants(GenerationRequest("Amiga launch",1))
        self.assertEqual(out["provider"],"openai-responses")
        self.assertEqual(seen["url"],"https://api.openai.com/v1/responses")
        self.assertEqual(seen["payload"]["model"],"test-model")
        self.assertEqual(seen["payload"]["text"]["format"]["type"],"json_object")
        self.assertEqual(provider_info()["openai-responses"]["protocol"],"responses")
    def test_malformed_output_rejected(self):
        with self.assertRaises(ValueError):
            OpenAIResponsesProvider(transport=lambda *_: {"output":[]}).generate_variants(GenerationRequest("x",1))
if __name__=="__main__": unittest.main()
