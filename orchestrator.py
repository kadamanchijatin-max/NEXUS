import json
import time
from agents import call_llm, AGENT_PROMPTS

PLANNER_PROMPT = """You are a Planner Agent. Read the user's project brief.
Decide which SDLC agents to run and in what order. Available agents:
intake, feasibility, requirements, methodology, architect, coder, reviewer, tester, writer.

Rules:
- Always start with intake.
- Always include feasibility next (gate).
- If feasibility verdict is NO-GO, stop after feasibility + writer.
- For a full build request: intake, feasibility, requirements, methodology, architect, coder, reviewer, tester, writer.
- For "review this code" type: intake, feasibility, reviewer, tester, writer.

Return JSON: {"tasks": [{"id": int, "agent": str, "deps": [int]}]}
Every task must have an id and list of dependency ids. Writer must be last."""


def planner(brief: str) -> list:
    raw = call_llm(PLANNER_PROMPT, brief)
    return json.loads(raw)["tasks"]


def topo_sort(tasks: list) -> list:
    remaining = {t["id"]: t for t in tasks}
    ordered, done = [], set()
    while remaining:
        progressed = False
        for tid in list(remaining.keys()):
            t = remaining[tid]
            if all(d in done for d in t["deps"]):
                ordered.append(t)
                done.add(tid)
                del remaining[tid]
                progressed = True
        if not progressed:
            raise ValueError("Cycle in task graph")
    return ordered


def run_agent(agent: str, brief: str, context: dict) -> dict:
    ctx_str = json.dumps(context, indent=2) if context else "{}"
    user_input = f"PROJECT BRIEF:\n{brief}\n\nUPSTREAM AGENT OUTPUTS:\n{ctx_str}"
    raw = call_llm(AGENT_PROMPTS[agent], user_input)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_output": raw}


def run_pipeline(brief: str, trace_callback=None):
    start_time = time.time()
    
    tasks = topo_sort(planner(brief))
    results = {}
    for t in tasks:
        agent = t["agent"]
        ctx = {str(d): results[d] for d in t["deps"] if d in results}
        if trace_callback:
            trace_callback("running", agent)
        out = run_agent(agent, brief, ctx)

        if agent == "feasibility" and out.get("verdict") == "NO-GO":
            results[t["id"]] = out
            if trace_callback:
                trace_callback("done", agent)
            break

        if agent == "reviewer" and out.get("verdict") == "FAIL":
            if trace_callback:
                trace_callback("retry", agent)
            coder_id = next((x["id"] for x in tasks if x["agent"] == "coder"), None)
            if coder_id and coder_id in results:
                feedback = json.dumps(out)
                retry_ctx = {"design": results.get(coder_id - 1, {}), "feedback": feedback}
                results[coder_id] = run_agent("coder", brief, retry_ctx)
                out = run_agent("reviewer", brief, {str(coder_id): results[coder_id]})

        results[t["id"]] = out
        if trace_callback:
            trace_callback("done", agent)

    writer_task = next((t for t in tasks if t["agent"] == "writer"), None)
    if writer_task and writer_task["id"] not in results:
        if trace_callback:
            trace_callback("running", "writer")
        all_ctx = {str(k): v for k, v in results.items()}
        results[writer_task["id"]] = run_agent("writer", brief, all_ctx)
        if trace_callback:
            trace_callback("done", "writer")

    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    
    return results, total_time