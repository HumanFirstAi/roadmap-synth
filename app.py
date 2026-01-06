#!/usr/bin/env python3
"""
Roadmap Synthesis Tool - Streamlit Web Interface
"""

import streamlit as st
from pathlib import Path
import os
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd

# Import functions from roadmap.py
from roadmap import (
    parse_document, chunk_text, chunk_with_fallback, index_chunks, retrieve_chunks,
    generate_roadmap, format_for_persona, init_db,
    VALID_LENSES, OUTPUT_DIR, DATA_DIR, MATERIALS_DIR,
    validate_api_keys, ContextGraph, generate_embeddings,
    load_questions, save_questions, load_answers, save_answers,
    load_decisions, save_decisions,
    load_architecture_documents, scan_architecture_documents, generate_architecture_alignment,
    parse_roadmap_for_analysis, extract_engineering_questions_from_alignment,
    add_architecture_questions_to_system, save_alignment_analysis,
    load_alignment_analysis, format_alignment_report,
    load_competitor_developments, add_competitor_development, get_competitor_development,
    load_analyst_assessments, generate_analyst_assessment, format_analyst_assessment_markdown,
    UnifiedContextGraph, sync_all_to_graph, retrieve_with_authority, AUTHORITY_LEVELS
)

# Page configuration
st.set_page_config(
    page_title="Roadmap Synth",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'index_stats' not in st.session_state:
    st.session_state.index_stats = None


# ========== UTILITY FUNCTIONS ==========

def get_index_stats() -> Optional[Dict]:
    """Get statistics about indexed materials"""
    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")

        # Get all chunks
        chunks = table.to_pandas()

        if chunks.empty:
            return None

        # Calculate statistics
        total_chunks = len(chunks)
        total_tokens = chunks['token_count'].sum()

        # Breakdown by lens
        lens_counts = chunks['lens'].value_counts().to_dict()

        # Recent sources
        recent_sources = chunks.nlargest(10, 'created_at')[['source_file', 'created_at', 'lens']].to_dict('records')

        return {
            'total_chunks': total_chunks,
            'total_tokens': int(total_tokens),
            'lens_breakdown': lens_counts,
            'recent_sources': recent_sources
        }
    except Exception:
        return None


def clear_index():
    """Clear the entire vector index"""
    try:
        db = init_db()
        db.drop_table("roadmap_chunks")
        st.session_state.index_stats = None
        return True
    except Exception as e:
        st.error(f"Error clearing index: {e}")
        return False


def save_env_vars(anthropic_key: str, voyage_key: str):
    """Save API keys to .env file"""
    env_path = Path(".env")
    content = f"""# Anthropic Claude API Key (required)
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY={anthropic_key}

# Voyage AI API Key (required)
# Get from: https://dash.voyageai.com/
VOYAGE_API_KEY={voyage_key}
"""
    env_path.write_text(content)
    # Reload environment
    os.environ['ANTHROPIC_API_KEY'] = anthropic_key
    os.environ['VOYAGE_API_KEY'] = voyage_key


def rebuild_context_graph():
    """Rebuild the context graph from all indexed chunks"""
    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")

        # Get all chunks and embeddings from store
        all_data = table.to_pandas()
        all_chunks = []
        all_embeddings = []

        for _, row in all_data.iterrows():
            all_chunks.append({
                "id": row["id"],
                "content": row["content"],
                "lens": row["lens"],
                "source_file": row["source_file"],
                "chunk_index": row["chunk_index"],
                "token_count": row["token_count"],
            })
            all_embeddings.append(row["vector"])

        # Build graph
        graph = ContextGraph()
        graph.build_from_chunks(all_chunks, all_embeddings)
        graph.save()

        return graph.get_stats()
    except Exception as e:
        st.warning(f"⚠️ Could not build graph: {e}")
        return None


def get_all_materials() -> List[Dict]:
    """Get all materials files organized by lens"""
    materials = []
    for lens in VALID_LENSES:
        lens_dir = MATERIALS_DIR / lens
        if lens_dir.exists():
            for file_path in lens_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    materials.append({
                        'file': file_path.name,
                        'path': str(file_path),
                        'lens': lens,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'size_mb': f"{file_path.stat().st_size / 1024 / 1024:.2f} MB"
                    })
    return materials


def move_file_to_lens(file_path: str, new_lens: str) -> bool:
    """Move a file to a different lens folder"""
    try:
        source = Path(file_path)
        if not source.exists():
            return False

        # Create destination directory
        dest_dir = MATERIALS_DIR / new_lens
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Move file
        dest = dest_dir / source.name
        source.rename(dest)
        return True
    except Exception as e:
        st.error(f"Error moving file: {e}")
        return False


def delete_material_file(file_path: str) -> bool:
    """Delete a material file"""
    try:
        Path(file_path).unlink()
        return True
    except Exception as e:
        st.error(f"Error deleting file: {e}")
        return False


def get_all_chunks() -> Optional[pd.DataFrame]:
    """Get all chunks from the index"""
    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")
        chunks_df = table.to_pandas()

        if chunks_df.empty:
            return None

        # Add human-readable created_at
        chunks_df['created_at'] = pd.to_datetime(chunks_df['created_at'])
        chunks_df['created_at_str'] = chunks_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')

        return chunks_df
    except Exception:
        return None


# ========== PAGE: DASHBOARD ==========

def page_dashboard():
    st.title("📊 Dashboard")
    st.markdown("Overview of your indexed materials and roadmap status")

    # Get or refresh stats
    if st.button("🔄 Refresh Stats"):
        st.session_state.index_stats = get_index_stats()

    stats = st.session_state.index_stats or get_index_stats()

    if not stats:
        st.warning("⚠️ No materials indexed yet. Go to **Ingest Materials** to get started.")
        return

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Chunks", f"{stats['total_chunks']:,}")
    with col2:
        st.metric("Total Tokens", f"{stats['total_tokens']:,}")
    with col3:
        status = "✅ Ready to generate" if stats['total_chunks'] > 0 else "⚠️ No materials"
        st.metric("Status", status)

    # Lens breakdown
    st.subheader("Breakdown by Lens")
    lens_df = pd.DataFrame([
        {"Lens": lens, "Chunks": count}
        for lens, count in stats['lens_breakdown'].items()
    ])
    st.bar_chart(lens_df.set_index("Lens"))

    # Recent sources
    st.subheader("Recent Ingested Sources")
    if stats['recent_sources']:
        recent_df = pd.DataFrame(stats['recent_sources'])
        recent_df['created_at'] = pd.to_datetime(recent_df['created_at'])
        recent_df['created_at'] = recent_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(recent_df, use_container_width=True)

    # Context graph stats
    st.subheader("Context Graph")
    try:
        graph = ContextGraph().load()
        graph_stats = graph.get_stats()

        col1, col2, col3 = st.columns(3)
        col1.metric("Graph Nodes", graph_stats["nodes"])
        col2.metric("Graph Edges", graph_stats["edges"])
        col3.metric("Components", graph_stats["components"])

        if graph_stats["edge_types"]:
            with st.expander("Edge Type Breakdown"):
                for edge_type, count in graph_stats["edge_types"].items():
                    st.write(f"- **{edge_type}**: {count}")
    except Exception:
        st.info("No context graph built yet. Ingest materials to build the graph.")

    # Unified Context Graph stats
    st.subheader("🕸️ Unified Knowledge Graph")
    st.caption("Integrates decisions, assessments, questions, and roadmap with authority hierarchy")

    try:
        unified_graph = UnifiedContextGraph.load()

        if unified_graph.graph.number_of_nodes() == 0:
            st.info("Graph is empty. Click 'Sync Graph' to build the unified knowledge graph.")

            if st.button("🔄 Sync Graph"):
                with st.spinner("Syncing all data sources..."):
                    unified_graph = sync_all_to_graph()
                st.success("Graph synced!")
                st.rerun()
        else:
            # Show graph metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Nodes", unified_graph.graph.number_of_nodes())
            col2.metric("Total Edges", unified_graph.graph.number_of_edges())

            active_decisions = len([
                d for d in unified_graph.node_indices["decision"].values()
                if d.get("status") == "active"
            ])
            col3.metric("Active Decisions", active_decisions)

            pending_questions = len([
                q for q in unified_graph.node_indices["question"].values()
                if q.get("status") == "pending"
            ])
            col4.metric("Open Questions", pending_questions)

            # Authority breakdown
            with st.expander("Knowledge by Authority Level"):
                authority_data = {}
                for node_type, level in AUTHORITY_LEVELS.items():
                    count = 0
                    if node_type == "answered_question":
                        count = len([q for q in unified_graph.node_indices["question"].values() if q.get("status") == "answered"])
                    elif node_type == "pending_question":
                        count = len([q for q in unified_graph.node_indices["question"].values() if q.get("status") == "pending"])
                    else:
                        count = len(unified_graph.node_indices.get(node_type.replace("_question", "question"), {}))

                    if count > 0:
                        authority_data[f"L{level}: {node_type.replace('_', ' ').title()}"] = count

                if authority_data:
                    st.bar_chart(authority_data)

            if st.button("🔄 Re-sync Graph"):
                with st.spinner("Re-syncing..."):
                    unified_graph = sync_all_to_graph()
                st.success("Graph re-synced!")
                st.rerun()

    except Exception as e:
        st.warning(f"Could not load unified graph: {e}")
        if st.button("🔄 Build Graph"):
            with st.spinner("Building unified knowledge graph..."):
                unified_graph = sync_all_to_graph()
            st.success("Graph built!")
            st.rerun()

    # Clear index button
    st.divider()
    if st.button("🗑️ Clear Index", type="secondary"):
        if st.checkbox("⚠️ Are you sure? This cannot be undone."):
            if clear_index():
                st.success("Index cleared successfully!")
                st.rerun()


# ========== PAGE: INGEST MATERIALS ==========

def page_ingest():
    st.title("📥 Ingest Materials")
    st.markdown("Upload documents and tag them with authority levels (lenses)")

    # File upload method
    st.subheader("Upload Files")

    lens = st.selectbox(
        "Select Lens (Authority Level)",
        options=VALID_LENSES,
        help="Choose the authority level for these documents"
    )

    # Lens descriptions
    lens_help = {
        "your-voice": "Your strategic vision (highest authority)",
        "team-structured": "Formal team documentation",
        "team-conversational": "Meeting notes, discussions",
        "business-framework": "OKRs, business strategy",
        "engineering": "Technical docs (veto power on feasibility)",
        "external-analyst": "Market research (lowest authority)"
    }
    st.info(f"**{lens}**: {lens_help.get(lens, '')}")

    # Chunking method selection
    st.subheader("Chunking Method")
    chunking_method = st.radio(
        "Select chunking strategy",
        ["Agentic (Claude-powered)", "Structure-aware (fallback)"],
        index=0,
        help="""
        - **Agentic**: Highest quality, uses Claude to find logical boundaries (~$0.01-0.05 per document)
        - **Structure-aware**: Simple token-based splitting, no LLM cost
        """
    )

    use_agentic = chunking_method == "Agentic (Claude-powered)"

    if use_agentic:
        st.info("⚠️ Agentic chunking calls Claude API. Estimated cost: ~$0.02-0.05 per document.")

    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'pptx', 'xlsx', 'csv', 'txt', 'md', 'json']
    )

    if st.button("📥 Ingest Uploaded Files", disabled=not uploaded_files):
        if not uploaded_files:
            st.warning("Please upload at least one file")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        success_count = 0
        error_count = 0

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Processing {uploaded_file.name}...")

                # Save file to materials directory
                lens_dir = MATERIALS_DIR / lens
                lens_dir.mkdir(parents=True, exist_ok=True)
                file_path = lens_dir / uploaded_file.name
                file_path.write_bytes(uploaded_file.read())

                # Parse and index
                text = parse_document(file_path)
                if not text.strip():
                    st.warning(f"⚠️ {uploaded_file.name}: Empty document, skipping")
                    error_count += 1
                    continue

                chunks = chunk_with_fallback(text, str(file_path), lens, use_agentic=use_agentic)
                if not chunks:
                    st.warning(f"⚠️ {uploaded_file.name}: No chunks generated, skipping")
                    error_count += 1
                    continue

                index_chunks(chunks, str(file_path))
                st.success(f"✓ {uploaded_file.name} ({len(chunks)} chunks)")
                success_count += 1

            except Exception as e:
                st.error(f"✗ {uploaded_file.name}: {str(e)}")
                error_count += 1

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text(f"Complete! {success_count} succeeded, {error_count} failed")
        st.session_state.index_stats = None  # Clear cache

        # Rebuild context graph
        if success_count > 0:
            with st.spinner("Rebuilding context graph..."):
                graph_stats = rebuild_context_graph()
                if graph_stats:
                    st.success(f"✓ Context graph updated: {graph_stats['nodes']} nodes, {graph_stats['edges']} edges")

    # Alternative: Path-based ingestion
    st.divider()
    st.subheader("Ingest from Path")

    col1, col2 = st.columns([3, 1])
    with col1:
        folder_path = st.text_input("Folder Path", placeholder="/path/to/documents")
    with col2:
        path_lens = st.selectbox("Lens", options=VALID_LENSES, key="path_lens")

    if st.button("📂 Ingest from Path"):
        if not folder_path:
            st.warning("Please provide a path")
            return

        path_obj = Path(folder_path)
        if not path_obj.exists():
            st.error(f"Path not found: {folder_path}")
            return

        files = [f for f in path_obj.rglob("*") if f.is_file() and not f.name.startswith('.')]

        if not files:
            st.warning("No files found in path")
            return

        st.info(f"Found {len(files)} files")

        progress_bar = st.progress(0)
        success_count = 0

        for i, file in enumerate(files):
            try:
                text = parse_document(file)
                if text.strip():
                    chunks = chunk_with_fallback(text, str(file), path_lens, use_agentic=use_agentic)
                    if chunks:
                        index_chunks(chunks, str(file))
                        success_count += 1
            except Exception:
                pass

            progress_bar.progress((i + 1) / len(files))

        st.success(f"Ingested {success_count}/{len(files)} files successfully!")
        st.session_state.index_stats = None

        # Rebuild context graph
        if success_count > 0:
            with st.spinner("Rebuilding context graph..."):
                graph_stats = rebuild_context_graph()
                if graph_stats:
                    st.success(f"✓ Context graph updated: {graph_stats['nodes']} nodes, {graph_stats['edges']} edges")


