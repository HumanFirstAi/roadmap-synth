# Quick Win #8: View Original Document from Source References

## Overview

Add ability to view the full original document when looking at source references for a question. This lets you validate the question against the complete context, not just the chunk excerpt.

---

## Feature

When viewing source references for a question:

```
┌──────────────────────────────────────────────────────────┐
│ 📄 Catalog Roadmap (team-structured)              [87%]  │
│ ID: chunk_123 | 🎯 semantic                              │
│                                                          │
│ "Q2 timeline is aggressive given current team            │
│ capacity and the dependency on..."                       │
│                                                          │
│ [📄 View Original] [📥 Download]      ← NEW BUTTONS      │
└──────────────────────────────────────────────────────────┘
```

Clicking "View Original" opens an expander with the full document:

```
┌──────────────────────────────────────────────────────────┐
│ 📄 Original Document: Catalog_Roadmap.md          [✕]   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ File: materials/team-structured/Catalog_Roadmap.md       │
│ Size: 4,523 bytes | Last modified: 2025-01-10           │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ # Catalog Roadmap 2025                               ││
│ │                                                      ││
│ │ ## Overview                                          ││
│ │ The Catalog service is our core product...           ││
│ │                                                      ││
│ │ ## Timeline                                          ││
│ │ Q2 timeline is aggressive given current team         ││  ← Highlighted
│ │ capacity and the dependency on API migration...      ││
│ │                                                      ││
│ │ ## Dependencies                                      ││
│ │ ...                                                  ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
│ Chunk location: Lines 45-52 (approx)                    │
│                                                          │
│ [📥 Download Full Document]                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation

### 1. Get Original Document Content

```python
from pathlib import Path
import os
from datetime import datetime

def get_original_document(source_path: str) -> dict | None:
    """
    Load original document from source path.
    
    Returns dict with content, metadata, or None if not found.
    """
    
    path = Path(source_path)
    
    # Handle relative paths
    if not path.is_absolute():
        # Try common base paths
        for base in [".", "materials", "/home/user/roadmap-tool"]:
            full_path = Path(base) / path
            if full_path.exists():
                path = full_path
                break
    
    if not path.exists():
        return None
    
    try:
        # Get file metadata
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        size = stat.st_size
        
        # Read content based on file type
        suffix = path.suffix.lower()
        
        if suffix in [".txt", ".md", ".json", ".csv", ".yaml", ".yml"]:
            # Plain text files
            content = path.read_text(encoding="utf-8", errors="replace")
            content_type = "text"
        
        elif suffix in [".pdf"]:
            # PDF - extract text if possible
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                content = "\n\n".join(page.extract_text() for page in reader.pages)
                content_type = "pdf_extracted"
            except:
                content = f"[PDF file - {size} bytes - text extraction not available]"
                content_type = "binary"
        
        elif suffix in [".docx"]:
            # Word doc - extract text if possible
            try:
                import docx
                doc = docx.Document(str(path))
                content = "\n\n".join(para.text for para in doc.paragraphs)
                content_type = "docx_extracted"
            except:
                content = f"[Word document - {size} bytes - text extraction not available]"
                content_type = "binary"
        
        elif suffix in [".pptx"]:
            # PowerPoint - extract text if possible
            try:
                from pptx import Presentation
                prs = Presentation(str(path))
                texts = []
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            texts.append(shape.text)
                content = "\n\n".join(texts)
                content_type = "pptx_extracted"
            except:
                content = f"[PowerPoint - {size} bytes - text extraction not available]"
                content_type = "binary"
        
        else:
            # Unknown type - try to read as text
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                content_type = "text"
            except:
                content = f"[Binary file - {size} bytes]"
                content_type = "binary"
        
        return {
            "path": str(path),
            "name": path.name,
            "size": size,
            "modified": modified,
            "content": content,
            "content_type": content_type,
            "suffix": suffix
        }
    
    except Exception as e:
        print(f"Error reading document: {e}")
        return None


def find_chunk_in_document(document_content: str, chunk_content: str) -> dict | None:
    """
    Find the approximate location of a chunk within the original document.
    
    Returns dict with line numbers and context, or None if not found.
    """
    
    if not document_content or not chunk_content:
        return None
    
    # Clean up for matching
    doc_lower = document_content.lower()
    
    # Try to find the chunk content (first 100 chars for matching)
    search_text = chunk_content[:100].lower().strip()
    
    # Remove extra whitespace for fuzzy matching
    import re
    search_text_normalized = re.sub(r'\s+', ' ', search_text)
    doc_normalized = re.sub(r'\s+', ' ', doc_lower)
    
    pos = doc_normalized.find(search_text_normalized[:50])
    
    if pos == -1:
        # Try with even shorter match
        pos = doc_normalized.find(search_text_normalized[:30])
    
    if pos == -1:
        return None
    
    # Calculate approximate line number
    text_before = document_content[:pos]
    start_line = text_before.count('\n') + 1
    
    # Estimate end line
    chunk_lines = chunk_content.count('\n')
    end_line = start_line + chunk_lines
    
    return {
        "start_line": start_line,
        "end_line": end_line,
        "char_position": pos
    }
