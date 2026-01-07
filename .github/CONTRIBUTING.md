# Contributing to Roadmap Synthesis Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/roadmap-synth.git
   cd roadmap-synth
   ```

2. **Install dependencies**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Install test dependencies**
   ```bash
   uv pip install pytest pytest-cov pytest-mock pytest-timeout pytest-asyncio responses freezegun
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Running Tests

### Run All Tests
```bash
PYTHONPATH=$PWD uv run pytest tests/ -v
```

### Run with Coverage
```bash
PYTHONPATH=$PWD uv run pytest tests/ --cov=roadmap --cov=app --cov-report=html --cov-report=term-missing
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Slow tests
pytest tests/ -m slow

# Specific test file
pytest tests/test_utilities.py -v

# Specific test
pytest tests/test_utilities.py::TestCountTokens::test_count_tokens_normal_text -v
```

### View Coverage Report
```bash
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

## Writing Tests

### Test Organization

Tests are organized by component:
- `tests/test_utilities.py` - Utility functions
- `tests/test_chunking.py` - Chunking functions
- `tests/test_embeddings.py` - Embedding and vector search
- `tests/test_graph.py` - Graph operations
- `tests/test_retrieval.py` - Retrieval and authority
- `tests/test_integration.py` - End-to-end workflows

### Test Markers

Use pytest markers to categorize tests:
```python
@pytest.mark.unit
def test_something():
    """Unit test for isolated function."""
    pass

@pytest.mark.integration
def test_workflow():
    """Integration test for complete workflow."""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Test that takes longer to run."""
    pass

@pytest.mark.requires_api
def test_with_real_api():
    """Test that requires actual API calls (rarely used)."""
    pass
```

### Using Fixtures

Common fixtures are defined in `tests/conftest.py`:
```python
def test_with_mocks(mock_anthropic_client, mock_voyage_client, mock_lancedb):
    """Test using pre-configured mocks."""
    # mock_anthropic_client, mock_voyage_client, and mock_lancedb are available
    pass

def test_with_sample_data(sample_chunks, sample_embeddings):
    """Test using sample data."""
    # sample_chunks and sample_embeddings are available
    pass

def test_with_temp_dir(temp_dir):
    """Test that needs a temporary directory."""
    # temp_dir is a Path object to a clean temporary directory
    pass
```

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from roadmap import your_function

class TestYourFunction:
    """Tests for your_function."""

    @pytest.mark.unit
    def test_normal_case(self):
        """Test normal operation."""
        result = your_function("input")
        assert result == "expected"

    @pytest.mark.unit
    def test_edge_case(self):
        """Test edge case."""
        result = your_function("")
        assert result == []

    @pytest.mark.unit
    def test_with_mock(self, mock_anthropic_client):
        """Test with mocked API."""
        with patch("roadmap.anthropic.Anthropic", return_value=mock_anthropic_client):
            result = your_function("query")
            assert mock_anthropic_client.messages.create.called
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests locally**
   ```bash
   # Run all tests
   PYTHONPATH=$PWD uv run pytest tests/ -v

   # Check coverage
   PYTHONPATH=$PWD uv run pytest tests/ --cov=roadmap --cov-report=term-missing
   ```

4. **Ensure code quality**
   ```bash
   # Format code (if you have black installed)
   black . --line-length=100

   # Sort imports (if you have isort installed)
   isort .

   # Lint code (if you have ruff installed)
   ruff check .
   ```

5. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI tests pass
   - Request review from maintainers

## Code Style Guidelines

- **Python Version**: Python 3.11+
- **Line Length**: 100 characters (soft limit)
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for function signatures
- **Imports**: Group imports (stdlib, third-party, local)

### Example Function

```python
from typing import List, Dict, Optional

def process_chunks(
    chunks: List[Dict],
    top_k: int = 10,
    filter_fn: Optional[callable] = None
) -> List[Dict]:
    """
    Process and filter chunks based on criteria.

    Args:
        chunks: List of chunk dictionaries
        top_k: Maximum number of chunks to return
        filter_fn: Optional filter function

    Returns:
        Filtered and sorted list of chunks

    Raises:
        ValueError: If chunks is empty
    """
    if not chunks:
        raise ValueError("chunks cannot be empty")

    # Implementation
    return chunks[:top_k]
```

## Coverage Goals

- **Current Coverage**: ~18%
- **Target Coverage**: 70%
- **Minimum for PRs**: Don't decrease existing coverage

### Prioritize Testing For:
1. Core business logic
2. Data transformations
3. Error handling
4. Edge cases
5. Integration points

## Continuous Integration

All PRs must pass:
- ✅ All unit tests
- ✅ All integration tests
- ✅ Coverage threshold (>15%)
- ✅ Code linting (warnings allowed)

GitHub Actions will automatically:
- Run tests on Python 3.11, 3.12, and 3.13
- Generate coverage reports
- Post coverage comments on PRs
- Upload coverage to Codecov (if configured)

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: File a GitHub Issue
- **Feature Requests**: Open an issue with "enhancement" label

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

Thank you for contributing! 🎉
