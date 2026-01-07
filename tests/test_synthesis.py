"""
Unit tests for roadmap synthesis and formatting functions in roadmap.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import generate_roadmap, format_for_persona, load_prompt


class TestGenerateRoadmap:
    """Tests for roadmap generation."""

    @pytest.mark.unit
    def test_generate_roadmap_basic(self, mock_env_vars, mock_lancedb, temp_dir, monkeypatch):
        """Test basic roadmap generation."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        # Mock graph with proper nodes structure
        mock_graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 10
        mock_graph.graph.nodes = {}  # Make nodes a dict for "in" checks
        mock_graph.load.return_value = mock_graph

        # Mock retrieval with at least one chunk
        mock_chunks = [
            {"id": "1", "content": "Strategic vision", "lens": "your-voice"},
            {"id": "2", "content": "Technical details", "lens": "engineering"},
        ]

        # Mock Claude response
        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "# Generated Roadmap\n\nThis is the master roadmap."
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.ContextGraph", return_value=mock_graph):
            with patch("roadmap.retrieve_balanced", return_value=mock_chunks):
                with patch("roadmap.retrieve_with_graph_expansion", return_value=mock_chunks):
                    with patch("roadmap.detect_potential_contradictions", return_value=[]):
                        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                            mock_client = Mock()
                            mock_client.messages.create.return_value = mock_anthropic_response
                            mock_anthropic.return_value = mock_client

                            result = generate_roadmap()

                            assert isinstance(result, str)
                            assert "Roadmap" in result or "roadmap" in result
                            mock_client.messages.create.assert_called_once()

    @pytest.mark.unit
    def test_generate_roadmap_uses_multiple_queries(self, mock_env_vars, mock_lancedb, temp_dir, monkeypatch):
        """Test that generation uses multiple query perspectives."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        mock_graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 5
        mock_graph.load.return_value = mock_graph

        call_count = {"count": 0}

        def mock_retrieve_balanced(query, chunks_per_lens):
            call_count["count"] += 1
            return [{"id": str(call_count["count"]), "content": query, "lens": "your-voice"}]

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Roadmap content"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.ContextGraph", return_value=mock_graph):
            with patch("roadmap.retrieve_balanced", side_effect=mock_retrieve_balanced):
                with patch("roadmap.retrieve_with_graph_expansion", return_value=[]):
                    with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                        mock_client = Mock()
                        mock_client.messages.create.return_value = mock_anthropic_response
                        mock_anthropic.return_value = mock_client

                        generate_roadmap()

                        # Should have called retrieve_balanced multiple times
                        assert call_count["count"] >= 3  # At least a few query perspectives

    @pytest.mark.unit
    def test_generate_roadmap_expands_via_graph(self, mock_env_vars, mock_lancedb, temp_dir, monkeypatch):
        """Test that generation expands context via graph when available."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        mock_graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 20  # Non-empty graph

        expansion_called = {"called": False}

        def mock_expansion(*args, **kwargs):
            expansion_called["called"] = True
            return [{"id": "expanded", "content": "Expanded content", "lens": "your-voice"}]

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Roadmap"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.ContextGraph") as mock_graph_class:
            mock_graph_instance = Mock()
            mock_graph_instance.graph.number_of_nodes.return_value = 20
            mock_graph_instance.load.return_value = mock_graph_instance
            mock_graph_class.return_value = mock_graph_instance

            with patch("roadmap.retrieve_balanced", return_value=[]):
                with patch("roadmap.retrieve_with_graph_expansion", side_effect=mock_expansion):
                    with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                        mock_client = Mock()
                        mock_client.messages.create.return_value = mock_anthropic_response
                        mock_anthropic.return_value = mock_client

                        generate_roadmap()

                        # Graph expansion should have been called
                        assert expansion_called["called"]

    @pytest.mark.unit
    def test_generate_roadmap_saves_to_file(self, mock_env_vars, mock_lancedb, temp_dir, monkeypatch):
        """Test that generated roadmap is saved to file."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        mock_graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 0
        mock_graph.load.return_value = mock_graph

        generated_content = "# Master Roadmap\n\nContent here"

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = generated_content
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.ContextGraph", return_value=mock_graph):
            with patch("roadmap.retrieve_balanced", return_value=[]):
                with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                    mock_client = Mock()
                    mock_client.messages.create.return_value = mock_anthropic_response
                    mock_anthropic.return_value = mock_client

                    result = generate_roadmap()

                    assert result == generated_content

                    # Verify file was saved
                    saved_file = output_dir / "master_roadmap.md"
                    assert saved_file.exists()
                    assert saved_file.read_text() == generated_content

    @pytest.mark.unit
    def test_generate_roadmap_with_custom_query(self, mock_env_vars, mock_lancedb, temp_dir, monkeypatch):
        """Test roadmap generation with custom query."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        mock_graph = Mock()
        mock_graph.graph.number_of_nodes.return_value = 0
        mock_graph.load.return_value = mock_graph

        custom_query = "Focus on Q1 priorities"

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Custom roadmap"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.ContextGraph", return_value=mock_graph):
            with patch("roadmap.retrieve_balanced", return_value=[]):
                with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                    mock_client = Mock()
                    mock_client.messages.create.return_value = mock_anthropic_response
                    mock_anthropic.return_value = mock_client

                    result = generate_roadmap(query=custom_query)

                    assert result == "Custom roadmap"


