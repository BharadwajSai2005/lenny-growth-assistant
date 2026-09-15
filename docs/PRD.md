# Product Requirements Document (PRD)

## User and Problem
**User**: Product managers, growth engineers, marketers, and startup founders.
**Problem**: Users want to access the wealth of knowledge from Lenny's Podcast, but finding specific actionable growth advice across hours of transcripts is tedious and time-consuming. They also want to synthesize this advice into standardized formats like a "Ship 30 for 30" essay.

## Success Metrics
- **Performance**: <2s response time for Q&A queries.
- **Accuracy/Trust**: 100% of answers include source citations.
- **User Engagement**: >3 messages per session on average.

## Assumptions
1. Users have a basic understanding of growth concepts.
2. The podcast transcripts provide sufficient depth and accuracy to answer the queries.
3. Users are fine with a local LLM providing slightly lower quality compared to a cloud provider if they opt for privacy/cost savings.
4. An artifact viewer is the best way to display generated essays/HTML.
5. Simple keyword or vector matching is sufficient for accurate retrieval (RAG).
6. Demo environment does not require authentication or user accounts.

## Scope Choices
- **Included**: RAG chat over podcast transcripts, Ship 30 for 30 essay generation, Artifact viewer for Markdown/HTML, toggle between cloud (Anthropic) and local (Ollama) LLM.
- **Excluded**: User authentication, persistent user profiles across devices, deployment to production (cloud hosting), real-time transcription of new episodes.
- **Reasoning**: To keep the project scoped for a take-home assessment while demonstrating core RAG, full-stack, and agentic capabilities.

## User Flows

- **Flow 1: Ask a growth question** 
  User types a question -> System retrieves relevant transcript chunks -> System generates an answer grounded in transcripts -> UI displays answer with source citation badges.
- **Flow 2: Request Ship 30 for 30 essay** 
  User requests an essay -> System identifies the essay generation skill -> System synthesizes transcripts into essay format -> UI displays the essay in the artifact viewer (right panel).
- **Flow 3: Request HTML artifact** 
  User requests HTML output -> System generates HTML -> UI renders HTML securely in a sandboxed iframe artifact viewer.
- **Flow 4: Start new chat** 
  User clicks "New Chat" -> Current session clears -> A fresh session ID is generated and used for subsequent messages.

## Acceptance Criteria
1. The backend must provide a health check endpoint.
2. The UI must support standard text chat with the assistant.
3. The system must retrieve context from the PostgreSQL database using pgvector.
4. The system must cite sources for answers when context is used.
5. The system must correctly route "Ship 30 for 30" requests to the essay generation skill.
6. Generated artifacts (Markdown/HTML) must render in a separate right-side panel.
7. HTML artifacts must render in a sandboxed environment to prevent XSS.
8. The backend must allow toggling between Anthropic and Ollama via `.env`.
9. The frontend must display which LLM provider is currently active.
10. The UI must be responsive (desktop and mobile layouts).

## Risks and Trade-offs
- **Hallucination**: The LLM might invent facts. *Mitigation: Ground heavily in context, cite sources.*
- **Latency**: Cloud LLMs and embedding retrieval may be slow. *Mitigation: Monitor performance, stream responses where possible (future scope).*
- **Cost**: Anthropic API usage can get expensive. *Mitigation: Provide Ollama fallback.*
- **Local Model Quality**: Local `phi3` is small and might underperform Claude. *Trade-off accepted for cost/privacy benefits.*
- **Data Leakage**: System might leak prompts. *Trade-off accepted for demo purposes.*
- **Unsafe Artifacts**: Generated HTML could contain malicious scripts. *Mitigation: Sandboxed iframe without same-origin.*

## Implementation Plan
1. **Day 1**: Database schema, vector embedding pipeline, backend API scaffolding.
2. **Day 2**: Frontend UI structure, chat interface, basic LLM integration.
3. **Day 3**: RAG implementation, pgvector integration, source citations.
4. **Day 4**: Agent skills routing (Ship 30 for 30), artifact viewer.
5. **Day 5**: Local LLM (Ollama) fallback, testing, final documentation polish.

## Key Architectural Decisions

### LangChain over Anthropic Agent SDK
The agent layer uses LangChain (`langchain-core`, `langchain-anthropic`, `langchain-ollama`) instead of the Anthropic Claude Agent SDK. This was a deliberate decision because:
- **Provider agnosticism**: LangChain provides a unified interface for both Anthropic (cloud) and Ollama (local) through the same `BaseChatModel` abstraction. This makes the local/cloud toggle seamless — a single `get_llm()` factory returns the correct provider.
- **The Anthropic Agent SDK only supports Anthropic models**, making it impossible to fulfill the mandatory local LLM requirement without maintaining two completely separate agent implementations.
- **Trade-off accepted**: We lose access to Anthropic-specific agent features (tool use, computer use) but gain a cleaner architecture for the dual-provider requirement.

### Bundled Transcript Data
The specified data source ([ChatPRD/lennys-podcast-transcripts](https://github.com/ChatPRD/lennys-podcast-transcripts)) returns a 404 error. To ensure the demo works reliably:
- **Bundled data**: 11 realistic transcript-style chunks are embedded directly in `ingest.py`, covering product-market fit, growth metrics, retention, pricing, and team building.
- **GitHub fallback**: The ingestion script still attempts to fetch from GitHub first, falling back to bundled data only if the API fails.
- **Trade-off**: Less data coverage, but guaranteed demo reliability. In production, this would be replaced with a proper ingestion pipeline connected to a live data source.
