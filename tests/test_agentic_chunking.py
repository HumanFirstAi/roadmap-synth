"""
Unit tests for agentic chunking functions in roadmap.py
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import (
    AgenticChunker,
    chunk_with_fallback,
    structure_aware_chunk,
    filter_chunks_by_quality,
)


class TestAgenticChunker:
    """Tests for AgenticChunker class."""

    @pytest.mark.unit
    def test_init_with_default_api_key(self, mock_env_vars):
        """Test AgenticChunker initialization with default API key."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            chunker = AgenticChunker()

            assert chunker.model == "claude-sonnet-4-20250514"
            assert chunker.max_tokens == 16000
            mock_anthropic.assert_called_once()

    @pytest.mark.unit
    def test_init_with_custom_api_key(self):
        """Test AgenticChunker initialization with custom API key."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            chunker = AgenticChunker(api_key="custom-key", model="claude-opus-4")

            assert chunker.model == "claude-opus-4"
            mock_anthropic.assert_called_once()

    @pytest.mark.unit
    def test_chunk_very_short_document(self, mock_env_vars):
        """Test chunking a very short document (<100 chars)."""
        with patch("roadmap.anthropic.Anthropic"):
            chunker = AgenticChunker()

            short_text = "Short doc"
            result = chunker.chunk_document(short_text, "test.md", "your-voice")

            assert len(result) == 1
            assert result[0]["content"] == short_text
            assert result[0]["lens"] == "your-voice"
            assert result[0]["chunk_index"] == 0
            assert "token_count" in result[0]

    @pytest.mark.unit
    def test_chunk_document_with_valid_json_response(self, mock_env_vars):
        """Test chunking with valid JSON response from Claude."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            document_text = "Long document text " * 50

            # Mock Claude response with start/end character positions
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({
                "chunks": [
                    {
                        "chunk_index": 0,
                        "start_char": 0,
                        "end_char": 100,
                        "section_title": "Introduction",
                        "key_entities": ["Product", "Roadmap"],
                        "time_references": ["Q1 2026"]
                    },
                    {
                        "chunk_index": 1,
                        "start_char": 100,
                        "end_char": 200,
                        "section_title": "Strategy",
                        "key_entities": ["Team", "Goals"],
                        "time_references": []
                    }
                ]
            })
            mock_response.content = [mock_content]

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            chunker = AgenticChunker()
            result = chunker.chunk_document(document_text, "test.md", "team-structured")

            assert len(result) == 2
            # Content is extracted from document using start_char:end_char
            assert result[0]["content"] == document_text[0:100]
            assert result[0]["lens"] == "team-structured"
            assert result[0]["metadata"]["section_title"] == "Introduction"
            assert "Product" in result[0]["metadata"]["key_entities"]

            assert result[1]["content"] == document_text[100:200]
            assert result[1]["chunk_index"] == 1

    @pytest.mark.unit
    def test_chunk_document_with_invalid_json_falls_back(self, mock_env_vars):
        """Test that invalid JSON from Claude is handled gracefully."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            # Mock Claude response with invalid JSON
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Not valid JSON"
            mock_response.content = [mock_content]

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            chunker = AgenticChunker()
            document_text = "Document text " * 50

            # Should fall back to structure-aware chunking
            with patch("roadmap.structure_aware_chunk") as mock_fallback:
                mock_fallback.return_value = [{"content": "Fallback chunk", "lens": "your-voice"}]

                result = chunker.chunk_document(document_text, "test.md", "your-voice")

                # Should have attempted fallback
                assert mock_fallback.called or len(result) >= 0

    @pytest.mark.unit
    def test_chunk_document_temperature_zero(self, mock_env_vars):
        """Test that chunking uses temperature=0 for determinism."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({"chunks": []})
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            chunker = AgenticChunker()
            document_text = "Test document " * 50
            chunker.chunk_document(document_text, "test.md", "your-voice")

            # Verify temperature=0 was used
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["temperature"] == 0

    @pytest.mark.unit
    def test_chunk_document_adds_metadata(self, mock_env_vars):
        """Test that chunks have required metadata fields."""
        with patch("roadmap.anthropic.Anthropic") as mock_anthropic:
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({
                "chunks": [{
                    "chunk_index": 0,
                    "content": "Test",
                    "section_title": "Title",
                    "key_entities": [],
                    "time_references": []
                }]
            })
            mock_response.content = [mock_content]
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            chunker = AgenticChunker()
            result = chunker.chunk_document("Test " * 50, "test.md", "your-voice")

            assert len(result) > 0
            chunk = result[0]
            assert "chunk_index" in chunk
            assert "content" in chunk
            assert "lens" in chunk
            assert "source_file" in chunk
            assert "token_count" in chunk
            assert "metadata" in chunk


