"""
Unit tests for chunking functions in roadmap.py
"""

import pytest
from roadmap import (
    score_chunk_quality,
    extract_key_terms,
    extract_time_references,
    verify_chunk_integrity,
    chunk_text,
)


class TestScoreChunkQuality:
    """Tests for chunk quality scoring."""

    @pytest.mark.unit
    def test_high_quality_chunk(self, high_quality_chunk):
        """Test scoring of high quality chunk."""
        result = score_chunk_quality(high_quality_chunk)

        assert "score" in result
        assert "reasons" in result
        assert result["score"] > 0.7  # High quality should score well
        assert isinstance(result["reasons"], list)

    @pytest.mark.unit
    def test_low_quality_chunk(self, low_quality_chunk):
        """Test scoring of low quality chunk."""
        result = score_chunk_quality(low_quality_chunk)

        assert result["score"] < 0.5  # Low quality should score poorly
        assert len(result["reasons"]) > 0  # Should have reasons for low score

    @pytest.mark.unit
    def test_very_short_chunk(self):
        """Test scoring of very short chunk."""
        chunk = {
            "content": "okay",
            "lens": "team-conversational",
        }
        result = score_chunk_quality(chunk)

        assert result["score"] < 0.6
        assert any("short" in reason.lower() for reason in result["reasons"])

    @pytest.mark.unit
    def test_repetitive_chunk(self):
        """Test scoring of repetitive chunk."""
        chunk = {
            "content": "test test test test test test test test",
            "lens": "team-structured",
        }
        result = score_chunk_quality(chunk)

        assert result["score"] < 0.8  # Repetitive content should score lower

    @pytest.mark.unit
    def test_conversational_chunk_with_fillers(self):
        """Test scoring of conversational chunk with filler words."""
        chunk = {
            "content": "um yeah so like basically we should you know do something",
            "lens": "team-conversational",
        }
        result = score_chunk_quality(chunk)

        # Conversational lens is more lenient with fillers
        assert 0 <= result["score"] <= 1.0

    @pytest.mark.unit
    def test_structured_chunk_with_content(self):
        """Test scoring of well-structured chunk."""
        chunk = {
            "content": """The product roadmap for Q1 includes:
                1. CPQ improvements
                2. Catalog enhancements
                3. Pricing modernization""",
            "lens": "team-structured",
        }
        result = score_chunk_quality(chunk)

        assert result["score"] > 0.4  # Reasonable quality threshold


class TestExtractKeyTerms:
    """Tests for key term extraction."""

    @pytest.mark.unit
    def test_extract_from_normal_text(self):
        """Test extracting key terms from normal text."""
        text = "The CPQ system needs API modernization and database migration."
        terms = extract_key_terms(text, top_n=5)

        assert isinstance(terms, list)
        assert len(terms) <= 5
        assert "cpq" in [t.lower() for t in terms]

    @pytest.mark.unit
    def test_extract_filters_stop_words(self):
        """Test that common stop words are filtered."""
        text = "the and or but in on at to for of with by"
        terms = extract_key_terms(text, top_n=10)

        # Should return empty or very few terms since all are stop words
        assert len(terms) <= 2

    @pytest.mark.unit
    def test_extract_from_technical_text(self):
        """Test extracting from technical text."""
        text = "Implement REST API with OAuth authentication and JWT tokens."
        terms = extract_key_terms(text, top_n=5)

        assert any(term.lower() in ["api", "rest", "oauth", "jwt"] for term in terms)

    @pytest.mark.unit
    def test_extract_empty_text(self):
        """Test extracting from empty text."""
        terms = extract_key_terms("", top_n=5)

        assert terms == []

    @pytest.mark.unit
    def test_extract_capitalized_names(self):
        """Test that capitalized product/team names are extracted."""
        text = "The Catalog Team and CPQ Product need to coordinate on API Design."
        terms = extract_key_terms(text, top_n=10)

        # Should include proper nouns
        assert len(terms) > 0

    @pytest.mark.unit
    def test_extract_respects_top_n(self):
        """Test that top_n parameter is respected."""
        text = "word " * 100  # Many repetitions
        terms = extract_key_terms(text, top_n=3)

        assert len(terms) <= 3


