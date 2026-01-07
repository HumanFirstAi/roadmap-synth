"""
Unit tests for document parsing functions in roadmap.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from roadmap import parse_document


class TestParseDocument:
    """Tests for document parsing."""

    @pytest.mark.unit
    def test_parse_text_file(self, temp_dir):
        """Test parsing a simple text file."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_content = "This is a test document.\n\nIt has multiple paragraphs."
        test_file.write_text(test_content)

        # Mock partition to return simple elements
        mock_element1 = Mock()
        mock_element1.text = "This is a test document."
        mock_element2 = Mock()
        mock_element2.text = "It has multiple paragraphs."

        with patch("roadmap.partition", return_value=[mock_element1, mock_element2]):
            result = parse_document(test_file)

        assert isinstance(result, str)
        assert "test document" in result.lower()
        assert "paragraphs" in result.lower()

    @pytest.mark.unit
    def test_parse_with_elements_without_text(self, temp_dir):
        """Test parsing when some elements don't have text attribute."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        # Mix of elements with and without text
        mock_element1 = Mock()
        mock_element1.text = "Has text"
        mock_element2 = Mock(spec=[])  # No text attribute
        mock_element3 = Mock()
        mock_element3.text = "Also has text"

        with patch("roadmap.partition", return_value=[mock_element1, mock_element2, mock_element3]):
            result = parse_document(test_file)

        assert "Has text" in result
        assert "Also has text" in result
        # Should skip element without text attribute

    @pytest.mark.unit
    def test_parse_empty_file(self, temp_dir):
        """Test parsing an empty file."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")

        with patch("roadmap.partition", return_value=[]):
            result = parse_document(test_file)

        assert result == ""

    @pytest.mark.unit
    def test_parse_file_with_special_characters(self, temp_dir):
        """Test parsing file with special characters."""
        test_file = temp_dir / "special.txt"
        test_file.write_text("Special chars: éñ™©")

        mock_element = Mock()
        mock_element.text = "Special chars: éñ™©"

        with patch("roadmap.partition", return_value=[mock_element]):
            result = parse_document(test_file)

        assert "Special chars" in result
        assert "éñ™©" in result

    @pytest.mark.unit
    def test_parse_nonexistent_file(self, temp_dir):
        """Test parsing a file that doesn't exist."""
        test_file = temp_dir / "nonexistent.txt"

        with patch("roadmap.partition", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                parse_document(test_file)

    @pytest.mark.unit
    def test_parse_handles_partition_errors(self, temp_dir):
        """Test that parse_document re-raises errors from partition."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test")

        with patch("roadmap.partition", side_effect=Exception("Parse error")):
            with pytest.raises(Exception) as exc_info:
                parse_document(test_file)

            assert "Parse error" in str(exc_info.value)

    @pytest.mark.unit
    def test_parse_joins_with_double_newlines(self, temp_dir):
        """Test that elements are joined with double newlines."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test")

        mock_element1 = Mock()
        mock_element1.text = "First"
        mock_element2 = Mock()
        mock_element2.text = "Second"

        with patch("roadmap.partition", return_value=[mock_element1, mock_element2]):
            result = parse_document(test_file)

        assert result == "First\n\nSecond"

    @pytest.mark.unit
    def test_parse_different_file_types(self, temp_dir):
        """Test parsing different supported file types."""
        file_types = [".txt", ".md", ".pdf", ".docx"]

        for ext in file_types:
            test_file = temp_dir / f"test{ext}"
            test_file.write_text("Test content")

            mock_element = Mock()
            mock_element.text = f"Content from {ext} file"

            with patch("roadmap.partition", return_value=[mock_element]):
                result = parse_document(test_file)

            assert f"Content from {ext} file" in result

    @pytest.mark.unit
    def test_parse_preserves_order(self, temp_dir):
        """Test that element order is preserved."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test")

        elements = []
        for i in range(5):
            elem = Mock()
            elem.text = f"Element {i}"
            elements.append(elem)

        with patch("roadmap.partition", return_value=elements):
            result = parse_document(test_file)

        lines = result.split("\n\n")
        for i, line in enumerate(lines):
            assert line == f"Element {i}"
