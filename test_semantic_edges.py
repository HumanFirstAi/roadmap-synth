#!/usr/bin/env python3
"""
Test semantic edge inference to verify it finds connections that keywords would miss.
"""

import sys
sys.path.insert(0, '.')

from roadmap import UnifiedContextGraph, cosine_similarity

def test_semantic_edges():
    """Test that semantic edges capture relationships better than keywords."""

    print("=" * 60)
    print("SEMANTIC EDGE INFERENCE TEST")
    print("=" * 60)
    print()

    # Load graph
    graph = UnifiedContextGraph.load()

    # Find some example roadmap items and their connected chunks
    roadmap_items = list(graph.node_indices["roadmap_item"].items())[:5]

    for ri_id, ri_data in roadmap_items:
        ri_name = ri_data.get("name", "Unknown")

        print(f"\n{'='*60}")
        print(f"ROADMAP ITEM: {ri_name}")
        print(f"{'='*60}")

        # Find connected chunks
        connected_chunks = []
        for neighbor_id in graph.graph.neighbors(ri_id):
            if graph.graph.nodes[neighbor_id].get("node_type") == "chunk":
                edge_data = graph.graph.edges[ri_id, neighbor_id]
                edge_type = edge_data.get("type", "unknown")
                weight = edge_data.get("weight", 0.0)

                chunk_data = graph.node_indices["chunk"].get(neighbor_id, {})
                chunk_content = chunk_data.get("content", "")[:200]  # First 200 chars

                connected_chunks.append({
                    "chunk_id": neighbor_id,
                    "content": chunk_content,
                    "edge_type": edge_type,
                    "similarity": weight
                })

        # Sort by similarity (highest first)
        connected_chunks.sort(key=lambda x: x["similarity"], reverse=True)

        print(f"\nTotal connected chunks: {len(connected_chunks)}")

        # Show top 3 connections
        print(f"\nTop 3 semantic matches:")
        for i, chunk in enumerate(connected_chunks[:3], 1):
            print(f"\n  {i}. Edge Type: {chunk['edge_type'].upper()}")
            print(f"     Similarity: {chunk['similarity']:.4f}")
            print(f"     Content preview:")
            print(f"     {chunk['content']}...")

            # Check if roadmap item name appears in chunk (keyword matching would catch this)
            name_lower = ri_name.lower()
            content_lower = chunk['content'].lower()
            if name_lower in content_lower:
                print(f"     ✓ Contains exact name match (keyword would catch)")
            else:
                print(f"     ✓ NO exact match - semantic inference found this!")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    # Count edge types
    edge_types = {}
    for _, _, data in graph.graph.edges(data=True):
        edge_type = data.get("type", "unknown")
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print(f"\nEdge Type Distribution:")
    for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {edge_type}: {count:,}")

    print(f"\n{'='*60}")


if __name__ == "__main__":
    test_semantic_edges()