class TestFormatForPersona:
    """Tests for persona-specific formatting."""

    @pytest.mark.unit
    def test_format_for_persona_with_provided_roadmap(self, mock_env_vars, temp_dir, monkeypatch):
        """Test formatting with provided master roadmap."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        master_roadmap = "# Master Roadmap\n\nDetailed content"
        persona_prompt = "You are formatting for executives."

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "# Executive Summary\n\nHigh-level view"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.load_prompt", return_value=persona_prompt):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.return_value = mock_anthropic_response
                mock_anthropic.return_value = mock_client

                result = format_for_persona("executive", master_roadmap=master_roadmap)

                assert isinstance(result, str)
                assert "Executive" in result or "executive" in result or "Summary" in result

                # Verify file was saved
                saved_file = temp_dir / "output" / "executive_roadmap.md"
                assert saved_file.exists()

    @pytest.mark.unit
    def test_format_for_persona_loads_from_file(self, mock_env_vars, temp_dir, monkeypatch):
        """Test formatting loads master roadmap from file if not provided."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        # Create master roadmap file
        master_content = "# Master Roadmap\n\nContent"
        (output_dir / "master_roadmap.md").write_text(master_content)

        persona_prompt = "Format for product managers."

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "# Product Roadmap\n\nDetailed features"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.load_prompt", return_value=persona_prompt):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.return_value = mock_anthropic_response
                mock_anthropic.return_value = mock_client

                result = format_for_persona("product")

                assert "Product Roadmap" in result

    @pytest.mark.unit
    def test_format_for_persona_fails_without_master_roadmap(self, mock_env_vars, temp_dir, monkeypatch):
        """Test that formatting fails if master roadmap doesn't exist."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        # No master roadmap file exists

        with pytest.raises(Exception):  # Could be typer.Exit or FileNotFoundError
            format_for_persona("executive")

    @pytest.mark.unit
    def test_format_for_persona_uses_correct_prompt(self, mock_env_vars, temp_dir, monkeypatch):
        """Test that correct persona prompt is loaded."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        master_roadmap = "Master content"
        loaded_prompts = {}

        def mock_load_prompt(path):
            loaded_prompts[path] = True
            return f"Prompt for {path}"

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Formatted output"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.load_prompt", side_effect=mock_load_prompt):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.return_value = mock_anthropic_response
                mock_anthropic.return_value = mock_client

                format_for_persona("engineering", master_roadmap=master_roadmap)

                # Verify engineering persona prompt was loaded
                assert "personas/engineering.md" in loaded_prompts

    @pytest.mark.unit
    def test_format_for_persona_all_personas(self, mock_env_vars, temp_dir, monkeypatch):
        """Test formatting for all available personas."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        master_roadmap = "Master content"
        personas = ["executive", "product", "engineering"]

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Formatted"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.load_prompt", return_value="Prompt"):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.return_value = mock_anthropic_response
                mock_anthropic.return_value = mock_client

                for persona in personas:
                    result = format_for_persona(persona, master_roadmap=master_roadmap)
                    assert isinstance(result, str)

                    # Verify file was saved for each persona
                    saved_file = temp_dir / "output" / f"{persona}_roadmap.md"
                    assert saved_file.exists()

    @pytest.mark.unit
    def test_format_for_persona_uses_opus_model(self, mock_env_vars, temp_dir, monkeypatch):
        """Test that formatting uses Claude Opus 4.5 model."""
        monkeypatch.setattr("roadmap.OUTPUT_DIR", temp_dir / "output")
        (temp_dir / "output").mkdir()

        master_roadmap = "Content"

        mock_anthropic_response = Mock()
        mock_content = Mock()
        mock_content.text = "Formatted"
        mock_anthropic_response.content = [mock_content]

        with patch("roadmap.load_prompt", return_value="Prompt"):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.return_value = mock_anthropic_response
                mock_anthropic.return_value = mock_client

                format_for_persona("executive", master_roadmap=master_roadmap)

                # Verify Opus model was used
                call_kwargs = mock_client.messages.create.call_args[1]
                assert call_kwargs["model"] == "claude-opus-4-5-20251101"


class TestLoadPrompt:
    """Tests for prompt loading utility."""

    @pytest.mark.unit
    def test_load_prompt_reads_file(self, temp_dir, monkeypatch):
        """Test that load_prompt reads prompt file."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        monkeypatch.setattr("roadmap.PROMPTS_DIR", prompts_dir)

        prompt_file = prompts_dir / "test.md"
        prompt_content = "This is a test prompt."
        prompt_file.write_text(prompt_content)

        result = load_prompt("test.md")

        assert result == prompt_content

    @pytest.mark.unit
    def test_load_prompt_handles_subdirectories(self, temp_dir, monkeypatch):
        """Test loading prompts from subdirectories."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        personas_dir = prompts_dir / "personas"
        personas_dir.mkdir()
        monkeypatch.setattr("roadmap.PROMPTS_DIR", prompts_dir)

        prompt_file = personas_dir / "executive.md"
        prompt_content = "Executive formatting prompt."
        prompt_file.write_text(prompt_content)

        result = load_prompt("personas/executive.md")

        assert result == prompt_content

    @pytest.mark.unit
    def test_load_prompt_handles_missing_file(self, temp_dir, monkeypatch):
        """Test that load_prompt handles missing file appropriately."""
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        monkeypatch.setattr("roadmap.PROMPTS_DIR", prompts_dir)

        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent.md")