# ========== PAGE: MANAGE MATERIALS ==========

def page_manage():
    st.title("📁 Manage Materials")
    st.markdown("View, organize, and manage your uploaded documents")

    # Get all materials
    materials = get_all_materials()

    if not materials:
        st.warning("⚠️ No materials found. Upload documents in **Ingest Materials** first.")
        return

    st.success(f"✓ Found {len(materials)} files across {len(set(m['lens'] for m in materials))} lenses")

    # Filter by lens
    st.subheader("Filter & View")
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_lens = st.multiselect(
            "Filter by Lens",
            options=["All"] + VALID_LENSES,
            default=["All"]
        )
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()

    # Filter materials
    if "All" not in selected_lens and selected_lens:
        filtered_materials = [m for m in materials if m['lens'] in selected_lens]
    else:
        filtered_materials = materials

    # Display as dataframe with controls
    st.subheader(f"Materials ({len(filtered_materials)} files)")

    for material in filtered_materials:
        with st.expander(f"📄 {material['file']} - [{material['lens']}]"):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(f"**Lens:** {material['lens']}")
                st.write(f"**Size:** {material['size_mb']}")
                st.write(f"**Modified:** {material['modified'].strftime('%Y-%m-%d %H:%M')}")

            with col2:
                # Move to different lens
                new_lens = st.selectbox(
                    "Move to lens:",
                    options=[l for l in VALID_LENSES if l != material['lens']],
                    key=f"move_{material['path']}"
                )

                if st.button("🔄 Move", key=f"btn_move_{material['path']}"):
                    if move_file_to_lens(material['path'], new_lens):
                        st.success(f"✓ Moved to {new_lens}")
                        st.info("⚠️ Note: You'll need to re-index this file for changes to take effect")
                        st.rerun()

            with col3:
                if st.button("🗑️ Delete", key=f"btn_delete_{material['path']}", type="secondary"):
                    if st.checkbox(f"Confirm delete?", key=f"confirm_{material['path']}"):
                        if delete_material_file(material['path']):
                            st.success("✓ Deleted")
                            st.rerun()

            # File path info
            st.caption(f"Path: {material['path']}")

    # Bulk operations
    st.divider()
    st.subheader("Bulk Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Re-index All Materials**")
        st.caption("Clears the index and re-ingests all materials. Useful after moving files.")

        if st.button("🔄 Re-index All", type="primary"):
            if st.checkbox("⚠️ This will clear the current index and re-ingest all materials. Continue?"):
                try:
                    # Clear index
                    clear_index()

                    # Re-ingest all materials
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    success_count = 0

                    for i, material in enumerate(materials):
                        try:
                            status_text.text(f"Processing {material['file']}...")
                            text = parse_document(Path(material['path']))
                            if text.strip():
                                chunks = chunk_with_fallback(text, material['path'], material['lens'], use_agentic=True)
                                if chunks:
                                    index_chunks(chunks, material['path'])
                                    success_count += 1
                        except Exception:
                            pass

                        progress_bar.progress((i + 1) / len(materials))

                    status_text.text(f"Complete! Re-indexed {success_count}/{len(materials)} files")
                    st.session_state.index_stats = None
                    st.success("✅ Re-indexing complete!")

                    # Rebuild context graph
                    if success_count > 0:
                        with st.spinner("Rebuilding context graph..."):
                            graph_stats = rebuild_context_graph()
                            if graph_stats:
                                st.success(f"✓ Context graph updated: {graph_stats['nodes']} nodes, {graph_stats['edges']} edges")

                except Exception as e:
                    st.error(f"Error during re-indexing: {e}")

    with col2:
        st.write("**Delete All in Lens**")
        st.caption("Remove all files from a specific lens folder.")

        delete_lens = st.selectbox("Select lens to clear:", options=VALID_LENSES, key="delete_lens")

        if st.button("🗑️ Delete All", type="secondary"):
            if st.checkbox(f"⚠️ This will delete ALL files in {delete_lens}. This cannot be undone!"):
                lens_materials = [m for m in materials if m['lens'] == delete_lens]
                deleted_count = 0

                for material in lens_materials:
                    if delete_material_file(material['path']):
                        deleted_count += 1

                st.success(f"✅ Deleted {deleted_count} files from {delete_lens}")
                st.rerun()


# ========== PAGE: VIEW CHUNKS ==========

