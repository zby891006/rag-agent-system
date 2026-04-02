# from langchain_google_genai import ChatGoogleGenerativeAI
# import json
# from dotenv import load_dotenv

# load_dotenv()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0
# )

# def build_rqc_prompt(query: str, docs: list[dict]) -> str:

#         context = "\n\n".join(
#             f"[Doc {i+1}]\n{doc['text'][:300]}"
#             for i, doc in enumerate(docs)
#         )

#         return f"""
#     You are a retrieval quality evaluator.

#     User Question:
#     {query}

#     Retrieved Documents:
#     {context}

#     Evaluate:

#     1. Are the documents sufficient to answer the question?
#     2. Are they too general or lacking specific details?
#     3. Is key information missing?

#     Return JSON:

#     {{
#     "decision": "PASS or RETRY",
#     "confidence": 0-1,
#     "reason": "...",
#     "keywords": ["..."],
#     "suggest_hyde": true/false
#     }}
#     """

# def evaluate_rqc(query: str, docs: list, hyde_queries=None):

#     if not docs:
#         return {
#             "decision": "RETRY",
#             "confidence": 0.0,
#             "reason": "No documents retrieved",
#             "keywords": [],
#             "suggest_hyde": True
#         }

#     prompt = build_rqc_prompt(query, docs)

#     response = llm.invoke(prompt).content

#     try:
#         result = json.loads(response)
#     except:
#         # fallback
#         result = {
#             "decision": "RETRY",
#             "confidence": 0.3,
#             "reason": "LLM output parsing failed",
#             "keywords": [],
#             "suggest_hyde": True
#         }

#     return result

from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# =========================================
# 🔥 JSON 安全解析（關鍵）
# =========================================
def safe_json_parse(text: str):

    try:
        # 抓 JSON 區塊（避免 LLM 前後加廢話）
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass

    return None


# =========================================
# 🔥 Prompt（升級版：能抓「空話」）
# =========================================
def build_rqc_prompt(query: str, docs: list[dict]) -> str:

    context = "\n\n".join(
        f"[Doc {i+1}]\n{doc['text'][:300]}"
        for i, doc in enumerate(docs)
    )

    return f"""
You are a strict retrieval quality evaluator for ESG and financial reports.

User Question:
{query}

Retrieved Documents:
{context}

Evaluation Criteria:

1. Can the documents DIRECTLY answer the question?
2. Are they SPECIFIC (contain measurable details, methods, frameworks)?
3. Or are they GENERIC statements (e.g. "the company manages risks")?

IMPORTANT RULES:

- Generic ESG statements are NOT sufficient
- Vague descriptions = RETRY
- Must contain concrete details like:
  - numbers
  - standards (ISO, TCFD, etc.)
  - processes
  - metrics
  - methodologies

Output STRICT JSON ONLY (no explanation outside JSON):

{{
  "decision": "PASS or RETRY",
  "confidence": 0.0-1.0,
  "reason": "short explanation",
  "keywords": ["missing key terms"],
  "suggest_hyde": true or false
}}
"""


# RQC 主函數

def evaluate_rqc(query: str, docs: list, hyde_queries=None):

    if not docs:
        return {
            "decision": "RETRY",
            "confidence": 0.0,
            "reason": "No documents retrieved",
            "keywords": [],
            "suggest_hyde": True
        }

    prompt = build_rqc_prompt(query, docs)

    response = llm.invoke(prompt).content

  
    # 安全解析 JSON

    result = safe_json_parse(response)

    if result is None:
        return {
            "decision": "RETRY",
            "confidence": 0.3,
            "reason": "LLM output parsing failed",
            "keywords": [],
            "suggest_hyde": True
        }

   
    #  防呆（關鍵）

    result.setdefault("decision", "RETRY")
    result.setdefault("confidence", 0.5)
    result.setdefault("reason", "")
    result.setdefault("keywords", [])
    result.setdefault("suggest_hyde", True)

    # 保證型態正確
    if not isinstance(result["keywords"], list):
        result["keywords"] = []

    return result