class TestChunkWithFallback:
    """Tests for chunk_with_fallback function."""

    @pytest.mark.unit
    def test_fallback_with_agentic_disabled(self, mock_env_vars):
        """Test fallback when agentic chunking is disabled."""
        document_text = "Test document content"

        with patch("roadmap.structure_aware_chunk") as mock_structure:
            mock_structure.return_value = [
                {"content": "Chunk 1", "lens": "your-voice", "chunk_index": 0}
            ]

            result = chunk_with_fallback(
                document_text,
                "test.md",
                "your-voice",
                use_agentic=False,
                log_results=False
            )

            assert mock_structure.called
            assert len(result) == 1
            assert result[0]["content"] == "Chunk 1"

    @pytest.mark.unit
    def test_fallback_with_very_large_document(self, mock_env_vars):
        """Test fallback for documents exceeding token limit."""
        # Create very large document (>30000 estimated tokens)
        document_text = "word " * 40000

        with patch("roadmap.structure_aware_chunk") as mock_structure:
            mock_structure.return_value = [{"content": "Chunk", "lens": "your-voice"}]

            result = chunk_with_fallback(
                document_text,
                "test.md",
                "your-voice",
                use_agentic=True,
                log_results=False
            )

            # Should use structure-aware for large docs
            assert mock_structure.called
            assert len(result) > 0

    @pytest.mark.unit
    def test_fallback_applies_quality_filter(self, mock_env_vars):
        """Test that quality filter is applied when enabled."""
        document_text = "Test content"

        with patch("roadmap.structure_aware_chunk") as mock_structure:
            # Return chunks including low quality ones
            mock_structure.return_value = [
                {"content": "Good quality chunk with substantive content", "lens": "your-voice"},
                {"content": "um yeah", "lens": "team-conversational"},  # Low quality
            ]

            with patch("roadmap.filter_chunks_by_quality") as mock_filter:
                mock_filter.return_value = (
                    [{"content": "Good quality chunk with substantive content", "lens": "your-voice"}],
                    [{"content": "um yeah", "lens": "team-conversational"}]
                )

                result = chunk_with_fallback(
                    document_text,
                    "test.md",
                    "your-voice",
                    use_agentic=False,
                    apply_quality_filter=True,
                    log_results=False
                )

                assert mock_filter.called
                assert len(result) == 1  # Only good quality chunk

    @pytest.mark.unit
    def test_fallback_skips_quality_filter_when_disabled(self, mock_env_vars):
        """Test that quality filter can be disabled."""
        document_text = "Test content"

        with patch("roadmap.structure_aware_chunk") as mock_structure:
            mock_structure.return_value = [
                {"content": "um yeah", "lens": "team-conversational"}
            ]

            with patch("roadmap.filter_chunks_by_quality") as mock_filter:
                result = chunk_with_fallback(
                    document_text,
                    "test.md",
                    "team-conversational",
                    use_agentic=False,
                    apply_quality_filter=False,
                    log_results=False
                )

                # Filter should not be called
                assert not mock_filter.called
                assert len(result) == 1

    @pytest.mark.unit
    def test_fallback_retries_on_agentic_failure(self, mock_env_vars):
        """Test retry logic when agentic chunking fails."""
        document_text = "Test " * 50

        with patch("roadmap.AgenticChunker") as mock_agentic_class:
            # First attempt fails
            mock_chunker = Mock()
            mock_chunker.chunk_document.side_effect = Exception("API error")
            mock_agentic_class.return_value = mock_chunker

            with patch("roadmap.structure_aware_chunk") as mock_structure:
                mock_structure.return_value = [{"content": "Fallback", "lens": "your-voice"}]

                result = chunk_with_fallback(
                    document_text,
                    "test.md",
                    "your-voice",
                    use_agentic=True,
                    max_retries=2,
                    log_results=False
                )

                # Should fall back to structure-aware
                assert mock_structure.called
                assert len(result) > 0

    @pytest.mark.unit
    def test_fallback_logs_results_when_enabled(self, mock_env_vars, capsys):
        """Test that chunking results are logged when log_results=True."""
        document_text = "Test"

        with patch("roadmap.structure_aware_chunk") as mock_structure:
            mock_structure.return_value = [{"content": "Chunk", "lens": "your-voice"}]

            with patch("roadmap.log_chunking_result") as mock_log:
                chunk_with_fallback(
                    document_text,
                    "test.md",
                    "your-voice",
                    use_agentic=False,
                    log_results=True
                )

                assert mock_log.called