```

### 2. Render Original Document Viewer

```python
def render_original_document_viewer(source: dict, chunk_content: str):
    """
    Render a viewer for the original document with chunk highlighting.
    """
    
    source_path = source.get("source_path", "")
    
    if not source_path:
        st.caption("Original document path not available")
        return
    
    # Load document
    doc = get_original_document(source_path)
    
    if not doc:
        st.warning(f"Could not load original document: {source_path}")
        return
    
    # Find chunk location
    location = find_chunk_in_document(doc["content"], chunk_content)
    
    # Document header
    st.markdown(f"**📄 Original Document:** `{doc['name']}`")
    
    col1, col2, col3 = st.columns(3)
    col1.caption(f"Size: {doc['size']:,} bytes")
    col2.caption(f"Modified: {doc['modified']}")
    col3.caption(f"Type: {doc['content_type']}")
    
    if location:
        st.caption(f"📍 Chunk location: Lines {location['start_line']}-{location['end_line']} (approx)")
    
    # Content display
    content = doc["content"]
    
    # Limit display size for very large files
    MAX_DISPLAY_CHARS = 50000
    truncated = False
    
    if len(content) > MAX_DISPLAY_CHARS:
        # If we know chunk location, center around it
        if location:
            start_char = max(0, location["char_position"] - 5000)
            end_char = min(len(content), location["char_position"] + 10000)
            content = f"... [truncated - showing around chunk location] ...\n\n{content[start_char:end_char]}\n\n... [truncated] ..."
        else:
            content = content[:MAX_DISPLAY_CHARS] + f"\n\n... [truncated - {len(doc['content']) - MAX_DISPLAY_CHARS:,} more characters]"
        truncated = True
    
    # Display content in scrollable container
    st.text_area(
        "Document Content",
        value=content,
        height=400,
        disabled=True,
        key=f"doc_content_{source.get('id', 'unknown')}"
    )
    
    if truncated:
        st.caption("Document truncated for display. Download for full content.")
    
    # Download button
    st.download_button(
        "📥 Download Full Document",
        doc["content"],
        file_name=doc["name"],
        mime="text/plain",
        key=f"download_{source.get('id', 'unknown')}"
    )
```

### 3. Integrate into Source Reference Display

Update `render_question_source_references()` to include the view original button:

```python
def render_question_source_references(question: dict):
    """
    Render source references for a question with original document access.
    """
    
    # ... existing source finding code ...
    
    for i, source in enumerate(sources):
        source_type = source.get("type", "chunk")
        source_id = source.get("id", "unknown")
        source_name = source.get("source_name", "Unknown Source")
        source_path = source.get("source_path", "")
        lens = source.get("lens", "")
        content = source.get("content", "")
        similarity = source.get("similarity", 0)
        search_method = source.get("search_method", "unknown")
        
        # Type icon
        type_icons = {
            "chunk": "📄",
            "assessment": "🔬",
            "roadmap_item": "🗺️",
            "gap": "⚠️",
            "decision": "✅"
        }
        icon = type_icons.get(source_type, "📎")
        
        with st.container(border=True):
            # Header row
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"{icon} **{source_name}**")
                
                meta_parts = []
                if lens and lens not in ["assessment", "gap", "roadmap"]:
                    meta_parts.append(f"Lens: {lens}")
                if source_id:
                    meta_parts.append(f"ID: {source_id[:20]}...")
                
                st.caption(" | ".join(meta_parts))
            
            with col2:
                # Relevance score
                score_pct = min(similarity * 100, 100)
                if score_pct >= 70:
                    st.success(f"{score_pct:.0f}%")
                elif score_pct >= 40:
                    st.warning(f"{score_pct:.0f}%")
                else:
                    st.caption(f"{score_pct:.0f}%")
            
            # Content excerpt
            if content:
                display_content = content[:250]
                if len(content) > 250:
                    display_content += "..."
                st.markdown(f"*\"{display_content}\"*")
            
            # === NEW: View Original Document ===
            if source_type == "chunk" and source_path:
                with st.expander("📄 View Original Document"):
                    render_original_document_viewer(source, content)
            
            elif source_type == "assessment":
                # For assessments, show the full assessment
                with st.expander("🔬 View Full Assessment"):
                    render_assessment_detail(source_id)
            
            elif source_type == "roadmap_item":
                # For roadmap items, show item detail
                with st.expander("🗺️ View Roadmap Item"):
                    render_roadmap_item_detail(source_id)
