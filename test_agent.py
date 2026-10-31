from agents import call_llm, AGENT_PROMPTS

brief = "Build a bookstore REST API with login and CRUD for books. Deadline 3 weeks, 2 devs, tight budget."
print(call_llm(AGENT_PROMPTS["intake"], brief))