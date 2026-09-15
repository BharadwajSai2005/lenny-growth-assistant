# Design Document

## UI/UX Principles
- **Clarity**: Keep the interface clean and focused on the conversation.
- **Side-by-side context**: When complex artifacts (essays, code) are generated, display them alongside the chat rather than inline, preventing chat disruption.
- **Progressive disclosure**: Show sources as small badges that can be hovered/clicked for more details, keeping the main response readable.

## Information Architecture
- **Chat Panel (Left/Main)**: 
  - Header: Application title, current LLM Provider badge, and a "New Chat" button.
  - Message History: Scrollable list of user and assistant messages.
  - Input Area: Text field and send button.
- **Artifact Panel (Right)**:
  - Appears conditionally when an artifact is returned by the backend.
  - Tabs: Toggle between "Preview" (rendered output) and "Code" (raw markdown/HTML).
  - Controls: Close button to dismiss the panel.

## Key Interaction States
- **Empty State**: Displays a welcome message and 2-3 usage hints or suggested queries to get started.
- **Loading State**: Animated pulsating dots in the chat bubble while waiting for the LLM response.
- **Error State**: Inline red error messages within the chat, offering recovery guidance (e.g., "Ollama is not running, please start it.").
- **Artifact Generated**: The right panel slides in. The chat bubble includes a brief text response and a button/indicator that an artifact was generated.

## Responsive Behavior
- **Desktop (>768px)**: Uses a side-by-side layout (split screen). Chat on the left, Artifact on the right.
- **Mobile (<=768px)**: Uses a stacked layout. The artifact viewer acts as a full-screen or large modal overlay that slides up over the chat.

## Accessibility Considerations
- **ARIA labels**: Applied to icon buttons (like "Send" or "Close") for screen readers.
- **Keyboard navigation**: Support for pressing `Enter` to send messages (and `Shift+Enter` for newlines). Tab navigation through interactive elements.
- **Color contrast**: The dark theme utilizes light gray/white text on dark backgrounds, satisfying WCAG AA contrast ratios.
- **Semantic HTML**: Proper use of `<main>`, `<aside>`, `<header>`, and list elements for messages.

## Design Decisions
- **Dark Theme**: Chosen specifically to appeal to a developer and PM-heavy audience.
- **Source Citations**: Rendered as small clickable badges `[1]`, `[2]` at the end of sentences rather than dumping full URLs, optimizing for scannability.
- **Skill Badge**: When a specific skill (e.g., "Ship 30 for 30") is activated, a small badge appears in the assistant's message header to clarify how the response was processed.
