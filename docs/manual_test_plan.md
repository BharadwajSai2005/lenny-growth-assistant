# Manual Test Plan

Run through these test cases to verify the core functionality of the Lenny Growth Assistant.

## Test Cases

1. **Health check**
   - Action: Visit the `/health` endpoint in a browser or via `curl`.
   - Expected: Returns a 200 OK status with `{"status": "ok"}`.

2. **Send a question and get grounded answer with sources**
   - Action: Ask a question like "How do I measure product-market fit?"
   - Expected: Returns an accurate answer. The answer includes source citation badges linking to transcript chunks.

3. **Ask follow-up question in same session**
   - Action: Following test #2, ask "Can you elaborate on the second metric?"
   - Expected: The assistant understands the context from the previous message and answers appropriately.

4. **Click 'New Chat' and verify fresh session**
   - Action: Click the "New Chat" button.
   - Expected: The chat history clears. Sending a new message creates a new session (verify network request or lack of previous context).

5. **Ask for Ship 30 for 30 essay, verify artifact viewer opens**
   - Action: Type "Write a Ship 30 for 30 essay about onboarding."
   - Expected: The assistant replies, and the right-side artifact viewer panel automatically opens containing the formatted essay.

6. **Switch between Preview and Code tabs in artifact viewer**
   - Action: In the open artifact viewer, click "Code" then "Preview".
   - Expected: "Code" displays raw Markdown/HTML. "Preview" displays the rendered content correctly.

7. **Close artifact viewer**
   - Action: Click the close/X button on the artifact viewer.
   - Expected: The panel slides out and hides, returning the UI to standard chat mode.

8. **Test with Ollama running (local mode)**
   - Action: Set `LLM_PROVIDER=local` in `.env`, ensure Ollama is running, and send a message.
   - Expected: The assistant responds successfully using the local model.

9. **Test with Ollama stopped (graceful error)**
   - Action: Keep `LLM_PROVIDER=local`, but stop the Ollama service. Send a message.
   - Expected: The UI displays a graceful error message indicating the local provider is unreachable.

10. **Test responsive layout on mobile viewport**
    - Action: Shrink the browser width to <768px and trigger an artifact.
    - Expected: The artifact viewer overlays the chat in a stacked manner, rather than rendering side-by-side.

11. **Verify sources are displayed as badges**
    - Action: Look at an answer derived from RAG.
    - Expected: Citations are small, clickable, non-intrusive badges (e.g., `[1]`).

12. **Verify LLM provider badge shows correct provider**
    - Action: Check the top header of the chat interface.
    - Expected: The badge correctly indicates "Local (Ollama)" or "Cloud (Anthropic)" based on the current backend configuration.
