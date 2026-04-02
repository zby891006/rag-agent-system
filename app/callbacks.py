from langchain_core.callbacks import BaseCallbackHandler

class DebugHandler(BaseCallbackHandler):

    def on_tool_start(self, serialized, input_str, **kwargs):
        print("\n[TOOL START]")
        print("Tool:", serialized.get("name"))
        print("Input:", input_str)

    def on_tool_end(self, output, **kwargs):
        print("[TOOL END]")
        print("Output:", output)

    def on_llm_start(self, serialized, prompts, **kwargs):
        print("\n[LLM START]")

    def on_llm_end(self, response, **kwargs):
        print("[LLM END]")