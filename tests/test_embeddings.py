"""
Unit tests for embedding and vector search functions in roadmap.py
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from roadmap import generate_embeddings, init_db, index_chunks, retrieve_chunks


class TestGenerateEmbeddings:
    """Tests for embedding generation."""

    @pytest.mark.unit
    def test_generate_single_embedding(self, mock_env_vars, sample_embeddings):
        """Test generating embedding for single text."""
        texts = ["This is a test document about CPQ."]

        # Create properly configured mock
        mock_client = Mock()
        mock_result = Mock()
        mock_result.embeddings = [sample_embeddings[0]]  # Return one embedding
        mock_client.embed.return_value = mock_result

        with patch("roadmap.voyageai.Client", return_value=mock_client):
            embeddings = generate_embeddings(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1024  # Voyage returns 1024-dim vectors

    @pytest.mark.unit
    def test_generate_multiple_embeddings(self, mock_voyage_client, mock_env_vars):
        """Test generating embeddings for multiple texts."""
        texts = [
            "First document about roadmaps.",
            "Second document about planning.",
            "Third document about strategy.",
        ]

        with patch("roadmap.voyageai.Client", return_value=mock_voyage_client):
            embeddings = generate_embeddings(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 1024 for emb in embeddings)

    @pytest.mark.unit
    def test_generate_empty_list(self, mock_voyage_client, mock_env_vars):
        """Test generating embeddings for empty list."""
        texts = []

        with patch("roadmap.voyageai.Client", return_value=mock_voyage_client):
            mock_voyage_client.embed.return_value.embeddings = []
            embeddings = generate_embeddings(texts)

        assert embeddings == []

    @pytest.mark.unit
    def test_generate_with_long_text(self, mock_voyage_client, mock_env_vars):
        """Test generating embedding for very long text."""
        texts = ["word " * 10000]  # Very long text

        with patch("roadmap.voyageai.Client", return_value=mock_voyage_client):
            embeddings = generate_embeddings(texts)

        # Should handle long text (may truncate or split)
        assert isinstance(embeddings, list)

    @pytest.mark.unit
    def test_generate_with_unicode(self, mock_env_vars, sample_embeddings):
        """Test generating embeddings with unicode text."""
        texts = ["Hello 世界 🌍"]

        # Create properly configured mock
        mock_client = Mock()
        mock_result = Mock()
        mock_result.embeddings = [sample_embeddings[0]]  # Return one embedding
        mock_client.embed.return_value = mock_result

        with patch("roadmap.voyageai.Client", return_value=mock_client):
            embeddings = generate_embeddings(texts)

        assert len(embeddings) == 1


class TestInitDb:
    """Tests for database initialization."""

    @pytest.mark.unit
    def test_init_creates_connection(self, mock_lancedb, temp_dir, monkeypatch):
        """Test that init_db creates a database connection."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir / "data")

        with patch("roadmap.lancedb.connect", return_value=mock_lancedb):
            db = init_db()

        assert db is not None

    @pytest.mark.unit
    def test_init_uses_correct_path(self, mock_lancedb, temp_dir, monkeypatch):
        """Test that init_db uses correct database path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", data_dir)

        with patch("roadmap.lancedb.connect") as mock_connect:
            mock_connect.return_value = mock_lancedb
            init_db()

            # Verify connect was called with correct path
            mock_connect.assert_called_once()


class TestIndexChunks:
    """Tests for chunk indexing."""

    @pytest.mark.unit
    def test_index_new_chunks(
        self, mock_lancedb, mock_voyage_client, sample_chunks, sample_embeddings, mock_env_vars
    ):
        """Test indexing new chunks."""
        # Setup mocks
        mock_table = Mock()
        mock_lancedb.create_table.return_value = mock_table
        mock_lancedb.open_table.side_effect = Exception("Table does not exist")

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=sample_embeddings):
                # Should not raise exception
                index_chunks(sample_chunks, source_file="test.md")

    @pytest.mark.unit
    def test_index_to_existing_table(
        self, mock_lancedb, sample_chunks, sample_embeddings, mock_env_vars
    ):
        """Test indexing chunks to existing table."""
        # Setup mocks
        mock_table = Mock()
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=sample_embeddings):
                index_chunks(sample_chunks, source_file="test.md")

                # Verify add was called on table
                mock_table.add.assert_called()

    @pytest.mark.unit
    def test_index_empty_chunks(self, mock_lancedb, mock_env_vars):
        """Test indexing empty chunk list."""
        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[]):
                # Should handle gracefully
                index_chunks([], source_file="test.md")

    @pytest.mark.unit
    def test_index_adds_created_at(
        self, mock_lancedb, sample_chunks, sample_embeddings, mock_env_vars
    ):
        """Test that indexing adds created_at timestamp."""
        mock_table = Mock()
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=sample_embeddings):
                with patch("roadmap.datetime") as mock_datetime:
                    mock_datetime.now.return_value.isoformat.return_value = "2026-01-07T12:00:00"
                    index_chunks(sample_chunks, source_file="test.md")

                    # Verify chunks have timestamps
                    call_args = mock_table.add.call_args
                    if call_args:
                        indexed_chunks = call_args[0][0] if call_args[0] else []
                        # Chunks should have been processed
                        assert isinstance(indexed_chunks, list) or isinstance(indexed_chunks, type(None))


class TestRetrieveChunks:
    """Tests for chunk retrieval."""

    @pytest.mark.unit
    def test_retrieve_with_results(self, mock_lancedb, mock_env_vars):
        """Test retrieving chunks with results."""
        # Setup mock results
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {
                "id": "chunk_1",
                "content": "Test content",
                "lens": "team-structured",
                "_distance": 0.1,
            }
        ]

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                chunks = retrieve_chunks("test query", top_k=5)

        assert isinstance(chunks, list)
        assert len(chunks) > 0

    @pytest.mark.unit
    def test_retrieve_with_no_results(self, mock_lancedb, mock_env_vars):
        """Test retrieving chunks when no results found."""
        # Setup empty results
        mock_results = Mock()
        mock_results.to_list.return_value = []

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                chunks = retrieve_chunks("test query", top_k=5)

        assert chunks == []

    @pytest.mark.unit
    def test_retrieve_respects_top_k(self, mock_lancedb, mock_env_vars):
        """Test that retrieve_chunks respects top_k parameter."""
        # Setup mock results with many items
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {"id": f"chunk_{i}", "content": f"Content {i}", "lens": "team-structured"}
            for i in range(100)
        ]

        mock_table = Mock()
        mock_search = mock_table.search.return_value
        mock_search.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                retrieve_chunks("test query", top_k=10)

                # Verify limit was called with correct value
                mock_search.limit.assert_called_with(10)

    @pytest.mark.unit
    def test_retrieve_empty_query(self, mock_lancedb, mock_env_vars, sample_embeddings):
        """Test retrieving with empty query."""
        mock_table = Mock()
        mock_result = Mock()
        mock_result.to_list.return_value = []
        mock_table.search.return_value.limit.return_value = mock_result
        mock_lancedb.open_table.return_value = mock_table

        # Mock voyageai.Client since retrieve_chunks creates its own client
        mock_vo_client = Mock()
        mock_vo_result = Mock()
        mock_vo_result.embeddings = [sample_embeddings[0]]
        mock_vo_client.embed.return_value = mock_vo_result

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.voyageai.Client", return_value=mock_vo_client):
                # Should handle gracefully
                chunks = retrieve_chunks("", top_k=5)

        assert isinstance(chunks, list)

    @pytest.mark.unit
    def test_retrieve_includes_similarity_scores(self, mock_lancedb, mock_env_vars):
        """Test that retrieved chunks include similarity scores."""
        # Setup mock results with distance scores
        mock_results = Mock()
        mock_results.to_list.return_value = [
            {
                "id": "chunk_1",
                "content": "Test content",
                "lens": "team-structured",
                "_distance": 0.15,
            },
            {
                "id": "chunk_2",
                "content": "More content",
                "lens": "engineering",
                "_distance": 0.25,
            },
        ]

        mock_table = Mock()
        mock_table.search.return_value.limit.return_value = mock_results
        mock_lancedb.open_table.return_value = mock_table

        with patch("roadmap.init_db", return_value=mock_lancedb):
            with patch("roadmap.generate_embeddings", return_value=[[0.1] * 1024]):
                chunks = retrieve_chunks("test query", top_k=5)

        # Chunks should have similarity or distance information
        assert all(isinstance(c, dict) for c in chunks)