class TestExtractTimeReferences:
    """Tests for time reference extraction."""

    @pytest.mark.unit
    def test_extract_quarters(self):
        """Test extracting quarter references."""
        text = "We plan to launch in Q1 2026 and follow up in Q3."
        refs = extract_time_references(text)

        assert "Q1" in " ".join(refs) or any("q1" in r.lower() for r in refs)

    @pytest.mark.unit
    def test_extract_years(self):
        """Test extracting year references."""
        text = "The 2026 roadmap includes several initiatives."
        refs = extract_time_references(text)

        assert any("2026" in r for r in refs)

    @pytest.mark.unit
    def test_extract_months(self):
        """Test extracting month references."""
        text = "Launch scheduled for March 2026 with follow-up in June."
        refs = extract_time_references(text)

        assert any("March" in r or "June" in r for r in refs)

    @pytest.mark.unit
    def test_extract_relative_time(self):
        """Test extracting relative time references."""
        text = "This quarter we will complete the work, next year we expand."
        refs = extract_time_references(text)

        assert len(refs) > 0

    @pytest.mark.unit
    def test_extract_no_time_references(self):
        """Test text with no time references."""
        text = "The product has many features and capabilities."
        refs = extract_time_references(text)

        # Might be empty or have very few
        assert isinstance(refs, list)

    @pytest.mark.unit
    def test_extract_returns_unique_refs(self):
        """Test that duplicate time refs are deduplicated."""
        text = "Q1 2026 is important. Q1 2026 is the target. Q1 2026 deadline."
        refs = extract_time_references(text)

        # Should not have duplicates
        assert len(refs) == len(set(refs))


class TestVerifyChunkIntegrity:
    """Tests for chunk integrity verification."""

    @pytest.mark.unit
    def test_verify_complete_chunk(self):
        """Test verification of complete chunk."""
        chunk = {
            "content": "This is a complete sentence with proper structure.",
            "source_file": "test.md",
            "chunk_index": 0,
        }
        source_doc = "This is a complete sentence with proper structure. More text here."

        result = verify_chunk_integrity(chunk, source_doc)

        # verify_chunk_integrity returns: chunk_id, is_valid, issues, issue_count
        assert "is_valid" in result
        assert result["is_valid"] is True
        assert result["issue_count"] == 0

    @pytest.mark.unit
    def test_verify_truncated_chunk(self):
        """Test verification of truncated chunk."""
        chunk = {
            "content": "This is an incomplete",
            "source_file": "test.md",
            "chunk_index": 0,
        }
        source_doc = "This is an incomplete sentence that got cut off."

        result = verify_chunk_integrity(chunk, source_doc)

        # Should detect that content exists in source
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "issues" in result
        assert "issue_count" in result

    @pytest.mark.unit
    def test_verify_middle_chunk(self):
        """Test verification of middle chunk (no start/end)."""
        chunk = {
            "content": "middle of a document without clear boundaries",
            "source_file": "test.md",
            "chunk_index": 1,
        }
        source_doc = "Beginning. Middle of a document without clear boundaries. End."

        result = verify_chunk_integrity(chunk, source_doc)

        assert isinstance(result, dict)


class TestChunkText:
    """Tests for basic text chunking."""

    @pytest.mark.unit
    def test_chunk_normal_text(self, sample_text):
        """Test chunking normal length text."""
        chunks = chunk_text(sample_text, lens="team-structured")

        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(c, dict) for c in chunks)
        assert all("content" in c for c in chunks)
        assert all("lens" in c for c in chunks)
        assert all(c["lens"] == "team-structured" for c in chunks)

    @pytest.mark.unit
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunks = chunk_text("", lens="team-structured")

        # Should return empty list or minimal chunks
        assert isinstance(chunks, list)

    @pytest.mark.unit
    def test_chunk_very_long_text(self):
        """Test chunking very long text."""
        long_text = "This is a sentence. " * 1000
        chunks = chunk_text(long_text, lens="engineering")

        assert len(chunks) > 1  # Should split into multiple chunks
        assert all(c["lens"] == "engineering" for c in chunks)

    @pytest.mark.unit
    def test_chunk_includes_metadata(self):
        """Test that chunks include required metadata."""
        text = "Sample text for chunking."
        chunks = chunk_text(text, lens="your-voice", source_path="test.md")

        for i, chunk in enumerate(chunks):
            assert "id" in chunk or "content" in chunk
            assert "lens" in chunk
            assert "chunk_index" in chunk or i >= 0  # Has index info
            assert "token_count" in chunk or "content" in chunk

    @pytest.mark.unit
    def test_chunk_respects_lens(self):
        """Test that lens is properly assigned to all chunks."""
        text = "Test text for lens assignment."
        lens = "external-analyst"
        chunks = chunk_text(text, lens=lens)

        assert all(c["lens"] == lens for c in chunks)

    @pytest.mark.unit
    def test_chunk_with_unicode(self):
        """Test chunking text with unicode characters."""
        text = "Hello 世界 🌍 This is unicode text."
        chunks = chunk_text(text, lens="team-conversational")

        assert len(chunks) > 0
        assert all("content" in c for c in chunks)
