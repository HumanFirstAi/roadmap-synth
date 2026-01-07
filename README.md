# Roadmap Synthesis Tool

[![Tests](https://github.com/yourusername/roadmap-synth/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/roadmap-synth/actions/workflows/test.yml)
[![Coverage](https://codecov.io/gh/yourusername/roadmap-synth/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/roadmap-synth)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI tool that synthesizes diverse strategic documents into persona-specific product roadmaps using semantic search and Claude AI.

## Features

- **Multi-format document ingestion**: PDF, DOCX, PPTX, XLSX, CSV, MD, TXT, JSON
- **Lens-based authority tagging**: Organize sources by authority level (your-voice, team-structured, etc.)
- **Semantic search**: Vector-based retrieval using Voyage AI embeddings
- **AI synthesis**: Generate coherent roadmaps using Claude Opus 4.5
- **Persona formatting**: Output tailored for executives, product managers, or engineers
- **Q&A interface**: Ask questions about your indexed materials
- **Web interface**: User-friendly Streamlit app for all features

## Web Interface (Recommended)

Launch the Streamlit web app for a user-friendly interface:

```bash
uv run streamlit run app.py
```

Open http://localhost:8501 in your browser.

**Features:**
- 📊 **Dashboard**: View index statistics and status
- 📥 **Ingest Materials**: Upload files or ingest from folders
- 🔧 **Generate Roadmap**: Create master roadmap with one click
- 👥 **Format by Persona**: Transform for executive/product/engineering audiences
- ❓ **Ask Questions**: Chat-style Q&A over your materials
- ⚙️ **Settings**: Manage API keys and configuration

## CLI Interface

For command-line usage, see the commands below.

## Quick Start

### 1. Setup

```bash
# Clone or navigate to project directory
cd roadmap-synth

# Install dependencies (already done by uv)
# uv add "typer[all]" anthropic voyageai lancedb "unstructured[all-docs]" python-dotenv tiktoken pyarrow

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and VOYAGE_API_KEY
```

### 2. Get API Keys

- **Anthropic API**: https://console.anthropic.com/
- **Voyage AI API**: https://dash.voyageai.com/

Add them to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
VOYAGE_API_KEY=pa-...
```

### 3. Add Your Documents

Organize documents by lens (authority level) in `materials/`:

```
materials/
├── your-voice/              # Your strategic vision (highest authority)
├── team-structured/         # Official team documents
├── team-conversational/     # Meeting notes, discussions
├── business-framework/      # OKRs, business strategy
├── engineering/             # Technical docs (veto power on feasibility)
└── external-analyst/        # Market research (lowest authority)
```

### 4. Ingest Documents

```bash
# Ingest from a lens directory
uv run python roadmap.py ingest ./materials/your-voice/ --lens your-voice
uv run python roadmap.py ingest ./materials/team-structured/ --lens team-structured

# Or ingest a single file
uv run python roadmap.py ingest ./materials/your-voice/strategy-2026.pdf --lens your-voice
```

### 5. Generate Roadmap

```bash
# Generate master roadmap
uv run python roadmap.py generate

# Format for specific personas
uv run python roadmap.py format executive
uv run python roadmap.py format product
uv run python roadmap.py format engineering
```

### 6. Ask Questions

```bash
# Query your materials
uv run python roadmap.py ask "What are the dependencies between Catalog and Acquisition?"
```

## Lens Authority Hierarchy

When sources conflict, the tool respects this priority:

1. **your-voice** (HIGHEST) - Your strategic vision
2. **team-conversational** - Real priorities from discussions
3. **team-structured** - Formal team documentation
4. **business-framework** - Business strategy, OKRs
5. **engineering** - Technical feasibility (**veto power**)
6. **external-analyst** (LOWEST) - Market validation

**Special Rule**: Engineering can veto any item as infeasible, overriding all other sources.

## Commands

### `ingest`
Ingest documents with specified lens.

```bash
uv run python roadmap.py ingest <path> --lens <lens>

# Examples:
uv run python roadmap.py ingest ./materials/your-voice/ --lens your-voice
uv run python roadmap.py ingest ./strategy.pdf --lens your-voice
```

**Lens options**: `your-voice`, `team-structured`, `team-conversational`, `business-framework`, `engineering`, `external-analyst`

### `generate`
Generate master roadmap from indexed materials.

```bash
uv run python roadmap.py generate
```

Output: `output/master_roadmap.md`

### `format`
Format roadmap for specific persona.

```bash
uv run python roadmap.py format <persona>

# Examples:
uv run python roadmap.py format executive   # High-level strategic view
uv run python roadmap.py format product     # Detailed priorities & metrics
uv run python roadmap.py format engineering # Technical implementation details
```

Output: `output/{persona}_roadmap.md`

### `ask`
Ask questions about your indexed materials.

```bash
uv run python roadmap.py ask "<question>"

# Examples:
uv run python roadmap.py ask "What are the key dependencies for the CPQ roadmap?"
uv run python roadmap.py ask "What engineering concerns were raised about the AI features?"
```

## Project Structure

```
roadmap-synth/
├── roadmap.py               # Main CLI script
├── prompts/
│   ├── synthesis.md         # Master synthesis framework
│   └── personas/
│       ├── executive.md     # Executive formatting prompt
│       ├── product.md       # Product manager formatting prompt
│       └── engineering.md   # Engineering formatting prompt
├── materials/               # Your source documents (organized by lens)
├── output/                  # Generated roadmaps
├── data/                    # LanceDB vector database
└── .env                     # API keys (not committed)
```

## Persona Outputs

### Executive
- **Length**: 500-800 words (1 page)
- **Focus**: Strategic narrative, investment themes, business impact, risks
- **Timeline**: Quarterly
- **Tone**: High-level, business-focused, confident but realistic

### Product
- **Length**: 2-3 pages
- **Focus**: Feature details, user value, success metrics, dependencies
- **Timeline**: Monthly/quarterly with milestones
- **Tone**: Practical, actionable, metric-driven

### Engineering
- **Length**: 5-10 pages
- **Focus**: Technical approach, architecture, components, testing, infrastructure
- **Timeline**: Sprint/milestone-based
- **Tone**: Technically precise, detail-oriented, pragmatic

## Troubleshooting

### SSL Certificate Issues (macOS)

If you see SSL certificate errors:

```bash
# Run the Python certificate installer
/Applications/Python\ 3.1*/Install\ Certificates.command
```

### API Key Errors

If you see "API key not set" errors:
1. Check `.env` file exists in project root
2. Verify keys are set correctly (no quotes needed)
3. Try running with explicit path: `ANTHROPIC_API_KEY=sk-... uv run python roadmap.py ...`

### No Documents Found

If retrieval returns no results:
1. Run `ingest` to index your documents first
2. Check that `data/` directory has content
3. Verify files were parsed successfully (check console output during ingest)

### Empty Output

If generated roadmaps are empty or low-quality:
1. Ensure you have enough source materials (at least 3-5 documents)
2. Check that documents contain meaningful text (not just images/scans)
3. Try ingesting documents with different lenses
4. Review `prompts/synthesis.md` and adjust if needed

## How It Works

1. **Ingestion**: Documents are parsed using the `unstructured` library
2. **Chunking**: Text is split into ~512 token chunks with 50 token overlap
3. **Embedding**: Chunks are embedded using Voyage AI (voyage-3-large model)
4. **Indexing**: Embeddings are stored in LanceDB (local vector database)
5. **Retrieval**: Queries are embedded and similar chunks are retrieved
6. **Synthesis**: Claude Opus 4.5 generates roadmaps respecting lens hierarchy
7. **Formatting**: Roadmaps are reformatted for specific personas

## Customization

### Adjust Chunking

Edit `roadmap.py` constants:
```python
CHUNK_SIZE = 512      # Tokens per chunk
CHUNK_OVERLAP = 50    # Overlap between chunks
TOP_K = 20            # Number of chunks to retrieve
```

### Modify Prompts

Edit files in `prompts/` directory:
- `synthesis.md` - Master synthesis framework and lens hierarchy
- `personas/executive.md` - Executive formatting rules
- `personas/product.md` - Product manager formatting rules
- `personas/engineering.md` - Engineering formatting rules

### Change Models

Edit `roadmap.py`:
```python
# Voyage AI model (default: voyage-3-large)
vo.embed(..., model="voyage-3-large", ...)

# Claude model (default: claude-opus-4.5-20251101)
client.messages.create(model="claude-opus-4.5-20251101", ...)
```

## Cost Estimates

Approximate costs per operation:

- **Ingestion** (per 100 pages): ~$0.10-0.50 (Voyage AI embeddings)
- **Roadmap generation**: ~$1-3 (Claude Opus 4.5)
- **Persona formatting**: ~$0.50-1.50 per persona
- **Q&A query**: ~$0.10-0.50 per question

Use Claude Haiku for cheaper Q&A if needed.

## Testing

The project includes a comprehensive test suite with 107 tests covering core functionality.

### Running Tests

```bash
# Run all tests
PYTHONPATH=$PWD uv run pytest tests/ -v

# Run with coverage report
PYTHONPATH=$PWD uv run pytest tests/ --cov=roadmap --cov=app --cov-report=html --cov-report=term-missing

# Run unit tests only (fast)
pytest tests/ -m unit

# Run integration tests
pytest tests/ -m integration

# Run specific test file
pytest tests/test_utilities.py -v
```

### View Coverage Report

```bash
open htmlcov/index.html  # View detailed HTML coverage report
```

### Test Organization

- `tests/test_utilities.py` - Utility functions (count_tokens, cosine_similarity, API validation)
- `tests/test_chunking.py` - Chunking functions (quality scoring, key terms, time refs)
- `tests/test_embeddings.py` - Embedding generation and vector search
- `tests/test_graph.py` - UnifiedContextGraph operations
- `tests/test_retrieval.py` - Authority-based retrieval and ranking
- `tests/test_integration.py` - End-to-end workflow tests

### Coverage Status

Current coverage: ~18% (target: 70%)

**Well-tested components:**
- ✅ Utility functions (~90%)
- ✅ Chunking functions (~25%)
- ✅ Embeddings (~20%)
- ✅ Graph operations (~22%)

### Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed guidelines on writing tests and submitting pull requests.

## Development

```bash
# Run directly
uv run python roadmap.py --help

# Install in development mode
uv pip install -e .

# Install test dependencies
uv pip install pytest pytest-cov pytest-mock pytest-timeout pytest-asyncio responses freezegun

# Format code
uv run ruff format roadmap.py

# Type check
uv run mypy roadmap.py
```

### Continuous Integration

GitHub Actions automatically runs tests on:
- ✅ Every push to main/develop branches
- ✅ Every pull request
- ✅ Python 3.11, 3.12, and 3.13
- ✅ Coverage reporting and threshold checks

## License

MIT License - use freely for personal or commercial projects.

## Credits

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Anthropic Claude](https://www.anthropic.com/) - LLM synthesis
- [Voyage AI](https://www.voyageai.com/) - Embeddings
- [LanceDB](https://lancedb.com/) - Vector database
- [unstructured](https://unstructured.io/) - Document parsing
