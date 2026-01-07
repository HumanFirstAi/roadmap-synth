"""
Pytest configuration and shared fixtures for roadmap-synth tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
from unittest.mock import Mock, MagicMock
import json


# ========== PATH FIXTURES ==========

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_data_dir(temp_dir):
    """Create test data directory structure."""
    data_dir = temp_dir / "data"
    data_dir.mkdir()
    (data_dir / "unified_graph").mkdir()
    (data_dir / "questions").mkdir()
    return data_dir


@pytest.fixture
def test_materials_dir(temp_dir):
    """Create test materials directory with lens structure."""
    materials_dir = temp_dir / "materials"
    for lens in ["your-voice", "team-structured", "team-conversational",
                 "sales-conversational", "business-framework", "engineering",
                 "external-analyst"]:
        (materials_dir / lens).mkdir(parents=True)
    return materials_dir


@pytest.fixture
def test_output_dir(temp_dir):
    """Create test output directory."""
    output_dir = temp_dir / "output"
    output_dir.mkdir()
    return output_dir


# ========== SAMPLE DATA FIXTURES ==========

@pytest.fixture
def sample_text():
    """Sample document text for testing."""
    return """
# Product Roadmap 2026

## Q1 Goals
We need to focus on three key areas:
1. Improve CPQ configuration experience
2. Enhance catalog search capabilities
3. Build better pricing workflows

## Technical Requirements
The engineering team has identified several dependencies:
- API modernization required before Q2
- Database migration scheduled for March
- New microservices architecture

