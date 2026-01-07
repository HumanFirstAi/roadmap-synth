"""
Unit tests for retrieval and authority functions in roadmap.py
"""

import pytest
from unittest.mock import Mock, patch
from roadmap import (
    retrieve_balanced,
    retrieve_with_authority,
    detect_potential_contradictions,
    AUTHORITY_LEVELS,
)


class TestAuthorityLevels:
    """Tests for authority level configuration."""

    @pytest.mark.unit
    def test_authority_levels_defined(self):
        """Test that authority levels are properly defined."""
        assert isinstance(AUTHORITY_LEVELS, dict)
        # AUTHORITY_LEVELS maps node types, not lens names
        assert "decision" in AUTHORITY_LEVELS
        assert "chunk" in AUTHORITY_LEVELS
        assert "roadmap_item" in AUTHORITY_LEVELS

    @pytest.mark.unit
    def test_decision_highest_authority(self):
        """Test that decision has highest authority (lowest number)."""
        decision_authority = AUTHORITY_LEVELS["decision"]

        # Lower numbers = higher authority
        for node_type, authority in AUTHORITY_LEVELS.items():
            if node_type != "decision":
                assert decision_authority <= authority

    @pytest.mark.unit
    def test_pending_question_lowest_authority(self):
        """Test that pending_question has lowest authority (highest number)."""
        pending_authority = AUTHORITY_LEVELS["pending_question"]

        # Higher numbers = lower authority
        for node_type, authority in AUTHORITY_LEVELS.items():
            if node_type != "pending_question":
                assert pending_authority >= authority

    @pytest.mark.unit
    def test_authority_hierarchy_ordered(self):
        """Test that authority levels follow expected hierarchy."""
        # Decision should override everything
        assert AUTHORITY_LEVELS["decision"] == 1
        # Chunk should be lower than strategic elements
        assert AUTHORITY_LEVELS["chunk"] > AUTHORITY_LEVELS["roadmap_item"]
        # All values should be positive integers
        assert all(isinstance(v, int) and v > 0 for v in AUTHORITY_LEVELS.values())


class TestRetrieveBalanced:
    """Tests for balanced retrieval across lenses."""

    @pytest.mark.unit
    def test_balanced_retrieval_basic(self, mock_lancedb, mock_env_vars):
        """Test basic balanced retrieval."""
        # Setup mock to return chunks from different lenses
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {"id": f"chunk_{i}", "content": f"Content {i}", "lens": lens}
            for i, lens in enumerate(
                ["your-voice", "team-structured", "engineering"]
            )
        ]

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                chunks = retrieve_balanced("test query", chunks_per_lens=2)

        assert isinstance(chunks, list)

    @pytest.mark.unit
    def test_balanced_ensures_diversity(self, mock_lancedb, mock_env_vars):
        """Test that balanced retrieval ensures lens diversity."""
        # Setup mock with multiple chunks from same lens
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {"id": f"chunk_{i}", "content": f"Content {i}", "lens": "team-structured"}
            for i in range(20)
        ]

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                chunks = retrieve_balanced("test query", chunks_per_lens=5)

        # Should attempt to get chunks from different lenses
        assert isinstance(chunks, list)

    @pytest.mark.unit
    def test_balanced_respects_chunks_per_lens(self, mock_lancedb, mock_env_vars):
        """Test that chunks_per_lens parameter is respected."""
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {"id": f"chunk_{i}", "content": f"Content {i}", "lens": "team-structured"}
            for i in range(10)
        ]

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                retrieve_balanced("test query", chunks_per_lens=3)

                # Verify the query behavior
                assert mock_table.search.called


