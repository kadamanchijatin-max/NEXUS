from orchestrator import run_pipeline

brief = "Build a bookstore REST API with login and CRUD for books. Deadline 3 weeks, 2 devs, tight budget."

def trace(status, agent):
    print(f"[{status.upper()}] {agent}")

results = run_pipeline(brief, trace_callback=trace)
print("\n=== FINAL WRITER OUTPUT ===")
for tid, out in results.items():
    print(f"\n--- task {tid} ---")
    print(str(out)[:300])