## Customer Feedback
Recent surveys show customers want:
- Faster quote generation (mentioned by 85% of respondents)
- More flexible pricing rules
- Better integration with CRM systems
"""


@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    return [
        {
            "id": "test_doc_0",
            "content": "We need to focus on improving CPQ configuration experience and catalog search.",
            "lens": "team-structured",
            "source_file": "test_doc.md",
            "chunk_index": 0,
            "token_count": 15,
        },
        {
            "id": "test_doc_1",
            "content": "Engineering team requires API modernization before Q2 launch.",
            "lens": "engineering",
            "source_file": "test_doc.md",
            "chunk_index": 1,
            "token_count": 12,
        },
        {
            "id": "test_doc_2",
            "content": "Customers want faster quote generation and better CRM integration.",
            "lens": "your-voice",
            "source_file": "test_doc.md",
            "chunk_index": 2,
            "token_count": 11,
        },
    ]


@pytest.fixture
def sample_embeddings():
    """Sample embeddings (1024-dimensional vectors)."""
    import numpy as np
    # Create 3 sample embeddings with some similarity
    embeddings = []
    for i in range(3):
        vec = np.random.randn(1024)
        vec = vec / np.linalg.norm(vec)  # Normalize
        embeddings.append(vec.tolist())
    return embeddings


@pytest.fixture
def sample_chunk_with_embedding(sample_chunks, sample_embeddings):
    """Sample chunk with embedding attached."""
    chunk = sample_chunks[0].copy()
    chunk["vector"] = sample_embeddings[0]
    return chunk


# ========== MOCK API FIXTURES ==========

@pytest.fixture
def mock_anthropic_client(mocker):
    """Mock Anthropic Claude API client."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Mocked Claude response")]
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)

    mock_client.messages.create.return_value = mock_response

    mocker.patch("anthropic.Anthropic", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_voyage_client(mocker, sample_embeddings):
    """Mock Voyage AI client."""
    mock_client = Mock()
    mock_result = Mock()
    mock_result.embeddings = sample_embeddings

    mock_client.embed.return_value = mock_result

    mocker.patch("voyageai.Client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_lancedb(mocker):
    """Mock LanceDB database."""
    mock_db = Mock()
    mock_table = Mock()

    # Mock table operations
    mock_table.to_pandas.return_value = Mock(empty=True)
    mock_table.search.return_value = Mock()

    mock_db.open_table.return_value = mock_table
    mock_db.create_table.return_value = mock_table

    mocker.patch("lancedb.connect", return_value=mock_db)
    return mock_db


# ========== CHUNK QUALITY FIXTURES ==========

@pytest.fixture
def high_quality_chunk():
    """High quality chunk for testing."""
    return {
        "id": "high_quality_0",
        "content": """The product strategy for 2026 focuses on three pillars:
        1. Customer Experience - improving onboarding and reducing time-to-value
        2. Platform Capabilities - building extensible APIs and integration framework
        3. Market Expansion - targeting mid-market segment with Stage 1/2 solutions

        Each pillar has clear success metrics and quarterly milestones.""",
        "lens": "your-voice",
        "source_file": "strategy.md",
        "chunk_index": 0,
        "token_count": 85,
    }


@pytest.fixture
def low_quality_chunk():
    """Low quality chunk for testing."""
    return {
        "id": "low_quality_0",
        "content": "yeah so um like we should maybe do something",
        "lens": "team-conversational",
        "source_file": "notes.txt",
        "chunk_index": 0,
        "token_count": 9,
    }


# ========== GRAPH FIXTURES ==========

@pytest.fixture
def sample_graph_nodes():
    """Sample nodes for UnifiedContextGraph."""
    return {
        "chunks": [
            {
                "id": "chunk_1",
                "content": "CPQ improvements needed",
                "lens": "team-structured",
            },
            {
                "id": "chunk_2",
                "content": "API modernization required",
                "lens": "engineering",
            },
        ],
        "questions": [
            {
                "id": "q_eng_001",
                "question": "What is the timeline for API modernization?",
                "audience": "engineering",
                "priority": "high",
                "status": "open",
            }
        ],
        "roadmap_items": [
            {
                "id": "item_1",
                "name": "CPQ Configuration Improvements",
                "description": "Enhance the configuration UX",
                "horizon": "now",
            }
        ],
    }


# ========== UTILITY FIXTURES ==========

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("VOYAGE_API_KEY", "test-voyage-key")


@pytest.fixture
def sample_roadmap_text():
    """Sample generated roadmap text."""
    return """# Product Roadmap

## Now (0-3 months)
- **CPQ Configuration Improvements**: Streamline configuration workflow
- **Catalog Search Enhancement**: Add faceted search and filters

## Next (3-6 months)
- **API Modernization**: Migrate to REST APIs
- **Pricing Engine**: Build flexible pricing rules

## Later (6-12 months)
- **Platform Integration**: Connect with major CRM systems
"""


@pytest.fixture
def sample_questions_list():
    """Sample questions for testing question management."""
    return [
        {
            "id": "q_eng_001",
            "question": "Can we complete API modernization by Q2?",
            "audience": "engineering",
            "category": "feasibility",
            "priority": "critical",
            "status": "open",
        },
        {
            "id": "q_leadership_001",
            "question": "What is the expected ROI for pricing engine investment?",
            "audience": "leadership",
            "category": "investment",
            "priority": "high",
            "status": "open",
        },
        {
            "id": "q_product_001",
            "question": "Should we prioritize CPQ or Catalog work?",
            "audience": "product",
            "category": "trade-off",
            "priority": "high",
            "status": "answered",
            "answer": "Prioritize CPQ based on customer feedback.",
        },
    ]


# ========== MOCK DOCUMENT FIXTURES ==========

@pytest.fixture
def sample_pdf_content():
    """Sample content as if extracted from PDF."""
    return """
Enterprise Product Strategy
Q1 2026

Executive Summary
Our strategy focuses on becoming the leading platform for B2B commerce.
Key initiatives include modernizing our CPQ system and expanding catalog capabilities.

Market Analysis
The B2B software market is projected to grow 15% annually.
Competitors are investing heavily in AI-powered configuration tools.

Product Roadmap
Phase 1: Foundation (Q1-Q2)
- API modernization
- Database migration
- Core UX improvements

Phase 2: Expansion (Q3-Q4)
- Advanced pricing rules
- CRM integrations
- Analytics dashboard
"""


@pytest.fixture
def sample_docx_content():
    """Sample content as if extracted from DOCX."""
    return """
Meeting Notes - Product Planning Session
Date: January 5, 2026
Attendees: Product, Engineering, Sales

Discussion Points:
1. Sales feedback: Customers are frustrated with slow quote generation
2. Engineering: Current system architecture is limiting scalability
3. Product: Need to balance new features with technical debt

Action Items:
- Engineering to provide technical assessment by next week
- Product to prioritize based on customer impact
- Sales to document top 5 customer pain points

Decisions:
- Agreed to allocate 30% of Q1 to technical improvements
- Will delay advanced analytics to focus on core workflows
"""


# ========== PYTEST CONFIGURATION ==========

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests that require external API access"
    )


# ========== CLEANUP FIXTURES ==========

@pytest.fixture(autouse=True)
def reset_imports():
    """Reset module imports between tests to avoid state leakage."""
    import sys
    import importlib

    # Store modules before test
    modules_before = set(sys.modules.keys())

    yield

    # Clean up modules added during test
    modules_after = set(sys.modules.keys())
    for module in modules_after - modules_before:
        if module.startswith("roadmap") or module.startswith("app"):
            sys.modules.pop(module, None)