def page_chunks():
    st.title("🔍 View Chunks")
    st.markdown("Inspect how documents were chunked and indexed")

    # Explanation section
    with st.expander("ℹ️ How Chunking Works", expanded=False):
        st.markdown("""
        ### Chunking Process

        When you ingest documents, they are broken down into smaller "chunks" for better semantic search and retrieval.

        **Process:**
        1. **Document Parsing**: Files are converted to plain text using the `unstructured` library
        2. **Tokenization**: Text is converted to tokens using tiktoken (cl100k_base encoding, Claude-compatible)
        3. **Chunking**: Text is split into chunks of ~512 tokens each
        4. **Overlap**: Each chunk overlaps with the next by 50 tokens to preserve context across boundaries
        5. **Embedding**: Each chunk is embedded using Voyage AI (voyage-3-large model, 1024 dimensions)
        6. **Indexing**: Embeddings are stored in LanceDB with metadata (lens, source file, token count, etc.)

        **Why Chunk?**
        - Enables precise semantic search over specific sections
        - Fits within context windows for both embedding and LLM models
        - Preserves context through overlap
        - Allows lens-based authority weighting

        **Parameters:**
        - **Chunk Size**: 512 tokens (~350-400 words)
        - **Overlap**: 50 tokens (~35-40 words)
        - **Encoding**: cl100k_base (same as Claude)
        """)

    st.divider()

    # Get chunks
    chunks_df = get_all_chunks()

    if chunks_df is None:
        st.warning("⚠️ No chunks indexed yet. Ingest documents to see chunks here.")
        return

    st.success(f"✓ Found {len(chunks_df)} chunks in the index")

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Chunks", f"{len(chunks_df):,}")
    with col2:
        st.metric("Total Tokens", f"{chunks_df['token_count'].sum():,}")
    with col3:
        st.metric("Unique Sources", chunks_df['source_file'].nunique())
    with col4:
        avg_tokens = int(chunks_df['token_count'].mean())
        st.metric("Avg Tokens/Chunk", avg_tokens)

    # Filters
    st.subheader("Filter Chunks")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_lenses = st.multiselect(
            "Filter by Lens",
            options=["All"] + list(chunks_df['lens'].unique()),
            default=["All"]
        )

    with col2:
        # Get unique source files
        unique_sources = chunks_df['source_file'].unique()
        source_names = [Path(s).name for s in unique_sources]
        selected_source = st.selectbox(
            "Filter by Source File",
            options=["All"] + source_names
        )

    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=["Created (newest)", "Created (oldest)", "Token Count (high)", "Token Count (low)", "Chunk Index"]
        )

    # Apply filters
    filtered_df = chunks_df.copy()

    if "All" not in selected_lenses and selected_lenses:
        filtered_df = filtered_df[filtered_df['lens'].isin(selected_lenses)]

    if selected_source != "All":
        # Find the full path that matches the selected name
        matching_path = [p for p in unique_sources if Path(p).name == selected_source][0]
        filtered_df = filtered_df[filtered_df['source_file'] == matching_path]

    # Apply sorting
    if sort_by == "Created (newest)":
        filtered_df = filtered_df.sort_values('created_at', ascending=False)
    elif sort_by == "Created (oldest)":
        filtered_df = filtered_df.sort_values('created_at', ascending=True)
    elif sort_by == "Token Count (high)":
        filtered_df = filtered_df.sort_values('token_count', ascending=False)
    elif sort_by == "Token Count (low)":
        filtered_df = filtered_df.sort_values('token_count', ascending=True)
    elif sort_by == "Chunk Index":
        filtered_df = filtered_df.sort_values(['source_file', 'chunk_index'])

    st.info(f"Showing {len(filtered_df)} of {len(chunks_df)} chunks")

    # Display chunks
    st.subheader("Chunk Details")

    # Pagination
    chunks_per_page = 10
    total_pages = (len(filtered_df) + chunks_per_page - 1) // chunks_per_page

    if total_pages > 1:
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page_num - 1) * chunks_per_page
        end_idx = start_idx + chunks_per_page
        page_df = filtered_df.iloc[start_idx:end_idx]
    else:
        page_df = filtered_df

    # Display each chunk
    for idx, row in page_df.iterrows():
        source_name = Path(row['source_file']).name

        with st.expander(f"🔹 Chunk {row['chunk_index']} from {source_name} [{row['lens']}]"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Chunk Content:**")
                st.text_area(
                    "Content",
                    value=row['content'],
                    height=200,
                    key=f"chunk_{row['id']}",
                    label_visibility="collapsed"
                )

            with col2:
                st.markdown("**Metadata:**")
                st.write(f"**Lens:** {row['lens']}")
                st.write(f"**Token Count:** {row['token_count']}")
                st.write(f"**Chunk Index:** {row['chunk_index']}")
                st.write(f"**Created:** {row['created_at_str']}")
                st.caption(f"**Source:** {row['source_file']}")
                st.caption(f"**ID:** {row['id']}")

    # Export option
    st.divider()
    st.subheader("Export Chunks")

    col1, col2 = st.columns(2)

    with col1:
        # Export filtered chunks as CSV
        if st.button("📥 Export Filtered as CSV"):
            csv = filtered_df[['id', 'content', 'lens', 'source_file', 'chunk_index', 'token_count', 'created_at_str']].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="chunks_export.csv",
                mime="text/csv"
            )

    with col2:
        # Export as JSON
        if st.button("📥 Export Filtered as JSON"):
            json_data = filtered_df[['id', 'content', 'lens', 'source_file', 'chunk_index', 'token_count', 'created_at_str']].to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="chunks_export.json",
                mime="application/json"
            )


# ========== PAGE: CHUNKING AUDIT ==========

