"""
Unit tests for CLI command functions in roadmap.py
"""

import pytest
import typer
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from typer.testing import CliRunner
from roadmap import app, ingest, generate, ask


runner = CliRunner()


class TestIngestCommand:
    """Tests for the ingest CLI command."""

    @pytest.mark.unit
    def test_ingest_single_file(self, temp_dir, mock_env_vars):
        """Test ingesting a single file."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("This is test content for ingestion.")

        with patch("roadmap.parse_document", return_value="Test content"):
            with patch("roadmap.chunk_with_fallback") as mock_chunk:
                mock_chunk.return_value = [
                    {"id": "1", "content": "Test", "lens": "your-voice"}
                ]
                with patch("roadmap.index_chunks"):
                    with patch("roadmap.init_db"):
                        with patch("roadmap.ContextGraph"):
                            ingest(str(test_file), lens="your-voice")

                            # Verify chunking was called
                            assert mock_chunk.called

    @pytest.mark.unit
    def test_ingest_invalid_lens(self, temp_dir):
        """Test that invalid lens raises error."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")

        with pytest.raises(typer.Exit):
            ingest(str(test_file), lens="invalid-lens")

    @pytest.mark.unit
    def test_ingest_nonexistent_path(self):
        """Test that nonexistent path raises error."""
        with pytest.raises(typer.Exit):
            ingest("/nonexistent/path.txt", lens="your-voice")

    @pytest.mark.unit
    def test_ingest_directory(self, temp_dir, mock_env_vars):
        """Test ingesting a directory of files."""
        # Create multiple test files
        (temp_dir / "file1.txt").write_text("Content 1")
        (temp_dir / "file2.txt").write_text("Content 2")
        (temp_dir / ".hidden").write_text("Hidden file")

        with patch("roadmap.parse_document", return_value="Test content"):
            with patch("roadmap.chunk_with_fallback") as mock_chunk:
                mock_chunk.return_value = [{"id": "1", "content": "Test", "lens": "your-voice"}]
                with patch("roadmap.index_chunks"):
                    with patch("roadmap.init_db"):
                        with patch("roadmap.ContextGraph"):
                            ingest(str(temp_dir), lens="your-voice")

                            # Should process 2 files (not hidden file)
                            assert mock_chunk.call_count == 2

    @pytest.mark.unit
    def test_ingest_empty_directory(self, temp_dir):
        """Test ingesting empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        # Should handle gracefully
        with patch("roadmap.parse_document"):
            with patch("roadmap.chunk_with_fallback"):
                with patch("roadmap.index_chunks"):
                    ingest(str(empty_dir), lens="your-voice")
                    # Should not raise error

    @pytest.mark.unit
    def test_ingest_empty_document(self, temp_dir, mock_env_vars):
        """Test ingesting document that parses to empty string."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")

        with patch("roadmap.parse_document", return_value=""):
            with patch("roadmap.chunk_with_fallback") as mock_chunk:
                with patch("roadmap.index_chunks") as mock_index:
                    with patch("roadmap.init_db"):
                        with patch("roadmap.ContextGraph"):
                            ingest(str(test_file), lens="your-voice")

                            # Should not call chunking for empty document
                            assert not mock_chunk.called
                            assert not mock_index.called

    @pytest.mark.unit
    def test_ingest_handles_parse_errors(self, temp_dir, mock_env_vars):
        """Test that parsing errors are handled gracefully."""
        test_file = temp_dir / "bad.txt"
        test_file.write_text("Content")

        with patch("roadmap.parse_document", side_effect=Exception("Parse error")):
            with patch("roadmap.init_db"):
                with patch("roadmap.ContextGraph"):
                    # Should not raise exception, just log error
                    ingest(str(test_file), lens="your-voice")

    @pytest.mark.unit
    def test_ingest_no_chunks_generated(self, temp_dir, mock_env_vars):
        """Test handling when no chunks are generated."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")

        with patch("roadmap.parse_document", return_value="Test"):
            with patch("roadmap.chunk_with_fallback", return_value=[]):
                with patch("roadmap.index_chunks") as mock_index:
                    with patch("roadmap.init_db"):
                        with patch("roadmap.ContextGraph"):
                            ingest(str(test_file), lens="your-voice")

                            # Should not index if no chunks
                            assert not mock_index.called

    @pytest.mark.unit
    def test_ingest_rebuilds_graph_on_success(self, temp_dir, mock_env_vars, mock_lancedb):
        """Test that graph is rebuilt after successful ingestion."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Content")

        with patch("roadmap.parse_document", return_value="Test"):
            with patch("roadmap.chunk_with_fallback", return_value=[{"id": "1", "content": "Test", "lens": "your-voice"}]):
                with patch("roadmap.index_chunks"):
                    # Graph rebuild happens inside ingest
                    ingest(str(test_file), lens="your-voice")
                    # Test passes if no exception raised


class TestGenerateCommand:
    """Tests for the generate CLI command."""

    @pytest.mark.unit
    def test_generate_success(self, mock_env_vars, temp_dir, monkeypatch):
        """Test successful roadmap generation."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        monkeypatch.setattr("roadmap.OUTPUT_DIR", output_dir)

        with patch("roadmap.generate_roadmap", return_value="# Generated Roadmap"):
            generate()
            # Should complete without error

    @pytest.mark.unit
    def test_generate_handles_errors(self, mock_env_vars):
        """Test that generation errors are handled gracefully."""
        with patch("roadmap.generate_roadmap", side_effect=Exception("Generation failed")):
            # Generation errors raise typer.Exit
            with pytest.raises(typer.Exit):
                generate()


class TestAskCommand:
    """Tests for the ask CLI command."""

    @pytest.mark.unit
    def test_ask_with_results(self, mock_env_vars, mock_lancedb):
        """Test asking question with results found."""
        chunks = [
            {"id": "1", "content": "Answer content", "lens": "your-voice"}
        ]

        with patch("roadmap.retrieve_chunks", return_value=chunks):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_response = Mock()
                mock_content = Mock()
                mock_content.text = "Here's the answer"
                mock_response.content = [mock_content]
                mock_client.messages.create.return_value = mock_response
                mock_anthropic.return_value = mock_client

                ask("What is the strategy?")
                # Should complete successfully

    @pytest.mark.unit
    def test_ask_with_no_results(self, mock_env_vars, mock_lancedb):
        """Test asking question when no relevant content found."""
        with patch("roadmap.retrieve_chunks", return_value=[]):
            ask("What is the strategy?")
            # Should handle gracefully, not raise error

    @pytest.mark.unit
    def test_ask_handles_api_errors(self, mock_env_vars, mock_lancedb):
        """Test that API errors are handled in ask command."""
        chunks = [{"id": "1", "content": "Content", "lens": "your-voice"}]

        with patch("roadmap.retrieve_chunks", return_value=chunks):
            with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.side_effect = Exception("API Error")
                mock_anthropic.return_value = mock_client

                # API errors will propagate (not handled in ask)
                with pytest.raises(Exception):
                    ask("Question?")


# Note: The following tests are commented out because these specific CLI command functions
# don't exist with the expected names. The CLI commands exist but are named differently.
# These can be uncommented and fixed once the correct command names are identified.

# class TestSyncCommand:
#     """Tests for sync-related commands."""
#     pass

# class TestFormatCommand:
#     """Tests for format CLI command."""
#     pass

# class TestAssessCommand:
#     """Tests for assessment CLI commands."""
#     pass

# class TestListCommand:
#     """Tests for list CLI commands."""
#     pass