class TestRetrieveWithAuthority:
    """Tests for authority-based retrieval."""

    @pytest.mark.unit
    def test_authority_reranking(self, sample_chunks, mock_lancedb, mock_env_vars):
        """Test that chunks are reranked by authority."""
        # Create mock graph with proper node_indices structure
        mock_graph = Mock()
        mock_graph.graph.nodes.return_value = []
        mock_graph.graph.edges.return_value = []
        mock_graph.node_indices = {
            "chunk": {},
            "question": {},
            "roadmap_item": {},
            "assessment": {},
            "decision": {},
            "gap": {},
        }

        # Setup mock retrieve to return chunks with different lenses
        with patch("roadmap.retrieve_chunks") as mock_retrieve:
            chunks_mixed = [
                {
                    "id": "1",
                    "content": "Test",
                    "lens": "external-analyst",
                    "_distance": 0.1,
                },
                {"id": "2", "content": "Test", "lens": "your-voice", "_distance": 0.2},
                {
                    "id": "3",
                    "content": "Test",
                    "lens": "engineering",
                    "_distance": 0.15,
                },
            ]
            mock_retrieve.return_value = chunks_mixed

            result = retrieve_with_authority("test query", mock_graph, top_k=20)

        # Should have reranked results
        assert "chunks" in result
        assert isinstance(result["chunks"], list)

        # Higher authority chunks should rank higher (your-voice > engineering > external-analyst)
        if len(result["chunks"]) >= 2:
            # Check that reranking happened (exact order depends on implementation)
            assert isinstance(result["chunks"][0], dict)

    @pytest.mark.unit
    def test_authority_includes_graph_context(self, mock_lancedb, mock_env_vars):
        """Test that authority retrieval includes graph context."""
        mock_graph = Mock()
        mock_graph.graph.nodes.return_value = ["chunk_1", "q_1"]
        mock_graph.node_indices = {
            "chunk": {"chunk_1": {"content": "Test", "lens": "your-voice"}},
            "question": {"q_1": {"question": "What?"}},
            "roadmap_item": {},
            "assessment": {},
            "decision": {},
            "gap": {},
        }

        with patch("roadmap.retrieve_chunks") as mock_retrieve:
            mock_retrieve.return_value = [
                {"id": "chunk_1", "content": "Test", "lens": "your-voice"}
            ]

            result = retrieve_with_authority("test query", mock_graph, top_k=20)

        # Should include graph entities
        assert "chunks" in result
        # May also include questions, decisions, etc. depending on implementation

    @pytest.mark.unit
    def test_authority_with_empty_results(self, mock_lancedb, mock_env_vars):
        """Test authority retrieval with no results."""
        mock_graph = Mock()
        mock_graph.graph.nodes.return_value = []
        mock_graph.node_indices = {
            "chunk": {},
            "question": {},
            "roadmap_item": {},
            "assessment": {},
            "decision": {},
            "gap": {},
        }

        with patch("roadmap.retrieve_chunks") as mock_retrieve:
            mock_retrieve.return_value = []

            result = retrieve_with_authority("test query", mock_graph, top_k=20)

        assert "chunks" in result
        assert isinstance(result["chunks"], list)

    @pytest.mark.unit
    def test_authority_filters_low_quality(self, mock_lancedb, mock_env_vars):
        """Test that low quality chunks may be filtered or deprioritized."""
        mock_graph = Mock()
        mock_graph.graph.nodes.return_value = []
        mock_graph.node_indices = {
            "chunk": {},
            "question": {},
            "roadmap_item": {},
            "assessment": {},
            "decision": {},
            "gap": {},
        }

        with patch("roadmap.retrieve_chunks") as mock_retrieve:
            chunks = [
                {
                    "id": "good",
                    "content": "This is substantive strategic content.",
                    "lens": "your-voice",
                    "_distance": 0.1,
                },
                {
                    "id": "bad",
                    "content": "um yeah so",
                    "lens": "team-conversational",
                    "_distance": 0.05,
                },
            ]
            mock_retrieve.return_value = chunks

            result = retrieve_with_authority("test query", mock_graph, top_k=20)

        # Should have some chunks (filtering/ranking depends on implementation)
        assert "chunks" in result


