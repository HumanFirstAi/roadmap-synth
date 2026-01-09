"""
Tests for batch cosine similarity optimization.
"""

import numpy as np
import pytest
from roadmap import cosine_similarity, cosine_similarity_batch


def test_batch_similarity_matches_individual():
    """Verify batch computation produces same results as individual calls."""
    # Create test embeddings
    np.random.seed(42)
    n_queries = 10
    n_targets = 5
    embedding_dim = 128

    query_embeddings = np.random.randn(n_queries, embedding_dim)
    target_embeddings = np.random.randn(n_targets, embedding_dim)

    # Compute similarities individually
    individual_results = np.zeros((n_queries, n_targets))
    for i in range(n_queries):
        for j in range(n_targets):
            individual_results[i, j] = cosine_similarity(
                query_embeddings[i].tolist(),
                target_embeddings[j].tolist()
            )

    # Compute similarities in batch
    batch_results = cosine_similarity_batch(query_embeddings, target_embeddings)

    # Results should match within floating point precision
    np.testing.assert_allclose(batch_results, individual_results, rtol=1e-5, atol=1e-8)


def test_batch_similarity_normalized_vectors():
    """Test with already normalized vectors."""
    # Create normalized test vectors
    query = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    target = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

    similarities = cosine_similarity_batch(query, target)

    # First query should be identical to first target (similarity = 1.0)
    assert abs(similarities[0, 0] - 1.0) < 1e-6

    # First query orthogonal to second target (similarity = 0.0)
    assert abs(similarities[0, 1] - 0.0) < 1e-6

    # Second query orthogonal to both targets
    assert abs(similarities[1, 0] - 0.0) < 1e-6
    assert abs(similarities[1, 1] - 0.0) < 1e-6


def test_batch_similarity_zero_vectors():
    """Test handling of zero vectors."""
    query = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    target = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    similarities = cosine_similarity_batch(query, target)

    # Zero vectors should have zero similarity (due to normalization handling)
    assert similarities.shape == (2, 2)
    # No NaN or Inf values
    assert not np.any(np.isnan(similarities))
    assert not np.any(np.isinf(similarities))


def test_batch_similarity_performance():
    """Test that batch computation is actually faster for large matrices."""
    import time

    np.random.seed(42)
    n_queries = 100
    n_targets = 50
    embedding_dim = 1024  # Typical embedding size

    query_embeddings = np.random.randn(n_queries, embedding_dim)
    target_embeddings = np.random.randn(n_targets, embedding_dim)

    # Time batch computation
    start = time.time()
    batch_results = cosine_similarity_batch(query_embeddings, target_embeddings)
    batch_time = time.time() - start

    # Time a sample of individual computations (don't do all to save time)
    start = time.time()
    sample_size = 100
    for _ in range(sample_size):
        i = np.random.randint(0, n_queries)
        j = np.random.randint(0, n_targets)
        _ = cosine_similarity(
            query_embeddings[i].tolist(),
            target_embeddings[j].tolist()
        )
    individual_sample_time = time.time() - start

    # Estimate total individual time
    estimated_individual_time = individual_sample_time * (n_queries * n_targets) / sample_size

    # Batch should be significantly faster
    speedup = estimated_individual_time / batch_time
    print(f"\nBatch speedup: {speedup:.1f}x")
    print(f"Batch time: {batch_time:.4f}s")
    print(f"Estimated individual time: {estimated_individual_time:.4f}s")

    # Should be at least 5x faster (conservative estimate)
    assert speedup > 5, f"Batch computation should be faster, got {speedup:.1f}x speedup"


def test_batch_similarity_shape():
    """Test output shape is correct."""
    query = np.random.randn(7, 64)
    target = np.random.randn(13, 64)

    similarities = cosine_similarity_batch(query, target)

    assert similarities.shape == (7, 13)


def test_batch_similarity_range():
    """Test that similarities are in valid range [-1, 1]."""
    np.random.seed(42)
    query = np.random.randn(20, 128)
    target = np.random.randn(15, 128)

    similarities = cosine_similarity_batch(query, target)

    # All similarities should be in [-1, 1]
    assert np.all(similarities >= -1.0)
    assert np.all(similarities <= 1.0)


def test_cosine_similarity_individual_still_works():
    """Ensure individual function still works correctly."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]

    similarity = cosine_similarity(vec1, vec2)
    assert abs(similarity - 1.0) < 1e-6

    vec3 = [0.0, 1.0, 0.0]
    similarity = cosine_similarity(vec1, vec3)
    assert abs(similarity - 0.0) < 1e-6