def page_chunking_audit():
    st.title("🔍 Chunking Audit Log")
    st.markdown("Review chunking quality and verification results")

    log_path = DATA_DIR / "chunking_log.jsonl"

    if not log_path.exists():
        st.info("No chunking logs yet. Ingest some documents to see audit information.")
        st.markdown("""
        **What is this page?**

        This page shows detailed information about how documents were chunked:
        - Which chunking method was used (agentic vs structure-aware)
        - Verification results for agentic chunking
        - Any issues detected during chunking
        - Preview of generated chunks
        """)
        return

    # Load logs
    import json
    logs = []
    try:
        with open(log_path) as f:
            for line in f:
                logs.append(json.loads(line))
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    total_docs = len(logs)
    agentic_docs = len([l for l in logs if l['method'].startswith('agentic')])
    fallback_docs = len([l for l in logs if 'fallback' in l['method'] or l['method'].startswith('structure')])
    issues_docs = len([l for l in logs if not l['verification']['all_valid']])

    col1.metric("Total Documents", total_docs)
    col2.metric("Agentic Chunking", agentic_docs)
    col3.metric("Fallback Used", fallback_docs)
    col4.metric("With Issues", issues_docs)

    # Filters
    st.subheader("Filters")
    col1, col2 = st.columns(2)

    with col1:
        show_only_issues = st.checkbox("Show only documents with issues")

    with col2:
        method_filter = st.selectbox(
            "Filter by method",
            ["All", "Agentic only", "Fallback only"]
        )

    # Apply filters
    filtered_logs = logs

    if show_only_issues:
        filtered_logs = [l for l in filtered_logs if not l['verification']['all_valid']]

    if method_filter == "Agentic only":
        filtered_logs = [l for l in filtered_logs if l['method'].startswith('agentic')]
    elif method_filter == "Fallback only":
        filtered_logs = [l for l in filtered_logs if 'fallback' in l['method'] or l['method'].startswith('structure')]

    # Show results
    st.subheader(f"Results ({len(filtered_logs)} documents)")

    for log in reversed(filtered_logs):  # Most recent first
        status = "✅" if log['verification']['all_valid'] else "⚠️"
        source_name = Path(log['source_path']).name

        with st.expander(f"{status} {source_name} — {log['chunk_count']} chunks — {log['method']}"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Lens:** {log['lens']}")
            col2.write(f"**Method:** {log['method']}")
            col3.write(f"**Time:** {log['timestamp'][:19]}")

            if not log['verification']['all_valid']:
                st.error(f"❌ Issues detected in {len(log['verification']['issues'])} chunks")

                for issue in log['verification']['issues']:
                    st.write(f"**Chunk {issue['chunk_index']}:**")
                    for problem in issue['issues']:
                        st.write(f"- {problem.get('severity', 'UNKNOWN')}: {problem.get('message', 'No message')}")
            else:
                st.success(f"✅ All {log['verification']['valid_count']} chunks verified successfully")

            # Show sample chunks
            st.write("**Sample Chunks:**")
            for chunk in log['chunks_preview']:
                st.code(f"[Chunk {chunk['index']}] {chunk['content_length']} chars\n{chunk['content_preview']}...")

                if chunk.get('entities'):
                    st.caption(f"Entities: {', '.join(chunk['entities'])}")


# ========== PAGE: CONTEXT GRAPH ==========

def page_context_graph():
    st.title("🕸️ Context Graph")
    st.markdown("Explore chunk relationships and semantic connections")

    # Load graph
    try:
        graph = ContextGraph().load()
        stats = graph.get_stats()
    except Exception as e:
        st.warning("⚠️ No context graph found. Ingest materials to build the graph.")
        st.info("The context graph is automatically built when you ingest documents.")
        return

    # Display statistics
    st.subheader("Graph Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes (Chunks)", stats["nodes"])
    col2.metric("Edges (Connections)", stats["edges"])
    col3.metric("Components", stats["components"])
    col4.metric("Density", f"{stats['density']:.4f}")

    # Edge type breakdown
    st.subheader("Edge Types")
    if stats["edge_types"]:
        edge_df = pd.DataFrame([
            {"Edge Type": edge_type, "Count": count}
            for edge_type, count in stats["edge_types"].items()
        ])
        st.bar_chart(edge_df.set_index("Edge Type"))

        # Show legend
        with st.expander("📖 Edge Type Descriptions"):
            st.markdown("""
            - **SIMILAR_TO**: Chunks with high semantic similarity (cosine > 0.80)
            - **SAME_SOURCE**: Chunks from the same source document
            - **SAME_LENS**: Chunks with the same authority lens
            - **TOPIC_OVERLAP**: Chunks sharing 2+ key terms
            - **TEMPORAL_OVERLAP**: Chunks referencing the same time periods
            - **SEQUENTIAL**: Adjacent chunks in the same document
            """)
    else:
        st.info("No edges found in the graph.")

    # Interactive exploration
    st.subheader("Explore Connections")

    if stats["nodes"] == 0:
        st.info("No nodes in the graph.")
        return

    # Select a chunk to explore
    chunk_ids = list(graph.graph.nodes())

    # Get node info for display
    node_options = {}
    for chunk_id in chunk_ids[:100]:  # Limit to first 100 for performance
        node_data = graph.graph.nodes[chunk_id]
        source_name = node_data.get('source_name', 'Unknown')
        lens = node_data.get('lens', 'unknown')
        preview = node_data.get('content_preview', '')[:50]
        display_name = f"{source_name} [{lens}] - {preview}..."
        node_options[display_name] = chunk_id

    if not node_options:
        st.info("No chunks available to explore.")
        return

    selected_display = st.selectbox("Select a chunk to explore", list(node_options.keys()))
    selected = node_options[selected_display]

    if selected:
        node_data = graph.graph.nodes[selected]

        # Show chunk info
        st.write("**Chunk Information:**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Lens", node_data.get('lens', 'N/A'))
        col2.metric("Source", node_data.get('source_name', 'N/A'))
        col3.metric("Token Count", node_data.get('token_count', 'N/A'))

        st.write("**Content Preview:**")
        st.text_area("", node_data.get('content_preview', 'N/A'), height=150, disabled=True)

        # Show key terms and time references
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Key Terms:**")
            terms = node_data.get('key_terms', [])
            if terms:
                st.write(", ".join(terms))
            else:
                st.write("None detected")

        with col2:
            st.write("**Time References:**")
            times = node_data.get('time_references', [])
            if times:
                st.write(", ".join(times))
            else:
                st.write("None detected")

        # Show connections
        neighbors = list(graph.graph.neighbors(selected))
        st.write(f"**Connected to {len(neighbors)} other chunks:**")

        if neighbors:
            # Group by edge type
            by_type = {}
            for neighbor in neighbors:
                edge_data = graph.graph.edges[selected, neighbor]
                edge_type = edge_data.get('type', 'UNKNOWN')
                if edge_type not in by_type:
                    by_type[edge_type] = []
                by_type[edge_type].append((neighbor, edge_data))

            # Display by type
            for edge_type, connections in by_type.items():
                with st.expander(f"{edge_type} ({len(connections)} connections)"):
                    for neighbor, edge_data in connections[:5]:  # Show first 5
                        neighbor_data = graph.graph.nodes[neighbor]
                        st.markdown(f"**→ {neighbor_data.get('source_name', neighbor)}**")
                        st.write(f"- **Lens:** {neighbor_data.get('lens', 'N/A')}")
                        st.write(f"- **Weight:** {edge_data.get('weight', 'N/A')}")

                        # Show shared terms/periods if available
                        if 'shared_terms' in edge_data:
                            st.write(f"- **Shared terms:** {', '.join(edge_data['shared_terms'])}")
                        if 'shared_periods' in edge_data:
                            st.write(f"- **Shared periods:** {', '.join(edge_data['shared_periods'])}")

                        st.write(f"- **Preview:** {neighbor_data.get('content_preview', 'N/A')[:100]}...")
                        st.markdown("---")
        else:
            st.info("This chunk has no connections in the graph.")


# ========== PAGE: GENERATE ROADMAP ==========

def page_generate():
    st.title("🔧 Generate Roadmap")
    st.markdown("Generate master roadmap from indexed materials")

    # Check if we have materials
    stats = get_index_stats()
    if not stats:
        st.warning("⚠️ No materials indexed. Please ingest documents first.")
        return

    st.success(f"✓ Ready to generate ({stats['total_chunks']} chunks indexed)")

    # Show existing roadmap if available
    master_path = OUTPUT_DIR / "master_roadmap.md"
    if master_path.exists():
        st.info(f"📄 Existing master roadmap found (last modified: {datetime.fromtimestamp(master_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")

        with st.expander("Preview Existing Roadmap"):
            st.markdown(master_path.read_text())

    # Generation options
    st.subheader("Generation Options")

    additional_context = st.text_area(
        "Additional Context (optional)",
        placeholder="E.g., Focus on Q2 priorities, emphasize platform investments...",
        help="Provide additional instructions for the roadmap generation"
    )

    # Generate button
    if st.button("🚀 Generate Master Roadmap", type="primary"):
        # Check API keys first
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.error("❌ ANTHROPIC_API_KEY not set. Please configure in Settings.")
            return
        if not os.getenv("VOYAGE_API_KEY"):
            st.error("❌ VOYAGE_API_KEY not set. Please configure in Settings.")
            return

        try:
            with st.spinner("Generating roadmap... This may take 30-60 seconds"):
                query = "Generate a comprehensive product roadmap"
                if additional_context:
                    query += f". Additional context: {additional_context}"

                roadmap = generate_roadmap(query)

                st.success("✅ Master roadmap generated successfully!")

                # Display roadmap
                st.subheader("Generated Roadmap")
                st.markdown(roadmap)

                # Download button
                st.download_button(
                    label="📥 Download Roadmap",
                    data=roadmap,
                    file_name="master_roadmap.md",
                    mime="text/markdown"
                )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            st.error(f"Error generating roadmap: {e}")
            with st.expander("🔍 Error Details"):
                st.code(error_details)

            # Provide helpful suggestions
            st.info("""
            **Troubleshooting:**
            - Check that your API keys are valid in Settings
            - Verify you have internet connectivity
            - Try testing the connection in Settings page
            - Check if the Anthropic API is accessible from your network
            """)


# ========== PAGE: FORMAT BY PERSONA ==========

def page_format():
    st.title("👥 Format by Persona")
    st.markdown("Transform master roadmap for specific audiences")

    # Check if master roadmap exists
    master_path = OUTPUT_DIR / "master_roadmap.md"
    if not master_path.exists():
        st.warning("⚠️ Master roadmap not found. Please generate it first.")
        return

    st.success(f"✓ Master roadmap found (last modified: {datetime.fromtimestamp(master_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")

    # Persona selection
    st.subheader("Select Persona")

    persona = st.radio(
        "Target Audience",
        options=["executive", "product", "engineering"],
        format_func=lambda x: {
            "executive": "📊 Executive (C-level, SVPs) - Strategic view, 500-800 words",
            "product": "📋 Product (PMs, Product Leaders) - Detailed priorities, 2-3 pages",
            "engineering": "⚙️ Engineering (Engineers, Architects) - Technical details, 5-10 pages"
        }[x],
        help="Choose the audience for the formatted roadmap"
    )

    # Check if formatted version exists
    persona_path = OUTPUT_DIR / f"{persona}_roadmap.md"
    if persona_path.exists():
        st.info(f"📄 Existing {persona} roadmap found (last modified: {datetime.fromtimestamp(persona_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")

    # Generate button
    if st.button(f"🎯 Generate {persona.capitalize()} Roadmap", type="primary"):
        try:
            with st.spinner(f"Formatting roadmap for {persona} audience..."):
                formatted = format_for_persona(persona)

                st.success(f"✅ {persona.capitalize()} roadmap generated successfully!")

                # Display with tabs
                tab1, tab2 = st.tabs(["📄 Formatted Roadmap", "📋 Master Roadmap"])

                with tab1:
                    st.markdown(formatted)
                    st.download_button(
                        label=f"📥 Download {persona.capitalize()} Roadmap",
                        data=formatted,
                        file_name=f"{persona}_roadmap.md",
                        mime="text/markdown",
                        key="download_formatted"
                    )

                with tab2:
                    master_text = master_path.read_text()
                    st.markdown(master_text)

        except Exception as e:
            st.error(f"Error formatting roadmap: {e}")

    # Show existing formatted roadmaps
    st.divider()
    st.subheader("Existing Roadmaps")

    for p in ["executive", "product", "engineering"]:
        p_path = OUTPUT_DIR / f"{p}_roadmap.md"
        if p_path.exists():
            with st.expander(f"📄 {p.capitalize()} Roadmap"):
                st.markdown(p_path.read_text())
                st.download_button(
                    label=f"📥 Download",
                    data=p_path.read_text(),
                    file_name=f"{p}_roadmap.md",
                    mime="text/markdown",
                    key=f"download_{p}"
                )


# ========== PAGE: ASK QUESTIONS ==========

def page_ask():
    st.title("❓ Ask Questions")
    st.markdown("Query your indexed materials and roadmap")

    # Check if we have materials
    stats = get_index_stats()
    if not stats:
        st.warning("⚠️ No materials indexed. Please ingest documents first.")
        return

    # Clear history button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.chat_history = []
            st.rerun()

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg['content'])
                if 'sources' in msg:
                    with st.expander("📚 Sources"):
                        for source in msg['sources']:
                            st.caption(f"[{source['lens']}] {source['source_file']}")

    # Question input
    question = st.chat_input("Ask a question about your materials...")

    if question:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': question
        })

        # Get answer
        try:
            with st.spinner("Searching and generating answer..."):
                chunks = retrieve_chunks(question, top_k=10)

                if not chunks:
                    answer = "I couldn't find relevant information in your indexed materials."
                    sources = []
                else:
                    # Build context
                    context = "\n\n".join([f"[{c['lens']}] {c['content']}" for c in chunks])

                    # Call Claude
                    import anthropic
                    import httpx
                    client = anthropic.Anthropic(
                        api_key=os.getenv("ANTHROPIC_API_KEY"),
                        http_client=httpx.Client(verify=False)  # Disable SSL verification
                    )
                    message = client.messages.create(
                        model="claude-opus-4-5-20251101",
                        max_tokens=2000,
                        messages=[
                            {"role": "user", "content": f"Context from documents:\n{context}\n\nQuestion: {question}"}
                        ]
                    )

                    answer = message.content[0].text
                    sources = [{'lens': c['lens'], 'source_file': c['source_file']} for c in chunks[:5]]

                # Add assistant message
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': answer,
                    'sources': sources
                })

                st.rerun()

        except Exception as e:
            st.error(f"Error generating answer: {e}")