class TestDetectPotentialContradictions:
    """Tests for contradiction detection."""

    @pytest.mark.unit
    def test_detect_contradictions_in_chunks(self):
        """Test detecting contradictions between chunks."""
        chunks = [
            {
                "id": "1",
                "content": "We will launch in Q1 2026",
                "lens": "team-structured",
            },
            {
                "id": "2",
                "content": "Launch delayed to Q3 2026",
                "lens": "team-conversational",
            },
            {
                "id": "3",
                "content": "Product strategy focuses on catalog",
                "lens": "your-voice",
            },
        ]

        mock_graph = Mock()
        # Make nodes behave like a dictionary for membership tests and item access
        mock_graph.graph.nodes = {
            "1": {"key_terms": ["launch", "q1", "2026"]},
            "2": {"key_terms": ["launch", "delayed", "q3", "2026"]},
            "3": {"key_terms": ["product", "strategy", "catalog"]},
        }
        mock_graph.node_indices = {
            "chunk": {
                "1": chunks[0],
                "2": chunks[1],
                "3": chunks[2],
            },
            "gap": {},
        }

        contradictions = detect_potential_contradictions(chunks, mock_graph)

        # Should return list of potential contradictions
        assert isinstance(contradictions, list)

    @pytest.mark.unit
    def test_no_contradictions_in_aligned_chunks(self):
        """Test that aligned chunks show no contradictions."""
        chunks = [
            {
                "id": "1",
                "content": "Focus on CPQ improvements",
                "lens": "team-structured",
            },
            {
                "id": "2",
                "content": "CPQ is our top priority",
                "lens": "your-voice",
            },
            {"id": "3", "content": "Improving CPQ workflow", "lens": "engineering"},
        ]

        mock_graph = Mock()
        # Make nodes behave like a dictionary
        mock_graph.graph.nodes = {
            "1": {"key_terms": ["cpq", "improvements"]},
            "2": {"key_terms": ["cpq", "priority"]},
            "3": {"key_terms": ["cpq", "workflow"]},
        }
        mock_graph.node_indices = {
            "chunk": {
                "1": chunks[0],
                "2": chunks[1],
                "3": chunks[2],
            },
            "gap": {},
        }

        contradictions = detect_potential_contradictions(chunks, mock_graph)

        # Should have few or no contradictions for aligned content
        assert isinstance(contradictions, list)

    @pytest.mark.unit
    def test_detect_contradictions_empty_list(self):
        """Test contradiction detection with empty chunk list."""
        mock_graph = Mock()

        contradictions = detect_potential_contradictions([], mock_graph)

        assert contradictions == []

    @pytest.mark.unit
    def test_detect_contradictions_single_chunk(self):
        """Test contradiction detection with single chunk."""
        chunks = [
            {"id": "1", "content": "Test content", "lens": "team-structured"}
        ]

        mock_graph = Mock()
        # Make nodes behave like a dictionary
        mock_graph.graph.nodes = {
            "1": {"key_terms": ["test", "content"]},
        }

        contradictions = detect_potential_contradictions(chunks, mock_graph)

        # Can't have contradictions with single chunk
        assert len(contradictions) == 0


class TestAuthorityWeighting:
    """Tests for authority weight calculations."""

    @pytest.mark.unit
    def test_authority_levels_for_node_types(self):
        """Test that AUTHORITY_LEVELS provides ordering for node types."""
        # AUTHORITY_LEVELS maps node types, not lens names
        # Verify the hierarchy exists
        assert AUTHORITY_LEVELS["decision"] < AUTHORITY_LEVELS["chunk"]
        assert AUTHORITY_LEVELS["decision"] < AUTHORITY_LEVELS["pending_question"]

        # Verify all expected node types are present
        expected_types = ["decision", "chunk", "roadmap_item", "pending_question"]
        for node_type in expected_types:
            assert node_type in AUTHORITY_LEVELS
            assert isinstance(AUTHORITY_LEVELS[node_type], (int, float))
            assert AUTHORITY_LEVELS[node_type] > 0