```

### 4. Helper Functions for Other Source Types

```python
def render_assessment_detail(assessment_id: str):
    """Render full assessment detail."""
    
    try:
        graph = load_unified_graph()
        if not graph:
            st.caption("Graph not available")
            return
        
        assessment = graph.node_indices.get("assessment", {}).get(assessment_id)
        
        if not assessment:
            st.caption(f"Assessment {assessment_id} not found")
            return
        
        data = assessment.__dict__ if hasattr(assessment, '__dict__') else assessment
        
        st.markdown(f"**Type:** {data.get('assessment_type', 'Unknown')}")
        st.markdown(f"**Created:** {data.get('created_at', 'Unknown')[:10]}")
        st.markdown(f"**Confidence:** {data.get('confidence', 'Unknown')}")
        
        st.divider()
        
        st.markdown("**Summary:**")
        st.write(data.get("summary", "No summary available"))
        
        # Show full assessment data
        if data.get("assessment_data"):
            with st.expander("Raw Assessment Data"):
                st.json(data["assessment_data"])
    
    except Exception as e:
        st.error(f"Error loading assessment: {e}")


def render_roadmap_item_detail(item_id: str):
    """Render roadmap item detail."""
    
    try:
        graph = load_unified_graph()
        if not graph:
            st.caption("Graph not available")
            return
        
        item = graph.node_indices.get("roadmap_item", {}).get(item_id)
        
        if not item:
            st.caption(f"Roadmap item {item_id} not found")
            return
        
        data = item.__dict__ if hasattr(item, '__dict__') else item
        
        st.markdown(f"### {data.get('name', 'Unknown')}")
        st.markdown(f"**Horizon:** {data.get('horizon', 'Unknown')}")
        st.markdown(f"**Theme:** {data.get('theme', 'Unknown')}")
        st.markdown(f"**Owner:** {data.get('owner', 'Unknown')}")
        
        st.divider()
        
        st.markdown("**Description:**")
        st.write(data.get("description", "No description available"))
        
        # Show gaps if any
        gaps = data.get("has_gaps", [])
        if gaps:
            st.markdown(f"**Gaps:** {len(gaps)}")
            for gap_id in gaps[:5]:
                st.caption(f"- {gap_id}")
        
        # Show questions if any
        questions = data.get("has_questions", [])
        if questions:
            st.markdown(f"**Open Questions:** {len(questions)}")
            for q_id in questions[:5]:
                st.caption(f"- {q_id}")
    
    except Exception as e:
        st.error(f"Error loading roadmap item: {e}")
```

### 5. Ensure source_path is Captured During Search

Update `find_sources_for_question()` to include `source_path`:

```python
def find_sources_for_question(question: dict, max_sources: int = 5) -> list[dict]:
    """Find sources - ensure source_path is included."""
    
    # ... existing code ...
    
    # In the semantic search section:
    for chunk in chunk_results:
        chunk_id = chunk.get("id", chunk.get("chunk_id", ""))
        if chunk_id in seen_ids:
            continue
        seen_ids.add(chunk_id)
        
        sources.append({
            "type": "chunk",
            "id": chunk_id,
            "source_name": chunk.get("source_name", chunk.get("source_path", "Unknown")),
            "source_path": chunk.get("source_path", ""),  # ← ENSURE THIS IS INCLUDED
            "lens": chunk.get("lens", "unknown"),
            "content": chunk.get("content", chunk.get("text", ""))[:300],
            "similarity": chunk.get("_distance", chunk.get("similarity", 0)),
            "search_method": "semantic"
        })
    
    # Same for keyword search section...
```

---

## Testing Checklist

- [ ] "View Original Document" button appears for chunk sources
- [ ] Text files (.md, .txt) display correctly
- [ ] Large files are truncated with message
- [ ] Chunk location is shown (approx line numbers)
- [ ] Download button works
- [ ] PDF extraction works (if pypdf installed)
- [ ] DOCX extraction works (if python-docx installed)
- [ ] PPTX extraction works (if python-pptx installed)
- [ ] Missing files show warning gracefully
- [ ] Assessment sources show full assessment
- [ ] Roadmap item sources show item detail

---

## Estimated Time

- get_original_document(): 15 min
- find_chunk_in_document(): 10 min
- render_original_document_viewer(): 15 min
- Integration: 10 min
- Testing: 10 min

**Total: ~1 hour**