# ========== PAGE: OPEN QUESTIONS ==========

def page_open_questions():
    st.title("📝 Open Questions")
    st.markdown("Track open questions, submit answers, and manage the decision log")

    # Load data
    questions = load_questions()
    answers = load_answers()
    decisions = load_decisions()

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Pending Questions", "✅ Answer Question", "📜 Decision Log"])

    # ========== TAB 1: PENDING QUESTIONS ==========
    with tab1:
        st.subheader("Pending Questions")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            audience_filter = st.selectbox("Audience", ["All", "engineering", "leadership", "product"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "critical", "high", "medium", "low"])
        with col3:
            category_filter = st.selectbox("Category", ["All", "feasibility", "investment", "direction", "trade-off", "alignment", "timing", "scope", "dependency"])

        # Filter questions
        pending = [q for q in questions if q.get("status", "pending") == "pending"]

        if audience_filter != "All":
            pending = [q for q in pending if q.get("audience", "") == audience_filter]
        if priority_filter != "All":
            pending = [q for q in pending if q.get("priority", "") == priority_filter]
        if category_filter != "All":
            pending = [q for q in pending if q.get("category", "") == category_filter]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        total_pending = len([q for q in questions if q.get("status", "pending") == "pending"])
        critical_count = len([q for q in pending if q.get("priority", "") == "critical"])
        answered_count = len([q for q in questions if q.get("status", "") == "answered"])
        decisions_count = len(decisions)

        col1.metric("Total Pending", total_pending)
        col2.metric("Critical", critical_count)
        col3.metric("Answered", answered_count)
        col4.metric("Decisions Made", decisions_count)

        st.markdown("---")

        if not pending:
            st.info("No pending questions match your filters.")
        else:
            # Display questions by audience
            for audience in ["engineering", "leadership", "product"]:
                audience_qs = [q for q in pending if q.get("audience", "") == audience]
                if not audience_qs:
                    continue

                st.markdown(f"### {audience.title()} ({len(audience_qs)})")

                # Sort by priority
                priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
                sorted_qs = sorted(audience_qs, key=lambda x: priority_order.get(x.get("priority", "low"), 4))

                for q in sorted_qs:
                    priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(q.get("priority", "medium"), "⚪")
                    question_preview = q['question'][:80] + "..." if len(q['question']) > 80 else q['question']

                    with st.expander(f"{priority_emoji} {question_preview}"):
                        st.write(f"**Question:** {q['question']}")
                        st.write(f"**Category:** {q.get('category', 'N/A')}")
                        st.write(f"**Priority:** {q.get('priority', 'medium')}")
                        st.write(f"**Context:** {q.get('context', 'None provided')}")

                        if q.get("related_roadmap_items"):
                            st.write(f"**Affects:** {', '.join(q['related_roadmap_items'])}")

                        st.write(f"**Created:** {q.get('created_at', 'Unknown')[:10]}")

                        # Quick actions
                        col1, col2 = st.columns(2)
                        if col1.button("Defer", key=f"def_{q['id']}"):
                            q["status"] = "deferred"
                            save_questions(questions)
                            st.success("Question deferred")
                            st.rerun()
                        if col2.button("Mark Obsolete", key=f"obs_{q['id']}"):
                            q["status"] = "obsolete"
                            save_questions(questions)
                            st.success("Question marked obsolete")
                            st.rerun()

    # ========== TAB 2: ANSWER QUESTION ==========
    with tab2:
        st.subheader("Answer Question")

        # Select question to answer
        pending = [q for q in questions if q.get("status", "pending") == "pending"]

        if not pending:
            st.info("No pending questions. Questions will be generated after roadmap synthesis.")
        else:
            question_options = {f"{q['id']}: {q['question'][:60]}...": q['id'] for q in pending}
            selected = st.selectbox("Select Question", list(question_options.keys()))

            if selected:
                q_id = question_options[selected]
                question = next(q for q in pending if q["id"] == q_id)

                st.markdown(f"**Question:** {question['question']}")
                st.markdown(f"**Context:** {question.get('context', 'None')}")
                st.markdown(f"**Audience:** {question.get('audience', 'N/A')} | **Category:** {question.get('category', 'N/A')}")

                if question.get("related_roadmap_items"):
                    st.markdown(f"**Affects:** {', '.join(question['related_roadmap_items'])}")

                st.markdown("---")

                # Answer form
                answer_text = st.text_area("Your Answer", height=150, key=f"answer_{q_id}")
                answered_by = st.text_input("Answered By", key=f"by_{q_id}")
                confidence = st.select_slider("Confidence", options=["low", "medium", "high"], value="medium", key=f"conf_{q_id}")

                create_decision = st.checkbox("Create Decision Record", value=True, key=f"dec_{q_id}")

                if create_decision:
                    st.markdown("#### Decision Details")
                    decision_text = st.text_area("Decision (leave blank to use answer)", height=100, key=f"dtext_{q_id}")
                    rationale = st.text_input("Rationale", key=f"rat_{q_id}")
                    implications = st.text_input("Implications (comma-separated)", key=f"imp_{q_id}")
                    owner = st.text_input("Owner", value=answered_by, key=f"own_{q_id}")

                if st.button("Submit Answer", type="primary", key=f"submit_{q_id}"):
                    if not answer_text or not answered_by:
                        st.error("Please provide answer and your name")
                    else:
                        # Save answer
                        answer_record = {
                            "id": f"ans_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "question_id": q_id,
                            "answer": answer_text,
                            "answered_by": answered_by,
                            "answered_at": datetime.now().isoformat(),
                            "confidence": confidence,
                            "follow_up_needed": False,
                            "notes": ""
                        }
                        answers.append(answer_record)
                        save_answers(answers)

                        # Save decision if requested
                        if create_decision:
                            decision_record = {
                                "id": f"dec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                "question_id": q_id,
                                "answer_id": answer_record["id"],
                                "decision": decision_text or answer_text,
                                "rationale": rationale,
                                "implications": [i.strip() for i in implications.split(",") if i.strip()],
                                "owner": owner or answered_by,
                                "review_date": None,
                                "status": "active",
                                "created_at": datetime.now().isoformat()
                            }
                            decisions.append(decision_record)
                            save_decisions(decisions)
                            st.success(f"Answer and decision recorded!")
                        else:
                            st.success("Answer recorded!")

                        # Update question status
                        question["status"] = "answered"
                        save_questions(questions)

                        st.rerun()

    # ========== TAB 3: DECISION LOG ==========
    with tab3:
        st.subheader("Decision Log")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_superseded = st.checkbox("Show superseded decisions")
        with col2:
            date_filter = st.date_input("Since", value=None)

        # Filter decisions
        filtered_decisions = decisions
        if not show_superseded:
            filtered_decisions = [d for d in filtered_decisions if d.get("status", "active") == "active"]
        if date_filter:
            date_str = str(date_filter)
            filtered_decisions = [d for d in filtered_decisions if d.get("created_at", "")[:10] >= date_str]

        # Sort by date
        filtered_decisions = sorted(filtered_decisions, key=lambda x: x.get("created_at", ""), reverse=True)

        st.markdown(f"**Total Decisions:** {len(filtered_decisions)}")
        st.markdown("---")

        if not filtered_decisions:
            st.info("No decisions recorded yet. Answer questions to create decisions.")
        else:
            # Display
            for dec in filtered_decisions:
                status_icon = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec.get("status", "active"), "?")
                created = dec.get("created_at", "Unknown")[:10]
                decision_preview = dec['decision'][:60] + "..." if len(dec['decision']) > 60 else dec['decision']

                with st.expander(f"{status_icon} {decision_preview} ({created})"):
                    st.write(f"**Decision:** {dec['decision']}")
                    st.write(f"**Rationale:** {dec.get('rationale', 'None provided')}")

                    if dec.get("implications"):
                        st.write("**Implications:**")
                        for imp in dec["implications"]:
                            st.write(f"  • {imp}")

                    st.write(f"**Owner:** {dec.get('owner', 'Unassigned')}")
                    st.write(f"**Status:** {dec.get('status', 'active')}")

                    # Link to original question
                    question_id = dec.get("question_id")
                    if question_id:
                        question = next((q for q in questions if q["id"] == question_id), None)
                        if question:
                            st.write(f"**Original Question:** {question['question']}")

                    # Actions
                    if dec.get("status", "active") == "active":
                        col1, col2 = st.columns(2)
                        if col1.button("Mark for Review", key=f"rev_{dec['id']}"):
                            dec["status"] = "revisiting"
                            save_decisions(decisions)
                            st.success("Decision marked for review")
                            st.rerun()
                        if col2.button("Supersede", key=f"sup_{dec['id']}"):
                            dec["status"] = "superseded"
                            save_decisions(decisions)
                            st.success("Decision superseded")
                            st.rerun()

            # Export button
            st.markdown("---")
            if st.button("📥 Export Decision Log"):
                md_lines = [
                    "# Decision Log",
                    f"\nGenerated: {datetime.now().isoformat()}",
                    f"Total Decisions: {len(filtered_decisions)}\n",
                    "---\n"
                ]

                for dec in filtered_decisions:
                    status_emoji = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec.get("status", "active"), "?")
                    created = dec.get("created_at", "Unknown")[:10]

                    md_lines.append(f"## {status_emoji} {dec['id']} ({created})\n")
                    md_lines.append(f"**Decision:** {dec['decision']}\n")

                    if dec.get("rationale"):
                        md_lines.append(f"**Rationale:** {dec['rationale']}\n")

                    if dec.get("implications"):
                        md_lines.append("**Implications:**")
                        for imp in dec["implications"]:
                            md_lines.append(f"- {imp}")
                        md_lines.append("")

                    md_lines.append(f"**Owner:** {dec.get('owner', 'Unassigned')}")
                    md_lines.append(f"**Status:** {dec.get('status', 'active')}")

                    question_id = dec.get("question_id")
                    if question_id:
                        md_lines.append(f"**Question ID:** {question_id}")

                    md_lines.append("\n---\n")

                md_content = "\n".join(md_lines)

                st.download_button(
                    "Download Markdown",
                    md_content,
                    file_name=f"decision_log_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )


# ========== PAGE: ARCHITECTURE ALIGNMENT ==========

def page_architecture_alignment():
    st.title("🏗️ Architecture Alignment Analysis")

    st.markdown("""
    This analysis maps functional roadmap items to technical architecture to identify:
    - Whether architecture supports planned features
    - Required technical changes
    - Technical risks and dependencies
    - Engineering questions that need answers
    """)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📄 Architecture Docs", "❓ Engineering Questions"])

    # ========== TAB 1: ANALYSIS ==========
    with tab1:
        st.subheader("Roadmap-Architecture Alignment")

        # Check for existing analysis
        alignment_file = OUTPUT_DIR / "architecture-alignment.json"

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Run Analysis", type="primary"):
                # Check if roadmap exists
                roadmap_file = OUTPUT_DIR / "master_roadmap.md"
                if not roadmap_file.exists():
                    st.error("Roadmap not found. Generate a roadmap first.")
                else:
                    # Check if documents are selected
                    selected_paths = st.session_state.get('selected_doc_paths', [])
                    if not selected_paths:
                        st.error("⚠️ No documents selected. Go to 'Architecture Docs' tab and select documents.")
                    else:
                        with st.spinner("Loading selected architecture documents..."):
                            arch_docs, metadata = load_architecture_documents(selected_files=selected_paths)

                        if not arch_docs:
                            st.error("No documents could be loaded. Check the Architecture Docs tab for details.")
                        else:
                            with st.spinner(f"Analyzing alignment ({len(arch_docs)} docs, {metadata['total_tokens']:,} tokens)... This may take 1-2 minutes"):
                                roadmap_content = roadmap_file.read_text()
                                roadmap = parse_roadmap_for_analysis(roadmap_content)
                                analysis = generate_architecture_alignment(roadmap, arch_docs, use_opus=True)
                                save_alignment_analysis(analysis)

                                # Add questions to system
                                questions = extract_engineering_questions_from_alignment(analysis)
                                added = add_architecture_questions_to_system(questions)

                            st.success(f"Analysis complete! {added} engineering questions added to Open Questions.")
                            st.rerun()

        if alignment_file.exists():
            analysis = load_alignment_analysis()

            # Summary metrics
            assessments = analysis.get("assessments", [])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Items Analyzed", len(assessments))
            col2.metric("Full Support", len([a for a in assessments if a.get("architecture_supports") == "full"]))
            col3.metric("Partial Support", len([a for a in assessments if a.get("architecture_supports") == "partial"]))
            col4.metric("No Support", len([a for a in assessments if a.get("architecture_supports") == "no"]))

            st.markdown("---")

            # Filter
            support_filter = st.multiselect(
                "Filter by support level",
                ["full", "partial", "no", "unknown"],
                default=["partial", "no"]
            )

            # Display assessments
            filtered_assessments = [a for a in assessments if a.get("architecture_supports") in support_filter]

            for assessment in filtered_assessments:
                support_icon = {
                    "full": "✅",
                    "partial": "⚠️",
                    "no": "❌",
                    "unknown": "❓"
                }.get(assessment.get("architecture_supports", "unknown"), "❓")

                with st.expander(f"{support_icon} {assessment.get('roadmap_item', 'Unknown')} ({assessment.get('horizon', 'N/A')})"):
                    st.write(f"**Description:** {assessment.get('roadmap_item_description', 'N/A')}")
                    st.write(f"**Architecture Support:** {assessment.get('architecture_supports', 'N/A')} (confidence: {assessment.get('confidence', 'N/A')})")
                    st.write(f"**Summary:** {assessment.get('summary', 'N/A')}")

                    # Supporting components
                    if assessment.get("supporting_components"):
                        st.write("**Supporting Components:**")
                        for comp in assessment["supporting_components"]:
                            st.write(f"  • {comp}")

                    # Required changes
                    if assessment.get("required_changes"):
                        st.write("**Required Changes:**")
                        for change in assessment["required_changes"]:
                            blocking = "🚫 BLOCKING" if change.get("blocking") else ""
                            st.write(f"  • **{change.get('component', 'N/A')}** ({change.get('change_type', 'N/A')}, {change.get('effort', 'N/A')}) — {change.get('description', 'N/A')} {blocking}")

                    # Technical risks
                    if assessment.get("technical_risks"):
                        st.write("**Technical Risks:**")
                        for risk in assessment["technical_risks"]:
                            severity_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(risk.get("severity", "low"), "⚪")
                            st.write(f"  {severity_color} {risk.get('risk', 'N/A')}")
                            st.write(f"     Mitigation: {risk.get('mitigation', 'N/A')}")

                    # Dependencies
                    deps = assessment.get("dependencies", {})
                    if deps.get("prerequisite_work"):
                        st.write(f"**Prerequisites:** {', '.join(deps['prerequisite_work'])}")
                    if deps.get("enables"):
                        st.write(f"**Enables:** {', '.join(deps['enables'])}")

                    # Questions
                    if assessment.get("questions"):
                        st.write(f"**Engineering Questions:** {len(assessment['questions'])}")
                        for q in assessment["questions"]:
                            st.write(f"  • [{q.get('priority', 'N/A')}] {q.get('question', 'N/A')}")

            # Cross-cutting concerns
            cross_cutting = analysis.get("cross_cutting_concerns", {})

            if cross_cutting:
                st.markdown("---")
                st.subheader("Cross-Cutting Concerns")

                if cross_cutting.get("architectural_gaps"):
                    st.write("**Architectural Gaps:**")
                    for gap in cross_cutting["architectural_gaps"]:
                        st.write(f"  • {gap}")

                if cross_cutting.get("systemic_risks"):
                    st.write("**Systemic Risks:**")
                    for risk in cross_cutting["systemic_risks"]:
                        st.write(f"  • {risk}")

                if cross_cutting.get("recommended_adrs"):
                    st.write("**Recommended ADRs:**")
                    for adr in cross_cutting["recommended_adrs"]:
                        st.write(f"  • {adr}")

                if cross_cutting.get("sequencing_recommendations"):
                    st.write("**Sequencing Recommendations:**")
                    st.write(cross_cutting["sequencing_recommendations"])

            # Export
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                md_content = format_alignment_report(analysis)
                st.download_button(
                    "📥 Export as Markdown",
                    md_content,
                    file_name="architecture-alignment.md",
                    mime="text/markdown"
                )
            with col2:
                import json
                st.download_button(
                    "📥 Export as JSON",
                    json.dumps(analysis, indent=2),
                    file_name="architecture-alignment.json",
                    mime="application/json"
                )

        else:
            st.info("No analysis found. Click 'Run Analysis' to analyze roadmap against architecture.")

    # ========== TAB 2: ARCHITECTURE DOCS ==========
    with tab2:
        st.subheader("Architecture Documents")

        # Upload section
        st.markdown("### Upload Architecture Documents")

        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox(
                "Document Type",
                ["architecture", "tech-specs"],
                help="Choose where to save the document"
            )

        uploaded_files = st.file_uploader(
            "Upload architecture documents (.md, .txt, .rst)",
            type=["md", "txt", "rst"],
            accept_multiple_files=True,
            help="Upload architecture documents, technical specs, or design docs"
        )

        if uploaded_files:
            if st.button("💾 Save Documents", type="primary"):
                # Create directory if it doesn't exist
                target_dir = Path(f"materials/engineering/{doc_type}")
                target_dir.mkdir(parents=True, exist_ok=True)

                saved_files = []
                for uploaded_file in uploaded_files:
                    # Save file
                    file_path = target_dir / uploaded_file.name
                    file_path.write_bytes(uploaded_file.getvalue())
                    saved_files.append(uploaded_file.name)

                st.success(f"✓ Successfully saved {len(saved_files)} document(s) to {target_dir}")

                # Show uploaded files
                with st.expander("📄 Uploaded Files", expanded=True):
                    for filename in saved_files:
                        st.write(f"  • {filename}")

                st.info("Documents will be loaded when you run the next analysis")

                # Wait a moment before rerun
                import time
                time.sleep(1)
                st.rerun()

        st.markdown("---")
        st.markdown("### Manage Architecture Files")

        # List files from both directories
        st.markdown("**Architecture Documents:**")
        arch_dir = Path("materials/engineering/architecture")
        if arch_dir.exists():
            arch_files = list(arch_dir.rglob("*"))
            arch_files = [f for f in arch_files if f.is_file() and f.suffix in ['.md', '.txt', '.rst']]

            if arch_files:
                for file_path in sorted(arch_files):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"📄 {file_path.name}")
                    with col2:
                        file_size = file_path.stat().st_size
                        st.text(f"{file_size / 1024:.1f} KB")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_arch_{file_path.name}"):
                            file_path.unlink()
                            st.success(f"Deleted {file_path.name}")
                            st.rerun()
            else:
                st.info("No files in architecture/ directory")
        else:
            st.info("architecture/ directory not created yet")

        st.markdown("**Technical Specs:**")
        specs_dir = Path("materials/engineering/tech-specs")
        if specs_dir.exists():
            spec_files = list(specs_dir.rglob("*"))
            spec_files = [f for f in spec_files if f.is_file() and f.suffix in ['.md', '.txt', '.rst']]

            if spec_files:
                for file_path in sorted(spec_files):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.text(f"📄 {file_path.name}")
                    with col2:
                        file_size = file_path.stat().st_size
                        st.text(f"{file_size / 1024:.1f} KB")
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_spec_{file_path.name}"):
                            file_path.unlink()
                            st.success(f"Deleted {file_path.name}")
                            st.rerun()
            else:
                st.info("No files in tech-specs/ directory")
        else:
            st.info("tech-specs/ directory not created yet")

        st.markdown("---")
        st.markdown("### Select Documents for Analysis")
        st.caption("Choose which architecture documents to include (max 200K tokens total)")

        try:
            # Scan available documents
            available_docs = scan_architecture_documents()

            if not available_docs:
                st.warning("⚠️ No architecture documents found in materials/engineering/")
                st.info("Upload documents in the 'Architecture Docs' tab above")
            else:
                st.success(f"📚 Found {len(available_docs)} architecture documents")

                # Initialize session state for document selection
                if 'selected_doc_paths' not in st.session_state:
                    # Auto-select documents that fit in budget (up to 200K tokens)
                    st.session_state.selected_doc_paths = []
                    running_total = 0
                    for doc in available_docs:
                        if not doc['too_large'] and running_total + doc['token_count'] <= 200000:
                            st.session_state.selected_doc_paths.append(doc['path'])
                            running_total += doc['token_count']

                # Document selection UI
                st.markdown("**Select documents to include in analysis:**")

                selected_paths = []
                running_tokens = 0

                for doc in available_docs:
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        is_selected = st.checkbox(
                            doc['title'],
                            value=doc['path'] in st.session_state.selected_doc_paths,
                            key=f"doc_select_{doc['path']}",
                            disabled=doc['too_large']
                        )

                        if is_selected:
                            selected_paths.append(doc['path'])
                            running_tokens += doc['token_count']

                    with col2:
                        token_color = "red" if doc['too_large'] else "green" if doc['token_count'] < 50000 else "orange"
                        st.markdown(f":{token_color}[{doc['token_count']:,} tokens]")

                    with col3:
                        st.caption(f"{doc['file_size'] / 1024:.1f} KB")

                    if doc['too_large']:
                        st.warning(f"⚠️ This document exceeds the 200K token limit per file and cannot be loaded")

                # Update session state
                st.session_state.selected_doc_paths = selected_paths

                # Show running total
                st.markdown("---")
                budget_color = "red" if running_tokens > 200000 else "green"
                st.markdown(f"**Selected:** {len(selected_paths)} documents | **Total Tokens:** :{budget_color}[{running_tokens:,} / 200,000]")

                if running_tokens > 200000:
                    st.error("⚠️ Selected documents exceed the 200K token budget. Deselect some documents.")
                elif running_tokens == 0:
                    st.info("ℹ️ Select at least one document to run analysis")
                else:
                    # Load selected documents
                    with st.spinner("Loading selected documents..."):
                        docs, metadata = load_architecture_documents(selected_files=selected_paths)

                    if metadata['skipped_count'] > 0:
                        with st.expander(f"⚠️ {metadata['skipped_count']} documents were skipped"):
                            for skipped in metadata['skipped_files']:
                                st.warning(f"**{skipped['name']}**: {skipped['reason']}")

                    # Show loaded documents
                    st.success(f"✓ **{len(docs)} documents loaded** ({metadata['total_tokens']:,} tokens)")

                    for doc in docs:
                        with st.expander(f"📄 {doc['title']} ({doc['token_count']:,} tokens)"):
                            st.write(f"**Path:** {doc['path']}")
                            st.write(f"**Type:** {doc['doc_type']}")
                            st.write(f"**Last Updated:** {doc.get('last_updated', 'Unknown')[:10]}")

                            if doc.get('key_components'):
                                st.write(f"**Key Components:** {', '.join(doc['key_components'][:10])}")

        except Exception as e:
            st.error(f"❌ Error scanning documents: {e}")
            import traceback
            st.code(traceback.format_exc())

    # ========== TAB 3: ENGINEERING QUESTIONS ==========
    with tab3:
        st.subheader("Engineering Questions from Architecture Analysis")

        questions = load_questions()
        arch_questions = [q for q in questions if q.get("source") == "architecture_alignment"]

        if not arch_questions:
            st.info("No architecture-related questions yet. Run an analysis to generate questions.")
        else:
            pending = [q for q in arch_questions if q.get("status") == "pending"]
            answered = [q for q in arch_questions if q.get("status") == "answered"]

            st.write(f"**{len(pending)} pending** | {len(answered)} answered")

            for q in sorted(pending, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority", "low"), 4)):
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(q.get("priority", "medium"), "⚪")

                with st.expander(f"{priority_icon} {q.get('question', 'N/A')[:80]}..."):
                    st.write(f"**Question:** {q.get('question', 'N/A')}")
                    st.write(f"**Category:** {q.get('category', 'N/A')}")
                    st.write(f"**Context:** {q.get('context', 'N/A')}")

                    if q.get("related_component"):
                        st.write(f"**Component:** {q['related_component']}")

                    if q.get("related_roadmap_items"):
                        st.write(f"**Roadmap Items:** {', '.join(q['related_roadmap_items'])}")

                    st.markdown("---")
                    st.info("Go to the 📝 Open Questions page to answer this question")


# ========== PAGE: COMPETITIVE INTELLIGENCE ==========

def page_competitive_intelligence():
    st.title("🎯 Competitive Intelligence")

    st.markdown("""
    ### Analyst Assessment Tool

    This tool generates **objective analyst assessments** of competitor developments against your roadmap.

    **Important:** This produces analyst research notes, not strategy recommendations:
    - The roadmap is the source of truth
    - No new features or approaches are suggested
    - Questions are raised for leadership, not answered
    """)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Manage Developments", "📊 Run Assessment", "📄 View Assessments"])

    # ========== TAB 1: MANAGE DEVELOPMENTS ==========
    with tab1:
        st.subheader("Competitor Developments")

        st.markdown("### Add New Development")

        with st.form("add_development"):
            col1, col2 = st.columns(2)

            with col1:
                competitor = st.text_input("Competitor Name*", placeholder="e.g., Competitor X")
                dev_type = st.selectbox(
                    "Development Type*",
                    ["product_launch", "feature", "acquisition", "partnership", "funding", "strategy_shift"]
                )
                title = st.text_input("Title*", placeholder="e.g., AI-Powered Pricing Launch")

            with col2:
                source_url = st.text_input("Source URL*", placeholder="https://...")
                announced_date = st.date_input("Announced Date*")
                description = st.text_area("Description*", placeholder="Full description of the development...")

            submitted = st.form_submit_button("➕ Add Development", type="primary")

            if submitted:
                if not all([competitor, title, description, source_url]):
                    st.error("All fields are required")
                else:
                    try:
                        development = add_competitor_development(
                            competitor=competitor,
                            development_type=dev_type,
                            title=title,
                            description=description,
                            source_url=source_url,
                            announced_date=str(announced_date)
                        )
                        st.success(f"✓ Added development: {development['id']}")
                        st.info("Go to the 'Run Assessment' tab to analyze this development")
                        import time
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding development: {e}")

        st.markdown("---")
        st.markdown("### Existing Developments")

        developments = load_competitor_developments()

        if not developments:
            st.info("No competitor developments tracked yet. Add one above to get started.")
        else:
            for dev in developments:
                with st.expander(f"🔹 {dev['competitor']} — {dev['title']}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**ID:** {dev['id']}")
                        st.write(f"**Type:** {dev['development_type']}")

                    with col2:
                        st.write(f"**Announced:** {dev['announced_date']}")
                        st.write(f"**Added:** {dev['created_at'][:10]}")

                    with col3:
                        # Check if assessed
                        assessments = load_analyst_assessments()
                        assessed = any(a['development_id'] == dev['id'] for a in assessments)
                        if assessed:
                            st.success("✓ Assessed")
                        else:
                            st.warning("⧗ Not yet assessed")

                    st.write(f"**Description:** {dev['description']}")
                    st.write(f"**Source:** {dev['source_url']}")

    # ========== TAB 2: RUN ASSESSMENT ==========
    with tab2:
        st.subheader("Generate Analyst Assessment")

        st.info("**Note:** Assessments are objective analyst research notes, not strategy recommendations.")

        developments = load_competitor_developments()

        if not developments:
            st.warning("No competitor developments found. Add a development in the 'Manage Developments' tab first.")
        else:
            # Select development
            dev_options = {f"{d['id']} — {d['competitor']}: {d['title']}": d['id'] for d in developments}
            selected_label = st.selectbox("Select Development to Assess", list(dev_options.keys()))
            selected_id = dev_options[selected_label]

            development = get_competitor_development(selected_id)

            if development:
                st.markdown("---")
                st.markdown("### Development Details")
                st.write(f"**Competitor:** {development['competitor']}")
                st.write(f"**Title:** {development['title']}")
                st.write(f"**Type:** {development['development_type']}")
                st.write(f"**Announced:** {development['announced_date']}")
                st.write(f"**Description:** {development['description'][:200]}...")

                st.markdown("---")

                # Check prerequisites
                roadmap_file = OUTPUT_DIR / "master_roadmap.md"
                if not roadmap_file.exists():
                    st.error("⚠️ Roadmap not found. Generate a roadmap first.")
                else:
                    col1, col2 = st.columns([3, 1])

                    with col2:
                        use_opus = st.checkbox("Use Opus (higher quality)", value=True)

                    with col1:
                        if st.button("🔄 Run Analyst Assessment", type="primary"):
                            with st.spinner("Generating analyst assessment... This may take 1-2 minutes"):
                                try:
                                    assessment = generate_analyst_assessment(development, use_opus=use_opus)
                                    analysis = assessment['analysis']

                                    st.success("✓ Assessment Complete!")

                                    # Show summary
                                    st.markdown(f"### {analysis['headline']}")
                                    st.write(analysis['executive_summary'])

                                    st.markdown("---")

                                    col1, col2, col3 = st.columns(3)
                                    col1.metric("Impact", analysis['overall_impact'])
                                    col2.metric("Timeline", analysis['impact_timeline'])
                                    col3.metric("Confidence", analysis['confidence'])

                                    st.write(f"**Roadmap Strengths:** {len(analysis.get('roadmap_strengths', []))}")
                                    st.write(f"**Roadmap Gaps:** {len(analysis.get('roadmap_gaps', []))}")
                                    st.write(f"**Strategic Questions:** {len(analysis.get('strategic_questions', []))}")

                                    st.info(f"Strategic questions have been added to Open Questions for leadership review.")

                                    if assessment.get('validation_warnings'):
                                        with st.expander(f"⚠️ {len(assessment['validation_warnings'])} Validation Warnings"):
                                            for warning in assessment['validation_warnings']:
                                                st.warning(warning)

                                    st.rerun()

                                except Exception as e:
                                    st.error(f"Assessment failed: {e}")
                                    import traceback
                                    st.code(traceback.format_exc())

    # ========== TAB 3: VIEW ASSESSMENTS ==========
    with tab3:
        st.subheader("Analyst Assessments")

        assessments = load_analyst_assessments()

        if not assessments:
            st.info("No assessments generated yet. Run an assessment in the 'Run Assessment' tab.")
        else:
            st.success(f"📊 {len(assessments)} assessment(s) generated")

            for assessment in reversed(assessments):  # Most recent first
                analysis = assessment['analysis']
                development = assessment['development']

                with st.expander(f"📄 {analysis['headline']}", expanded=False):
                    st.write(f"**Assessed:** {assessment['assessed_at'][:10]}")
                    st.write(f"**Competitor:** {development['competitor']}")
                    st.write(f"**Development:** {development['title']}")

                    st.markdown("---")

                    st.markdown("### Executive Summary")
                    st.write(analysis['executive_summary'])

                    st.markdown("### Impact Assessment")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Impact", analysis['overall_impact'])
                    col2.metric("Timeline", analysis['impact_timeline'])
                    col3.metric("Confidence", analysis['confidence'])

                    # Roadmap Strengths
                    st.markdown("### Roadmap Strengths")
                    for strength in analysis.get('roadmap_strengths', []):
                        st.write(f"**{strength['roadmap_item']}** ({strength['horizon']} horizon)")
                        st.write(f"- Coverage: {strength['coverage_level']}")
                        st.write(f"- Timing: {strength['timing_adequacy']}")
                        st.write(f"- {strength['how_it_addresses']}")

                    # Roadmap Gaps
                    st.markdown("### Roadmap Gaps")
                    for gap in analysis.get('roadmap_gaps', []):
                        severity_color = {"critical": "🔴", "significant": "🟠", "moderate": "🟡", "minor": "🟢"}.get(gap['severity'], "⚪")
                        st.write(f"{severity_color} **{gap['gap_description']}**")
                        st.write(f"- Severity: {gap['severity']}")
                        st.write(f"- Competitor has: {gap['competitor_capability']}")

                    # Strategic Questions
                    st.markdown("### Strategic Questions Raised")
                    for i, q in enumerate(analysis.get('strategic_questions', []), 1):
                        st.write(f"{i}. **[{q['question_type'].upper()}]** {q['question']}")
                        st.write(f"   *{q['context']}*")

                    # Export
                    st.markdown("---")
                    markdown_content = format_analyst_assessment_markdown(assessment)
                    st.download_button(
                        "📥 Export as Markdown",
                        markdown_content,
                        file_name=f"competitive_assessment_{assessment['id']}.md",
                        mime="text/markdown",
                        key=f"export_{assessment['id']}"
                    )


# ========== PAGE: SETTINGS ==========

def page_settings():
    st.title("⚙️ Settings")
    st.markdown("Configure API keys and system settings")

    # API Keys section
    st.subheader("API Keys")

    current_anthropic = os.getenv("ANTHROPIC_API_KEY", "")
    current_voyage = os.getenv("VOYAGE_API_KEY", "")

    # Show masked keys
    if current_anthropic:
        st.info(f"Anthropic API Key: {current_anthropic[:10]}...{current_anthropic[-4:]}")
    if current_voyage:
        st.info(f"Voyage AI Key: {current_voyage[:10]}...{current_voyage[-4:]}")

    # Input new keys
    with st.form("api_keys"):
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=current_anthropic,
            type="password",
            help="Get from: https://console.anthropic.com/"
        )

        voyage_key = st.text_input(
            "Voyage AI API Key",
            value=current_voyage,
            type="password",
            help="Get from: https://dash.voyageai.com/"
        )

        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("💾 Save Settings", type="primary")
        with col2:
            test_button = st.form_submit_button("🧪 Test Connection")

        if save_button:
            if not anthropic_key or not voyage_key:
                st.error("Both API keys are required")
            else:
                save_env_vars(anthropic_key, voyage_key)
                st.success("✅ API keys saved successfully!")

        if test_button:
            try:
                validate_api_keys()
                st.success("✅ API keys are valid!")
            except Exception as e:
                st.error(f"❌ API key validation failed: {e}")

    # Configuration display
    st.divider()
    st.subheader("Current Configuration")

    config_data = {
        "Setting": ["Materials Directory", "Output Directory", "Data Directory", "Valid Lenses"],
        "Value": [
            str(MATERIALS_DIR),
            str(OUTPUT_DIR),
            str(DATA_DIR),
            ", ".join(VALID_LENSES)
        ]
    }
    st.table(pd.DataFrame(config_data))


