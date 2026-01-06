# Streamlit App for Roadmap Synth

## Objective

Build a simple Streamlit web interface to manage the Roadmap Synthesis tool. The app should wrap the existing `roadmap.py` CLI functionality in a user-friendly UI.

---

## Core Requirements

### 1. Single File Implementation
- Create `app.py` in the project root
- Import and reuse functions from `roadmap.py` where possible
- Add streamlit to dependencies: `uv add streamlit`

### 2. Page Structure

Use Streamlit's sidebar navigation with these pages:

```
📊 Dashboard (home)
📥 Ingest Materials
🔧 Generate Roadmap
👥 Format by Persona
❓ Ask Questions
⚙️ Settings
```

---

## Page Specifications

### Page 1: Dashboard
**Purpose:** Overview of current state

**Display:**
- Index statistics (total chunks, tokens, sources)
- Breakdown by lens (bar chart or table)
- Breakdown by source type
- List of recent ingested sources (last 10)
- Quick status: "Ready to generate" or "No materials indexed"

**Actions:**
- Button: "Clear Index" (with confirmation)

---

### Page 2: Ingest Materials
**Purpose:** Upload and ingest documents

**UI Elements:**
- File uploader (accept: PDF, DOCX, PPTX, XLSX, CSV, TXT, MD)
- Dropdown: Select lens
  - your-voice
  - team-structured
  - team-conversational
  - business-framework
  - engineering
  - external-analyst
- Checkbox: "Process recursively" (for folders, default: True)
- Button: "Ingest"

**Behavior:**
- On upload, save file to appropriate `materials/<lens>/` folder
- Run ingestion process
- Show progress spinner
- Display success/error message
- Update dashboard stats

**Alternative Input:**
- Text input for folder path (for ingesting existing folders)
- Button: "Ingest from Path"

---

### Page 3: Generate Roadmap
**Purpose:** Generate master roadmap

**UI Elements:**
- Text area: "Additional Context" (optional, e.g., "Focus on Q2 priorities")
- Checkbox: "Use Opus for final quality" (default: False)
- Button: "Generate Master Roadmap"

**Behavior:**
- Show progress spinner during generation
- Display generated roadmap in markdown
- Provide download button for `.md` file
- Save to `output/master-roadmap.md`

**Display:**
- Preview of existing master roadmap (if exists)
- Last generated timestamp

---

### Page 4: Format by Persona
**Purpose:** Transform master roadmap for specific audiences

**UI Elements:**
- Radio buttons: Select persona
  - Executive
  - Product
  - Engineering
- Button: "Generate Persona Roadmap"

**Behavior:**
- Requires master roadmap to exist (show warning if not)
- Show progress spinner
- Display formatted roadmap in markdown
- Provide download button
- Save to `output/<persona>-roadmap.md`

**Display:**
- Side-by-side: Master roadmap (collapsed) | Persona roadmap
- Or tabs: Master | Executive | Product | Engineering

---

### Page 5: Ask Questions
**Purpose:** Q&A over indexed materials and roadmap

**UI Elements:**
- Text input: "Ask a question..."
- Button: "Ask" (or Enter to submit)
- Chat history display (session state)

**Behavior:**
- Query indexed materials
- Display answer with source attribution
- Maintain conversation history in session
- Button: "Clear History"

**Display:**
- Chat-style interface
- Sources cited below each answer

---

### Page 6: Settings
**Purpose:** Configuration and API key management

**UI Elements:**
- Text inputs (password type):
  - Anthropic API Key
  - Voyage AI API Key
- Display current config (masked keys)
- Button: "Save Settings" (write to `.env`)
- Button: "Test Connection" (verify API keys work)

**Display:**
- Current model settings
- Chunk size / overlap settings
- Path configurations

---

## Technical Implementation

### Session State
Use `st.session_state` for:
- Chat history
- Current index stats (cache)
- Generated roadmaps (avoid regenerating)

### Caching
Use `@st.cache_data` or `@st.cache_resource` for:
- Index statistics
- Loaded roadmaps
- Embedder/store initialization

### Error Handling
- Wrap all operations in try/except
- Display user-friendly error messages
- Log errors for debugging

### File Structure
```
roadmap-synth/
├── roadmap.py          # Existing CLI tool
├── app.py              # New Streamlit app
├── .env                # API keys
├── materials/          # Source documents
├── output/             # Generated roadmaps
├── data/               # Vector database
└── prompts/            # Prompt templates
```

---

## UI/UX Guidelines

### Style
- Clean, minimal interface
- Use Streamlit's native components
- Consistent spacing and layout
- Mobile-friendly (Streamlit handles this)

### Feedback
- Always show spinners for long operations
- Success/error messages with `st.success()` / `st.error()`
- Progress indicators where possible

### Navigation
- Sidebar always visible
- Current page highlighted
- Logical flow: Ingest → Generate → Format → Ask

---

## Launch Command

```bash
uv run streamlit run app.py
```

Add to README:
```markdown
## Web Interface

Launch the Streamlit app:
```bash
uv run streamlit run app.py
```

Open http://localhost:8501 in your browser.
```

---

## Dependencies to Add

```bash
uv add streamlit
```

---

## Implementation Order

1. Basic app structure with sidebar navigation
2. Dashboard page (read-only, displays stats)
3. Settings page (API key management)
4. Ingest page (file upload + ingestion)
5. Generate page (master roadmap)
6. Format page (persona formatting)
7. Ask page (Q&A interface)

---

## Example Code Skeleton

```python
import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Roadmap Synth",
    page_icon="🗺️",
    layout="wide"
)

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📥 Ingest", "🔧 Generate", "👥 Format", "❓ Ask", "⚙️ Settings"]
)

# Route to pages
if page == "📊 Dashboard":
    st.title("Dashboard")
    # ... dashboard code
    
elif page == "📥 Ingest":
    st.title("Ingest Materials")
    # ... ingest code

# ... etc
```

---

## Success Criteria

- [ ] All 6 pages functional
- [ ] Can ingest files via upload
- [ ] Can generate master roadmap
- [ ] Can format for all 3 personas
- [ ] Can ask questions and get answers
- [ ] Settings persist to `.env`
- [ ] Error handling throughout
- [ ] Clean, intuitive UI
