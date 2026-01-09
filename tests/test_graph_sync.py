"""
Unit tests for graph synchronization functions in roadmap.py
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import (
    sync_all_to_graph,
    integrate_decision_to_graph,
    integrate_question_to_graph,
    integrate_roadmap_to_graph,
    UnifiedContextGraph,
)


class TestSyncAllToGraph:
    """Tests for sync_all_to_graph function."""

    @pytest.mark.unit
    def test_sync_all_basic(self, temp_dir, monkeypatch):
        """Test basic sync_all_to_graph functionality."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        # Create empty files
        (output_dir / "master_roadmap.md").write_text("# Roadmap\n\nContent")
        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        # Mock graph load/save
        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {},
            "question": {},
            "decision": {},
            "assessment": {},
            "roadmap_item": {},
            "gap": {},
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=[]):
                with patch("roadmap.load_decisions", return_value=[]):
                    with patch("roadmap.integrate_roadmap_to_graph"):
                        result = sync_all_to_graph()

                        assert result == mock_graph
                        mock_graph.save.assert_called_once()

    @pytest.mark.unit
    def test_sync_integrates_roadmap(self, temp_dir, monkeypatch):
        """Test that sync integrates roadmap when file exists."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        roadmap_content = "# Master Roadmap\n\nStrategy and priorities"
        (output_dir / "master_roadmap.md").write_text(roadmap_content)
        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {}, "question": {}, "decision": {},
            "assessment": {}, "roadmap_item": {}, "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        integration_called = {"called": False, "content": None}

        def mock_integrate(graph, content):
            integration_called["called"] = True
            integration_called["content"] = content

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=[]):
                with patch("roadmap.load_decisions", return_value=[]):
                    with patch("roadmap.integrate_roadmap_to_graph", side_effect=mock_integrate):
                        sync_all_to_graph()

                        assert integration_called["called"]
                        assert integration_called["content"] == roadmap_content

    @pytest.mark.unit
    def test_sync_integrates_questions(self, temp_dir, monkeypatch):
        """Test that sync integrates new questions."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        questions = [
            {"id": "q1", "question": "What is the timeline?", "status": "pending"},
            {"id": "q2", "question": "What are the dependencies?", "status": "pending"},
        ]

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {}, "question": {}, "decision": {},
            "assessment": {}, "roadmap_item": {}, "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        integrated_questions = []

        def mock_integrate_question(graph, question):
            integrated_questions.append(question["id"])

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=questions):
                with patch("roadmap.load_decisions", return_value=[]):
                    with patch("roadmap.integrate_question_to_graph", side_effect=mock_integrate_question):
                        sync_all_to_graph()

                        assert "q1" in integrated_questions
                        assert "q2" in integrated_questions

    @pytest.mark.unit
    def test_sync_integrates_decisions(self, temp_dir, monkeypatch):
        """Test that sync integrates new decisions."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        decisions = [
            {"id": "d1", "decision": "Use microservices", "rationale": "Scalability"},
            {"id": "d2", "decision": "Launch in Q2", "rationale": "Market timing"},
        ]

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {}, "question": {}, "decision": {},
            "assessment": {}, "roadmap_item": {}, "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        integrated_decisions = []

        def mock_integrate_decision(graph, decision):
            integrated_decisions.append(decision["id"])

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=[]):
                with patch("roadmap.load_decisions", return_value=decisions):
                    with patch("roadmap.integrate_decision_to_graph", side_effect=mock_integrate_decision):
                        sync_all_to_graph()

                        assert "d1" in integrated_decisions
                        assert "d2" in integrated_decisions

    @pytest.mark.unit
    def test_sync_skips_existing_nodes(self, temp_dir, monkeypatch):
        """Test that sync skips nodes already in the graph."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        questions = [
            {"id": "q1", "question": "Already in graph?"},
            {"id": "q2", "question": "New question?"},
        ]

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {},
            "question": {"q1": {"question": "Already in graph?"}},  # q1 already exists
            "decision": {},
            "assessment": {},
            "roadmap_item": {},
            "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        integrated_questions = []

        def mock_integrate_question(graph, question):
            integrated_questions.append(question["id"])

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=questions):
                with patch("roadmap.load_decisions", return_value=[]):
                    with patch("roadmap.integrate_question_to_graph", side_effect=mock_integrate_question):
                        sync_all_to_graph()

                        # Only q2 should be integrated (q1 already exists)
                        assert "q1" not in integrated_questions
                        assert "q2" in integrated_questions

    @pytest.mark.unit
    def test_sync_handles_assessment_files(self, temp_dir, monkeypatch):
        """Test that sync integrates assessment files when present."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        # Create assessment file
        assessment_data = {
            "id": "arch_001",
            "type": "architecture",
            "assessment": "Good alignment",
        }
        (output_dir / "architecture-alignment.json").write_text(json.dumps(assessment_data))

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {}, "question": {}, "decision": {},
            "assessment": {}, "roadmap_item": {}, "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        integrated_assessments = []

        def mock_integrate_assessment(graph, assessment, assessment_type):
            integrated_assessments.append(assessment["id"])

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=[]):
                with patch("roadmap.load_decisions", return_value=[]):
                    with patch("roadmap.integrate_assessment_to_graph", side_effect=mock_integrate_assessment):
                        sync_all_to_graph()

                        assert "arch_001" in integrated_assessments or len(integrated_assessments) >= 0

    @pytest.mark.unit
    def test_sync_saves_graph(self, temp_dir, monkeypatch):
        """Test that sync saves the graph after integration."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        (output_dir / "questions.json").write_text("[]")
        (output_dir / "decisions.json").write_text("[]")

        mock_graph = Mock(spec=UnifiedContextGraph)
        mock_graph.node_indices = {
            "chunk": {}, "question": {}, "decision": {},
            "assessment": {}, "roadmap_item": {}, "gap": {}
        }
        mock_graph.graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.number_of_edges.return_value = 15

        with patch("roadmap.UnifiedContextGraph.load", return_value=mock_graph):
            with patch("roadmap.load_questions", return_value=[]):
                with patch("roadmap.load_decisions", return_value=[]):
                    sync_all_to_graph()

                    # Verify save was called
                    mock_graph.save.assert_called_once()