# ========== MAIN APP ==========

def main():
    # Sidebar navigation
    st.sidebar.title("🗺️ Roadmap Synth")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📥 Ingest Materials",
            "📁 Manage Materials",
            "🔍 View Chunks",
            "🔍 Chunking Audit",
            "🕸️ Context Graph",
            "🔧 Generate Roadmap",
            "👥 Format by Persona",
            "❓ Ask Questions",
            "📝 Open Questions",
            "🏗️ Architecture Alignment",
            "🎯 Competitive Intelligence",
            "⚙️ Settings"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Built with Streamlit & Claude")

    # Route to pages
    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📥 Ingest Materials":
        page_ingest()
    elif page == "📁 Manage Materials":
        page_manage()
    elif page == "🔍 View Chunks":
        page_chunks()
    elif page == "🔍 Chunking Audit":
        page_chunking_audit()
    elif page == "🕸️ Context Graph":
        page_context_graph()
    elif page == "🔧 Generate Roadmap":
        page_generate()
    elif page == "👥 Format by Persona":
        page_format()
    elif page == "❓ Ask Questions":
        page_ask()
    elif page == "📝 Open Questions":
        page_open_questions()
    elif page == "🏗️ Architecture Alignment":
        page_architecture_alignment()
    elif page == "🎯 Competitive Intelligence":
        page_competitive_intelligence()
    elif page == "⚙️ Settings":
        page_settings()


if __name__ == "__main__":
    main()
