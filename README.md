NEXUS: Autonomous Multi-Agent SDLC Assistant
NEXUS is an autonomous multi-agent AI system designed to solve complex software development life cycle (SDLC) problems. Instead of relying on a single chatbot, NEXUS decomposes a project brief into a dynamic Directed Acyclic Graph (DAG) and delegates tasks to a team of specialized AI agents.

Problem Addressed
The SDLC is highly complex. Non-technical founders and stakeholders often have raw ideas but lack the technical expertise to know if a project is feasible, how to architect it, or if it can be built within their budget. A single AI model struggles to reliably handle the entire lifecycle in one prompt without losing context.

Proposed Solution
NEXUS acts as an autonomous software engineering team. It reads a user's project brief, validates feasibility, generates architecture, writes code, reviews it for security flaws, and synthesizes a final report.

Key Features
Feasibility Gate: Analyzes budget and timeline. If a project is unrealistic, the pipeline halts autonomously to prevent wasted effort.

Self-Correction Loop: If the Reviewer agent detects a security flaw in the Coder's output, the Orchestrator forces the Coder to rewrite the code using the Reviewer's feedback.

Dynamic Routing: A Planner agent dynamically skips unnecessary phases based on the prompt complexity.

Human-in-the-Loop: Critical decisions require human sign-off in the interface.

Execution Visualization: Real-time trace of agent states (Running, Done, Skipped, Retry).

Architecture
Planner: Generates the task DAG.

Intake & Feasibility: Extracts constraints and determines GO / NO-GO.

Requirements & Methodology: Generates specs and selects the development model.

Architect: Designs the tech stack and module structure.

Coder & Reviewer: Writes code and performs strict security/correctness checks. Includes a retry loop.

Tester: Generates test cases and edge cases.

Writer: Synthesizes all agent JSON outputs into a final Markdown report.

Technology Stack
Frontend: Streamlit

Backend / Orchestration: Custom Python Engine (orchestrator.py) with Topological DAG Execution

LLM Provider: Google Gemini (Free Tier)

Local Setup Instructions
Clone the repository:
git clone https://github.com/kadamanchijatin-max/NEXUS.git

Install dependencies:
pip install -r requirements.txt

Create a .env file in the root directory and add your Gemini API key:
GEMINI_API_KEY=your_api_key_here

Run the application:
streamlit run app.py

Note
This project was built as a functional prototype for a 3-hour Agentic AI hackathon. The orchestration engine is built entirely from scratch without external agent frameworks like LangGraph or CrewAI.