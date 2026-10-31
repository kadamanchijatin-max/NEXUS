import os, json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def call_llm(system_prompt: str, user_input: str) -> str:
    resp = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"{system_prompt}\n\n---\nINPUT:\n{user_input}\n\nReturn ONLY valid JSON, no markdown fences."
    )
    text = resp.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()

AGENT_PROMPTS = {
    "intake": "You are an Intake Agent. Read the project brief. Return JSON: {\"summary\": str, \"constraints\": {\"budget\": str, \"time\": str, \"team\": str}, \"missing_info\": [str]}",
    "feasibility": "You are a Feasibility Agent. Given the summary and constraints, decide if the project is realistic. Return JSON: {\"verdict\": \"GO\"|\"NO-GO\"|\"CONDITIONAL\", \"risks\": [str], \"blockers\": [str], \"reasoning\": str}",
    "requirements": "You are a Requirements Agent. Return JSON: {\"functional\": [str], \"non_functional\": [str], \"out_of_scope\": [str], \"acceptance_criteria\": [str]}",
    "methodology": "You are a Methodology Agent. Choose the best SDLC methodology for this project from: Agile (Scrum/Kanban), Waterfall, Iterative, Spiral, Prototype, Evolutionary, V-Model, RAD. Base the choice on time, budget, team size, requirement stability, and risk. Return JSON: {\"methodology\": str, \"justification\": str, \"phases\": [str]}",
    "architect": "You are an Architect Agent. Tech stack MUST use Python (FastAPI/Flask). Return JSON: {\"tech_stack\": {str: str}, \"modules\": [str], \"folder_structure\": str, \"api_endpoints\": [str]}",
    "coder": "You are a Coder Agent. Write runnable Python code for ONE core module based on the design. Return JSON: {\"filename\": str, \"code\": str, \"explanation\": str}",
    "reviewer": "You are a strict Reviewer Agent. Review code against design and requirements. Check correctness AND security (hardcoded secrets, SQL injection, missing auth, weak hashing). Return JSON: {\"verdict\": \"PASS\"|\"FAIL\", \"correctness_issues\": [str], \"security_issues\": [{\"type\": str, \"location\": str, \"fix\": str}], \"severity\": \"low\"|\"med\"|\"high\"}",
    "tester": "You are a Tester Agent. Return JSON: {\"test_cases\": [{\"name\": str, \"input\": str, \"expected\": str}], \"edge_cases\": [str], \"test_plan\": str}",
    "writer": "You are a Writer Agent. Combine all upstream agent outputs into a clean markdown project report. Return EXACTLY a JSON object with one key: 'project_report'. The value must be the markdown string.",
}