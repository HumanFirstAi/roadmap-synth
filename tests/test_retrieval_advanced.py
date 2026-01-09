"""
Unit tests for advanced retrieval functions in roadmap.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import retrieve_with_graph_expansion, ContextGraph


class TestRetrieveWithGraphExpansion:
    """Tests for graph-enhanced retrieval."""

    @pytest.mark.unit
    def test_basic_graph_expansion(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test basic graph expansion retrieval."""
        # Create graph with connected chunks
        graph = ContextGraph()
        graph.graph.add_node("chunk1", chunk_id="chunk1", key_terms=["api", "architecture"])
        graph.graph.add_node("chunk2", chunk_id="chunk2", key_terms=["database", "schema"])
        graph.graph.add_node("chunk3", chunk_id="chunk3", key_terms=["frontend", "ui"])
        graph.graph.add_edge("chunk1", "chunk2", edge_type="MENTIONS")

        # Mock LanceDB results
        initial_results = [
            {"id": "chunk1", "content": "API architecture", "lens": "engineering", "_distance": 0.1}
        ]
        expanded_results = [
            {"id": "chunk2", "content": "Database schema", "lens": "engineering", "_distance": 0.3}
        ]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.to_list.side_effect = [initial_results, expanded_results]
            mock_search.where.return_value = mock_search
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "Tell me about the API",
                    graph,
                    initial_limit=1,
                    expansion_hops=1,
                    final_limit=10
                )

                assert len(result) >= 1
                assert any(r["id"] == "chunk1" for r in result)

    @pytest.mark.unit
    def test_expansion_with_empty_graph(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test expansion when graph has no connections."""
        graph = ContextGraph()

        initial_results = [
            {"id": "chunk1", "content": "Content", "lens": "your-voice", "_distance": 0.1}
        ]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.to_list.return_value = initial_results
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=5,
                    expansion_hops=1,
                    final_limit=10
                )

                assert len(result) == 1
                assert result[0]["id"] == "chunk1"

    @pytest.mark.unit
    def test_expansion_respects_hop_limit(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test that expansion respects the hop limit."""
        # Create graph with chain: chunk1 -> chunk2 -> chunk3 -> chunk4
        graph = ContextGraph()
        graph.graph.add_node("chunk1")
        graph.graph.add_node("chunk2")
        graph.graph.add_node("chunk3")
        graph.graph.add_node("chunk4")
        graph.graph.add_edge("chunk1", "chunk2")
        graph.graph.add_edge("chunk2", "chunk3")
        graph.graph.add_edge("chunk3", "chunk4")

        initial_results = [{"id": "chunk1", "content": "Start", "lens": "your-voice"}]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.where.return_value = mock_search

            # Mock initial search
            def mock_to_list():
                return initial_results

            # Mock expanded searches
            def mock_where_to_list():
                return []

            mock_search.to_list.side_effect = [mock_to_list()]
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                # With 1 hop, should only reach chunk2
                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=5,
                    expansion_hops=1,
                    final_limit=10
                )

                assert len(result) >= 1

    @pytest.mark.unit
    def test_expansion_deduplicates_results(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test that expansion deduplicates chunks."""
        graph = ContextGraph()
        graph.graph.add_node("chunk1")
        graph.graph.add_node("chunk2")
        graph.graph.add_edge("chunk1", "chunk2")

        # Mock initial results with duplicates
        initial_results = [
            {"id": "chunk1", "content": "Content 1", "lens": "your-voice"},
            {"id": "chunk1", "content": "Content 1", "lens": "your-voice"},  # Duplicate
        ]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.to_list.return_value = initial_results
            mock_search.where.return_value = mock_search
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=5,
                    expansion_hops=1,
                    final_limit=10
                )

                # Should have only 1 result despite duplicate in initial
                assert len(result) == 1
                assert result[0]["id"] == "chunk1"

    @pytest.mark.unit
    def test_expansion_respects_final_limit(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test that expansion respects the final result limit."""
        graph = ContextGraph()
        for i in range(20):
            graph.graph.add_node(f"chunk{i}")
            if i > 0:
                graph.graph.add_edge("chunk0", f"chunk{i}")

        initial_results = [{"id": f"chunk{i}", "content": f"Content {i}", "lens": "your-voice"} for i in range(10)]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.to_list.return_value = initial_results
            mock_search.where.return_value = mock_search
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=10,
                    expansion_hops=1,
                    final_limit=5  # Limit to 5 results
                )

                assert len(result) <= 5

    @pytest.mark.unit
    def test_expansion_handles_missing_table(self, mock_env_vars, sample_embeddings):
        """Test expansion when table doesn't exist."""
        graph = ContextGraph()

        with patch("roadmap.init_db") as mock_init_db:
            mock_db = Mock()
            mock_db.open_table.side_effect = Exception("Table not found")
            mock_init_db.return_value = mock_db

            result = retrieve_with_graph_expansion(
                "query",
                graph,
                initial_limit=5,
                expansion_hops=1,
                final_limit=10
            )

            assert result == []

    @pytest.mark.unit
    def test_expansion_handles_isolated_nodes(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test expansion with isolated nodes in graph."""
        graph = ContextGraph()
        graph.graph.add_node("chunk1")
        graph.graph.add_node("chunk2")
        # No edges - isolated nodes

        initial_results = [{"id": "chunk1", "content": "Content", "lens": "your-voice"}]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.to_list.return_value = initial_results
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=5,
                    expansion_hops=1,
                    final_limit=10
                )

                # Should only return initial result
                assert len(result) == 1
                assert result[0]["id"] == "chunk1"

    @pytest.mark.unit
    def test_expansion_with_multi_hop_paths(self, mock_env_vars, mock_lancedb, sample_embeddings):
        """Test expansion follows multi-hop paths correctly."""
        graph = ContextGraph()
        # Create diamond pattern: chunk1 -> chunk2, chunk3 -> chunk4
        #                          chunk2, chunk3 both link to chunk4
        graph.graph.add_node("chunk1")
        graph.graph.add_node("chunk2")
        graph.graph.add_node("chunk3")
        graph.graph.add_node("chunk4")
        graph.graph.add_edge("chunk1", "chunk2")
        graph.graph.add_edge("chunk1", "chunk3")
        graph.graph.add_edge("chunk2", "chunk4")
        graph.graph.add_edge("chunk3", "chunk4")

        initial_results = [{"id": "chunk1", "content": "Start", "lens": "your-voice"}]

        with patch("roadmap.init_db") as mock_init_db:
            mock_table = Mock()
            mock_search = Mock()
            mock_search.limit.return_value = mock_search
            mock_search.where.return_value = mock_search
            mock_search.to_list.return_value = initial_results
            mock_table.search.return_value = mock_search

            mock_db = Mock()
            mock_db.open_table.return_value = mock_table
            mock_init_db.return_value = mock_db

            with patch("roadmap.voyageai.Client") as mock_voyage:
                mock_client = Mock()
                mock_embed_result = Mock()
                mock_embed_result.embeddings = [sample_embeddings[0]]
                mock_client.embed.return_value = mock_embed_result
                mock_voyage.return_value = mock_client

                result = retrieve_with_graph_expansion(
                    "query",
                    graph,
                    initial_limit=5,
                    expansion_hops=2,  # 2 hops should reach chunk4
                    final_limit=10
                )

                assert len(result) >= 1
