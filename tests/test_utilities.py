"""
Unit tests for utility functions in roadmap.py
"""

import pytest
import numpy as np
import typer
from roadmap import count_tokens, cosine_similarity, validate_api_keys


class TestCountTokens:
    """Tests for token counting function."""

    @pytest.mark.unit
    def test_count_tokens_normal_text(self):
        """Test counting tokens in normal text."""
        text = "Hello world, this is a test."
        count = count_tokens(text)
        assert count > 0
        assert isinstance(count, int)

    @pytest.mark.unit
    def test_count_tokens_empty_string(self):
        """Test counting tokens in empty string."""
        count = count_tokens("")
        assert count == 0

    @pytest.mark.unit
    def test_count_tokens_unicode(self):
        """Test counting tokens with unicode characters."""
        text = "Hello 世界 🌍"
        count = count_tokens(text)
        assert count > 0

    @pytest.mark.unit
    def test_count_tokens_long_text(self):
        """Test counting tokens in long text."""
        text = "word " * 1000
        count = count_tokens(text)
        assert count >= 1000

    @pytest.mark.unit
    def test_count_tokens_special_characters(self):
        """Test counting tokens with special characters."""
        text = "Test!@#$%^&*()_+-=[]{}|;':\",./<>?"
        count = count_tokens(text)
        assert count > 0


class TestCosineSimilarity:
    """Tests for cosine similarity function."""

    @pytest.mark.unit
    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vec = [1.0, 2.0, 3.0, 4.0]
        similarity = cosine_similarity(vec, vec)
        assert abs(similarity - 1.0) < 0.0001  # Should be 1.0

    @pytest.mark.unit
    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0, 0.0]
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity) < 0.0001  # Should be 0.0

    @pytest.mark.unit
    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 0.0001  # Should be -1.0

    @pytest.mark.unit
    def test_similar_vectors(self):
        """Test cosine similarity of similar vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.1, 2.1, 2.9]
        similarity = cosine_similarity(vec1, vec2)
        assert 0.9 < similarity < 1.0

    @pytest.mark.unit
    def test_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [0.0, 0.0, 0.0]
        similarity = cosine_similarity(vec1, vec2)
        assert similarity == 0.0  # Function should return 0 for zero norm

    @pytest.mark.unit
    def test_large_dimensional_vectors(self):
        """Test cosine similarity with high-dimensional vectors."""
        np.random.seed(42)
        vec1 = np.random.randn(1024).tolist()
        vec2 = np.random.randn(1024).tolist()
        similarity = cosine_similarity(vec1, vec2)
        assert -1.0 <= similarity <= 1.0


class TestValidateAPIKeys:
    """Tests for API key validation."""

    @pytest.mark.unit
    def test_validate_with_keys_set(self, mock_env_vars):
        """Test validation passes when keys are set."""
        # Should not raise exception
        try:
            validate_api_keys()
        except SystemExit:
            pytest.fail("validate_api_keys() raised SystemExit unexpectedly")

    @pytest.mark.unit
    def test_validate_without_anthropic_key(self, monkeypatch):
        """Test validation fails without Anthropic key."""
        # Patch module-level variables, not just environment
        monkeypatch.setattr("roadmap.ANTHROPIC_API_KEY", None)
        monkeypatch.setattr("roadmap.VOYAGE_API_KEY", "test-key")

        with pytest.raises(typer.Exit):
            validate_api_keys()

    @pytest.mark.unit
    def test_validate_without_voyage_key(self, monkeypatch):
        """Test validation fails without Voyage key."""
        # Patch module-level variables, not just environment
        monkeypatch.setattr("roadmap.ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setattr("roadmap.VOYAGE_API_KEY", None)

        with pytest.raises(typer.Exit):
            validate_api_keys()

    @pytest.mark.unit
    def test_validate_without_any_keys(self, monkeypatch):
        """Test validation fails without any keys."""
        # Patch module-level variables, not just environment
        monkeypatch.setattr("roadmap.ANTHROPIC_API_KEY", None)
        monkeypatch.setattr("roadmap.VOYAGE_API_KEY", None)

        with pytest.raises(typer.Exit):
            validate_api_keys()