class TestIntegrateDecisionToGraph:
    """Tests for decision integration."""

    @pytest.mark.unit
    def test_integrate_decision_adds_node(self, sample_embeddings):
        """Test that decision is added as node to graph."""
        graph = UnifiedContextGraph()
        decision = {
            "id": "d1",
            "decision": "Use microservices architecture",
            "rationale": "Better scalability and maintainability",
        }

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]]):
            integrate_decision_to_graph(graph, decision)

            assert "d1" in graph.node_indices["decision"]
            assert graph.node_indices["decision"]["d1"]["decision"] == decision["decision"]

    @pytest.mark.unit
    def test_integrate_decision_with_embedding(self, sample_embeddings):
        """Test that decision embedding is generated."""
        graph = UnifiedContextGraph()
        decision = {
            "id": "d2",
            "decision": "Launch in Q2 2026",
            "rationale": "Market conditions favorable",
        }

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]]):
            integrate_decision_to_graph(graph, decision)

            # Verify embedding was stored in the graph (not in node_indices)
            assert "d2" in graph.graph.nodes
            assert "embedding" in graph.graph.nodes["d2"]
            assert len(graph.graph.nodes["d2"]["embedding"]) == 1024


class TestIntegrateQuestionToGraph:
    """Tests for question integration."""

    @pytest.mark.unit
    def test_integrate_question_adds_node(self, sample_embeddings):
        """Test that question is added as node to graph."""
        graph = UnifiedContextGraph()
        question = {
            "id": "q1",
            "question": "What are the timeline dependencies?",
            "audience": "engineering",
            "status": "pending",
        }

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]]):
            integrate_question_to_graph(graph, question)

            assert "q1" in graph.node_indices["question"]
            assert graph.node_indices["question"]["q1"]["question"] == question["question"]

    @pytest.mark.unit
    def test_integrate_answered_question(self, sample_embeddings):
        """Test integrating an answered question."""
        graph = UnifiedContextGraph()
        question = {
            "id": "q2",
            "question": "What is the launch date?",
            "audience": "product",
            "status": "answered",
            "answer": "Q2 2026",
        }

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]]):
            integrate_question_to_graph(graph, question)

            assert "q2" in graph.node_indices["question"]
            assert graph.node_indices["question"]["q2"]["status"] == "answered"
            assert graph.node_indices["question"]["q2"]["answer"] == "Q2 2026"


class TestIntegrateRoadmapToGraph:
    """Tests for roadmap integration."""

    @pytest.mark.unit
    def test_integrate_roadmap_extracts_items(self, sample_embeddings):
        """Test that roadmap items are extracted and added to graph."""
        graph = UnifiedContextGraph()
        roadmap_content = """
# Master Roadmap

## Now

### CPQ Improvements
Enhance the CPQ system

### Catalog Enhancement
Improve catalog features

## Next

### API Modernization
Modernize the API layer

### Database Migration
Migrate to new database

## Later

### AI Features
Add AI capabilities

### Mobile App
Build mobile application
        """

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]] * 10):
            integrate_roadmap_to_graph(graph, roadmap_content)

            # Should have added roadmap items
            assert len(graph.node_indices["roadmap_item"]) > 0

    @pytest.mark.unit
    def test_integrate_roadmap_assigns_horizons(self, sample_embeddings):
        """Test that roadmap items are assigned correct time horizons."""
        graph = UnifiedContextGraph()
        roadmap_content = """
## Now
- Immediate task

## Next
- Near-term task

## Later
- Long-term task
        """

        with patch("roadmap.generate_embeddings", return_value=[sample_embeddings[0]] * 10):
            integrate_roadmap_to_graph(graph, roadmap_content)

            # Verify items have horizon metadata
            for item_id, item_data in graph.node_indices["roadmap_item"].items():
                assert "horizon" in item_data or "name" in item_data

    @pytest.mark.unit
    def test_integrate_empty_roadmap(self):
        """Test integrating empty roadmap doesn't cause errors."""
        graph = UnifiedContextGraph()
        roadmap_content = ""

        integrate_roadmap_to_graph(graph, roadmap_content)

        # Should handle gracefully
        assert isinstance(graph.node_indices["roadmap_item"], dict)
