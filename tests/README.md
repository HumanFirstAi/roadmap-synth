# Roadmap Synthesis Tool - Test Suite

This directory contains a comprehensive pytest test suite for the Roadmap Synthesis Tool.

## Current Coverage

- **roadmap.py**: 17% coverage (target: 70%)
- **Test Files**: 6 test modules with 100+ test cases
- **Test Types**: Unit tests, integration tests

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_utilities.py        # Tests for utility functions (count_tokens, cosine_similarity)
├── test_chunking.py         # Tests for chunking functions
├── test_embeddings.py       # Tests for embedding and vector search
├── test_graph.py            # Tests for UnifiedContextGraph
├── test_retrieval.py        # Tests for retrieval and authority functions
└── test_integration.py      # End-to-end integration tests
```

## Running Tests

### Install Test Dependencies

```bash
uv pip install pytest pytest-cov pytest-mock pytest-timeout pytest-asyncio responses freezegun
```

### Run All Tests

```bash
PYTHONPATH=/Users/jharris/roadmap-synth uv run pytest tests/ -v
```

### Run Specific Test File

```bash
PYTHONPATH=/Users/jharris/roadmap-synth uv run pytest tests/test_utilities.py -v
```

### Run Tests with Coverage

```bash
PYTHONPATH=/Users/jharris/roadmap-synth uv run pytest tests/ --cov=roadmap --cov=app --cov-report=html --cov-report=term-missing
```

### Run Only Unit Tests

```bash
PYTHONPATH=/Users/jharris/roadmap-synth uv run pytest tests/ -m unit -v
```

### Run Only Integration Tests

```bash
PYTHONPATH=/Users/jharris/roadmap-synth uv run pytest tests/ -m integration -v
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual functions in isolation with mocked dependencies:

- **Utility Functions**: Token counting, cosine similarity, API key validation
- **Chunking**: Quality scoring, key term extraction, time reference extraction
- **Embeddings**: Embedding generation, vector indexing, retrieval
- **Graph Operations**: Node addition, edge creation, graph persistence
- **Retrieval**: Authority-based ranking, balanced retrieval, contradiction detection

### Integration Tests (`@pytest.mark.integration`)

Test complete workflows with multiple components:

- **Document Ingestion**: Parse → Chunk → Embed → Index
- **Retrieval & Synthesis**: Query → Retrieve → Generate Response
- **Graph Synchronization**: Build and persist complete graph
- **Q&A Workflow**: Question parsing → Context retrieval → Answer generation

## Fixtures

### Path Fixtures

- `temp_dir`: Temporary directory for test files
- `test_data_dir`: Test data directory structure
- `test_materials_dir`: Test materials with lens structure
- `test_output_dir`: Test output directory

### Data Fixtures

- `sample_text`: Sample document text
- `sample_chunks`: Sample chunk data
- `sample_embeddings`: Sample 1024-dim embeddings
- `sample_chunk_with_embedding`: Complete chunk with vector
- `high_quality_chunk`: High quality chunk for testing
- `low_quality_chunk`: Low quality chunk for testing

### Mock API Fixtures

- `mock_anthropic_client`: Mocked Claude API client
- `mock_voyage_client`: Mocked Voyage AI client
- `mock_lancedb`: Mocked LanceDB database

### Utility Fixtures

- `mock_env_vars`: Mocked environment variables
- `sample_roadmap_text`: Sample generated roadmap
- `sample_questions_list`: Sample questions for testing

## Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| roadmap.py core functions | 17% | 80% |
| app.py utility functions | 0% | 60% |
| AgenticChunker class | - | 90% |
| UnifiedContextGraph class | - | 85% |
| Retrieval functions | - | 80% |
| Overall codebase | 17% | 70% |

## Known Issues

### Test Failures (To Be Fixed)

1. **validate_api_keys tests** - Not raising SystemExit as expected
2. **AUTHORITY_LEVELS tests** - Dictionary structure mismatch
3. **Some mock object issues** - Need better mock configuration
4. **Integration test assertions** - Some expectations need adjustment

### Next Steps to Reach 70% Coverage

1. **Fix Existing Test Failures** (1-2 days)
   - Update test assertions to match actual behavior
   - Fix mock configurations
   - Add missing test data

2. **Add Tests for Uncovered Functions** (3-4 days)
   - Document parsing functions
   - Agentic chunking (AgenticChunker class)
   - Synthesis functions (generate_roadmap, format_for_persona)
   - Q&A functions (parse_query, synthesize_answer)

3. **Add App.py Tests** (2-3 days)
   - Streamlit page functions
   - Q&A workflow
   - Question generation
   - Graph diagnostics

4. **Improve Integration Tests** (2-3 days)
   - Add more end-to-end workflows
   - Test error scenarios
   - Test data persistence

## Writing New Tests

### Example Unit Test

```python
import pytest
from roadmap import your_function

@pytest.mark.unit
def test_your_function_basic():
    """Test basic functionality."""
    result = your_function("input")
    assert result == "expected_output"

@pytest.mark.unit
def test_your_function_with_mock(mock_anthropic_client, mock_env_vars):
    """Test with mocked API."""
    result = your_function("input")
    assert result is not None
```

### Example Integration Test

```python
import pytest
from unittest.mock import patch

@pytest.mark.integration
def test_complete_workflow(mock_lancedb, mock_anthropic_client, mock_env_vars):
    """Test complete workflow."""
    from roadmap import some_function, another_function

    with patch("roadmap.init_db", return_value=mock_lancedb):
        # Setup
        result1 = some_function("input")

        # Execute
        result2 = another_function(result1)

        # Verify
        assert result2 is not None
```

## Continuous Integration

To integrate with CI/CD:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ --cov=roadmap --cov=app --cov-fail-under=70
```

## Troubleshooting

### ImportError: No module named 'roadmap'

Set PYTHONPATH:
```bash
PYTHONPATH=/path/to/roadmap-synth uv run pytest tests/
```

### Tests Timeout

Increase timeout in pytest.ini or use `-timeout=30` flag.

### Mock Not Working

Ensure you're patching the correct import path. Use `mocker.patch` with full module path.

### Coverage Not Accurate

Ensure all source files are in coverage scope by checking pytest.ini configuration.

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Aim for >80% coverage on new code
3. Include both unit and integration tests
4. Update this README with new test categories
5. Ensure all tests pass before submitting PR

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Cov Documentation](https://pytest-cov.readthedocs.io/)
- [Pytest-Mock Documentation](https://pytest-mock.readthedocs.io/)
- [Architecture Review](../ARCHITECTURE_REVIEW.md) - See Test Plan section
