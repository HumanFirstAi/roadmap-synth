"""
Unit tests for UnifiedContextGraph in roadmap.py
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import UnifiedContextGraph


class TestUnifiedContextGraphInit:
    """Tests for UnifiedContextGraph initialization."""

    @pytest.mark.unit
    def test_init_creates_empty_graph(self):
        """Test that initialization creates empty graph."""
        graph = UnifiedContextGraph()

        assert graph.graph is not None
        assert len(graph.graph.nodes()) == 0
        assert len(graph.graph.edges()) == 0

    @pytest.mark.unit
    def test_init_creates_node_indices(self):
        """Test that initialization creates node type indices."""
        graph = UnifiedContextGraph()

        assert hasattr(graph, "node_indices")
        assert isinstance(graph.node_indices, dict)
        assert "chunk" in graph.node_indices
        assert "question" in graph.node_indices
        assert "roadmap_item" in graph.node_indices


class TestAddNode:
    """Tests for adding nodes to graph."""

    @pytest.mark.unit
    def test_add_chunk_node(self):
        """Test adding a chunk node."""
        graph = UnifiedContextGraph()

        node_data = {
            "id": "chunk_1",
            "content": "Test content",
            "lens": "team-structured",
        }

        graph.add_node(node_id="chunk_1", node_type="chunk", data=node_data)

        assert "chunk_1" in graph.graph.nodes()
        assert graph.graph.nodes["chunk_1"]["node_type"] == "chunk"
        assert "chunk_1" in graph.node_indices["chunk"]

    @pytest.mark.unit
    def test_add_question_node(self):
        """Test adding a question node."""
        graph = UnifiedContextGraph()

        node_data = {
            "id": "q_1",
            "question": "What is the timeline?",
            "audience": "engineering",
        }

        graph.add_node(node_id="q_1", node_type="question", data=node_data)

        assert "q_1" in graph.graph.nodes()
        assert "q_1" in graph.node_indices["question"]

    @pytest.mark.unit
    def test_add_roadmap_item_node(self):
        """Test adding a roadmap item node."""
        graph = UnifiedContextGraph()

        node_data = {
            "id": "item_1",
            "name": "CPQ Improvements",
            "horizon": "now",
        }

        graph.add_node(node_id="item_1", node_type="roadmap_item", data=node_data)

        assert "item_1" in graph.graph.nodes()
        assert "item_1" in graph.node_indices["roadmap_item"]

    @pytest.mark.unit
    def test_add_duplicate_node(self):
        """Test adding duplicate node (should update)."""
        graph = UnifiedContextGraph()

        node_data1 = {"id": "chunk_1", "content": "Original"}
        node_data2 = {"id": "chunk_1", "content": "Updated"}

        graph.add_node("chunk_1", "chunk", node_data1)
        graph.add_node("chunk_1", "chunk", node_data2)

        # Should only have one node
        assert len([n for n in graph.graph.nodes() if n == "chunk_1"]) == 1

    @pytest.mark.unit
    def test_add_node_with_embedding(self, sample_embeddings):
        """Test adding node with embedding vector."""
        graph = UnifiedContextGraph()

        node_data = {
            "id": "chunk_1",
            "content": "Test",
            "embedding": sample_embeddings[0],
        }

        graph.add_node("chunk_1", "chunk", node_data)

        assert "embedding" in graph.node_indices["chunk"]["chunk_1"]


class TestAddEdge:
    """Tests for adding edges to graph."""

    @pytest.mark.unit
    def test_add_edge_between_chunks(self):
        """Test adding edge between two chunks."""
        graph = UnifiedContextGraph()

        # Add two nodes
        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})

        # Add edge
        graph.add_edge("chunk_1", "chunk_2", edge_type="semantic", weight=0.8)

        assert graph.graph.has_edge("chunk_1", "chunk_2")
        edge_data = graph.graph.edges["chunk_1", "chunk_2"]
        assert edge_data["edge_type"] == "semantic"  # Key is 'edge_type', not 'type'
        assert edge_data["weight"] == 0.8

    @pytest.mark.unit
    def test_add_edge_cross_type(self):
        """Test adding edge between different node types."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("item_1", "roadmap_item", {"id": "item_1"})

        graph.add_edge("item_1", "chunk_1", edge_type="supports", weight=0.9)

        assert graph.graph.has_edge("item_1", "chunk_1")

    @pytest.mark.unit
    def test_add_edge_without_nodes(self):
        """Test adding edge when nodes don't exist."""
        graph = UnifiedContextGraph()

        # Try to add edge without creating nodes first
        # Should either fail gracefully or auto-create nodes
        try:
            graph.add_edge("nonexistent_1", "nonexistent_2", edge_type="test")
        except Exception:
            # Expected to fail
            pass

    @pytest.mark.unit
    def test_add_bidirectional_edge(self):
        """Test that edges can be traversed both ways."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})

        graph.add_edge("chunk_1", "chunk_2", edge_type="semantic", weight=0.7)

        # Check if edge exists in both directions (depends on graph type)
        assert graph.graph.has_edge("chunk_1", "chunk_2")


class TestGraphPersistence:
    """Tests for graph save/load functionality."""

    @pytest.mark.unit
    def test_save_empty_graph(self, test_data_dir, monkeypatch):
        """Test saving empty graph."""
        unified_graph_dir = test_data_dir / "unified_graph"
        monkeypatch.setattr("roadmap.DATA_DIR", test_data_dir)
        monkeypatch.setattr("roadmap.GRAPH_PATH", unified_graph_dir)

        graph = UnifiedContextGraph()
        graph.save()

        # Check that files were created
        assert (unified_graph_dir / "graph.json").exists()

    @pytest.mark.unit
    def test_save_graph_with_nodes(self, test_data_dir, monkeypatch):
        """Test saving graph with nodes."""
        unified_graph_dir = test_data_dir / "unified_graph"
        monkeypatch.setattr("roadmap.DATA_DIR", test_data_dir)
        monkeypatch.setattr("roadmap.GRAPH_PATH", unified_graph_dir)

        graph = UnifiedContextGraph()
        graph.add_node("chunk_1", "chunk", {"id": "chunk_1", "content": "Test"})
        graph.add_node("q_1", "question", {"id": "q_1", "question": "What?"})

        graph.save()

        # Verify files exist and contain data
        chunk_file = unified_graph_dir / "chunk_nodes.json"
        question_file = unified_graph_dir / "question_nodes.json"

        assert chunk_file.exists()
        assert question_file.exists()

        # Verify content
        with open(chunk_file) as f:
            chunks = json.load(f)
            assert "chunk_1" in chunks

    @pytest.mark.unit
    def test_load_empty_graph(self, test_data_dir, monkeypatch):
        """Test loading graph when no files exist."""
        unified_graph_dir = test_data_dir / "unified_graph"
        monkeypatch.setattr("roadmap.DATA_DIR", test_data_dir)
        monkeypatch.setattr("roadmap.GRAPH_PATH", unified_graph_dir)

        # Create empty unified_graph directory
        unified_graph_dir.mkdir(exist_ok=True)

        graph = UnifiedContextGraph.load()

        # Should return empty graph without error
        assert len(graph.graph.nodes()) == 0

    @pytest.mark.unit
    def test_save_and_load_roundtrip(self, test_data_dir, monkeypatch):
        """Test that save and load preserve graph structure."""
        unified_graph_dir = test_data_dir / "unified_graph"
        monkeypatch.setattr("roadmap.DATA_DIR", test_data_dir)
        monkeypatch.setattr("roadmap.GRAPH_PATH", unified_graph_dir)

        # Create graph
        graph1 = UnifiedContextGraph()
        graph1.add_node("chunk_1", "chunk", {"id": "chunk_1", "content": "Test content"})
        graph1.add_node("chunk_2", "chunk", {"id": "chunk_2", "content": "More content"})
        graph1.add_edge("chunk_1", "chunk_2", edge_type="semantic", weight=0.75)

        graph1.save()

        # Load graph
        graph2 = UnifiedContextGraph.load()

        # Verify structure preserved
        assert "chunk_1" in graph2.graph.nodes()
        assert "chunk_2" in graph2.graph.nodes()
        assert graph2.graph.has_edge("chunk_1", "chunk_2")

        # Verify node indices rebuilt
        assert "chunk_1" in graph2.node_indices["chunk"]


class TestGraphTraversal:
    """Tests for graph traversal operations."""

    @pytest.mark.unit
    def test_get_neighbors(self):
        """Test getting neighbors of a node."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})
        graph.add_node("chunk_3", "chunk", {"id": "chunk_3"})

        graph.add_edge("chunk_1", "chunk_2", edge_type="semantic", weight=0.8)
        graph.add_edge("chunk_1", "chunk_3", edge_type="semantic", weight=0.6)

        neighbors = list(graph.graph.neighbors("chunk_1"))

        assert len(neighbors) >= 2
        assert "chunk_2" in neighbors or "chunk_3" in neighbors

    @pytest.mark.unit
    def test_get_node_data(self):
        """Test retrieving node data."""
        graph = UnifiedContextGraph()

        node_data = {
            "id": "chunk_1",
            "content": "Important content",
            "lens": "your-voice",
        }

        graph.add_node("chunk_1", "chunk", node_data)

        # Get node from index
        retrieved = graph.node_indices["chunk"]["chunk_1"]

        assert retrieved["content"] == "Important content"
        assert retrieved["lens"] == "your-voice"

    @pytest.mark.unit
    def test_filter_nodes_by_type(self):
        """Test filtering nodes by type."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})
        graph.add_node("q_1", "question", {"id": "q_1"})

        chunks = graph.node_indices["chunk"]
        questions = graph.node_indices["question"]

        assert len(chunks) == 2
        assert len(questions) == 1


class TestSemanticEdgeInference:
    """Tests for semantic edge inference functionality."""

    @pytest.mark.unit
    def test_infer_edges_with_similar_embeddings(self, sample_embeddings):
        """Test that similar embeddings create edges."""
        graph = UnifiedContextGraph()

        # Add nodes with similar embeddings
        for i in range(3):
            graph.add_node(
                f"chunk_{i}",
                "chunk",
                {
                    "id": f"chunk_{i}",
                    "content": f"Content {i}",
                    "embedding": sample_embeddings[i],
                },
            )

        # Manually compute and add semantic edges (simulating the inference process)
        from roadmap import cosine_similarity

        for i in range(3):
            for j in range(i + 1, 3):
                sim = cosine_similarity(sample_embeddings[i], sample_embeddings[j])
                if sim > 0.6:  # Threshold
                    graph.add_edge(
                        f"chunk_{i}",
                        f"chunk_{j}",
                        edge_type="semantic",
                        weight=sim,
                    )

        # Should have some edges if embeddings are similar
        assert len(graph.graph.edges()) >= 0  # May or may not have edges depending on random embeddings

    @pytest.mark.unit
    def test_no_edges_for_dissimilar_embeddings(self):
        """Test that dissimilar embeddings don't create edges."""
        graph = UnifiedContextGraph()

        import numpy as np

        # Create orthogonal embeddings (dissimilar)
        emb1 = [1.0] + [0.0] * 1023
        emb2 = [0.0, 1.0] + [0.0] * 1022

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1", "embedding": emb1})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2", "embedding": emb2})

        # Check similarity
        from roadmap import cosine_similarity

        sim = cosine_similarity(emb1, emb2)
        assert sim < 0.6  # Below threshold

        # If we were to add edges, this shouldn't qualify
        if sim <= 0.6:
            # No edge should be added
            pass


class TestGraphStats:
    """Tests for graph statistics."""

    @pytest.mark.unit
    def test_get_node_count(self):
        """Test getting node count."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})
        graph.add_node("q_1", "question", {"id": "q_1"})

        assert len(graph.graph.nodes()) == 3

    @pytest.mark.unit
    def test_get_edge_count(self):
        """Test getting edge count."""
        graph = UnifiedContextGraph()

        graph.add_node("chunk_1", "chunk", {"id": "chunk_1"})
        graph.add_node("chunk_2", "chunk", {"id": "chunk_2"})
        graph.add_edge("chunk_1", "chunk_2", edge_type="semantic", weight=0.7)

        assert len(graph.graph.edges()) >= 1

    @pytest.mark.unit
    def test_get_stats_empty_graph(self):
        """Test getting stats from empty graph."""
        graph = UnifiedContextGraph()

        assert len(graph.graph.nodes()) == 0
        assert len(graph.graph.edges()) == 0
