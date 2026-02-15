Building a fair AI benchmark is harder than building the agents.

Most framework comparisons have a fatal flaw: uncontrolled variables. Different prompts. Different models. Different temperatures. You end up benchmarking your prompt engineering, not the framework.

So I controlled for everything.

Same pipeline across all 5 frameworks. Same prompts imported from a single shared module. Same tools. Same local model (Qwen 3 14B via Ollama). Temperature=0 for reproducibility. Every output scored by the same LLM judge on 5 dimensions.

The architecture enforces it. Framework implementations can import from shared/ but never from each other. The evaluation module can't import from shared/ or any framework — it only sees the output text. Clean dependency boundaries, no contamination.

The fun part? Dependency hell. CrewAI pins openai<1.84. MS Agent Framework requires openai>=1.99. They literally cannot coexist in the same environment. I ended up using uv's dependency groups to isolate them.

45 runs total. 5 frameworks x 3 companies x 3 iterations. Enough repetition to measure consistency, enough variety to test generalization.

If you're evaluating agent frameworks for your team, methodology matters as much as results. A sloppy comparison will mislead you faster than no comparison at all.

Full architecture breakdown and lessons learned: [link]

#Python #SoftwareEngineering #Benchmarking #AgentFrameworks