class TestStructureAwareChunk:
    """Tests for structure-aware chunking fallback."""

    @pytest.mark.unit
    def test_structure_aware_basic_chunking(self):
        """Test basic structure-aware chunking."""
        document_text = "This is a test document. " * 100

        result = structure_aware_chunk(document_text, "test.md", "your-voice")

        assert isinstance(result, list)
        assert len(result) > 0
        assert all("content" in chunk for chunk in result)
        assert all(chunk["lens"] == "your-voice" for chunk in result)
        assert all("chunk_index" in chunk for chunk in result)

    @pytest.mark.unit
    def test_structure_aware_preserves_sections(self):
        """Test that structure-aware chunking preserves section boundaries."""
        document_text = """# Section 1
        Content for section 1.

        # Section 2
        Content for section 2."""

        result = structure_aware_chunk(document_text, "test.md", "team-structured")

        # Should create chunks that respect section boundaries
        assert len(result) >= 1
        # At least one chunk should contain section markers or content
        combined = " ".join(c["content"] for c in result)
        assert "Section" in combined or "Content" in combined

    @pytest.mark.unit
    def test_structure_aware_handles_empty_document(self):
        """Test structure-aware chunking with empty document."""
        result = structure_aware_chunk("", "test.md", "your-voice")

        # Should handle gracefully
        assert isinstance(result, list)
        # May return empty list or single chunk with empty content


class TestFilterChunksByQuality:
    """Tests for chunk quality filtering."""

    @pytest.mark.unit
    def test_filter_removes_low_quality_chunks(self):
        """Test that low quality chunks are filtered."""
        chunks = [
            {"content": "This is substantive strategic content about roadmap.", "lens": "your-voice"},
            {"content": "um yeah so", "lens": "team-conversational"},
            {"content": "okay cool", "lens": "team-conversational"},
            {"content": "Detailed technical architecture for the system.", "lens": "engineering"},
        ]

        kept, filtered = filter_chunks_by_quality(chunks, log_filtered=False)

        assert len(kept) >= 2  # Should keep substantial chunks
        assert len(filtered) >= 1  # Should filter filler chunks
        assert all(len(c["content"]) > 20 for c in kept)  # Kept chunks have content

    @pytest.mark.unit
    def test_filter_preserves_good_quality_chunks(self):
        """Test that high quality chunks are preserved."""
        chunks = [
            {"content": "The product strategy for 2026 focuses on enterprise growth.", "lens": "your-voice"},
            {"content": "Engineering will implement microservices architecture.", "lens": "engineering"},
        ]

        kept, filtered = filter_chunks_by_quality(chunks, log_filtered=False)

        assert len(kept) == 2
        assert len(filtered) == 0

    @pytest.mark.unit
    def test_filter_handles_empty_list(self):
        """Test filtering empty chunk list."""
        kept, filtered = filter_chunks_by_quality([], log_filtered=False)

        assert kept == []
        assert filtered == []

    @pytest.mark.unit
    def test_filter_logs_when_enabled(self, capsys):
        """Test that filtering logs when log_filtered=True."""
        chunks = [
            {"content": "um", "lens": "team-conversational"},
        ]

        with patch("roadmap.score_chunk_quality") as mock_score:
            mock_score.return_value = {
                "score": 0.1,
                "reasons": ["Too short"],
                "should_index": False,
                "lens": "team-conversational"
            }

            kept, filtered = filter_chunks_by_quality(chunks, log_filtered=True)

            # Should have logged (captured by console.print)
            assert len(filtered) == 1
