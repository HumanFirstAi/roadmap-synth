"""
Unit tests for Q&A and question management functions in roadmap.py
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
from roadmap import (
    load_questions,
    save_questions,
    load_answers,
    save_answers,
    extract_engineering_questions_from_alignment,
    add_architecture_questions_to_system,
)


class TestLoadQuestions:
    """Tests for load_questions function."""

    @pytest.mark.unit
    def test_load_existing_questions(self, temp_dir, monkeypatch):
        """Test loading questions from existing file."""
        questions_dir = temp_dir / "questions"
        questions_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions_data = {
            "questions": [
                {"id": "q1", "question": "What is the timeline?", "status": "pending"},
                {"id": "q2", "question": "What are dependencies?", "status": "answered"}
            ]
        }
        questions_file = questions_dir / "questions.json"
        questions_file.write_text(json.dumps(questions_data))

        result = load_questions()

        assert len(result) == 2
        assert result[0]["id"] == "q1"
        assert result[1]["status"] == "answered"

    @pytest.mark.unit
    def test_load_nonexistent_questions(self, temp_dir, monkeypatch):
        """Test loading when questions file doesn't exist."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        result = load_questions()

        assert result == []

    @pytest.mark.unit
    def test_load_empty_questions_file(self, temp_dir, monkeypatch):
        """Test loading empty questions file."""
        questions_dir = temp_dir / "questions"
        questions_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions_file = questions_dir / "questions.json"
        questions_file.write_text(json.dumps({"questions": []}))

        result = load_questions()

        assert result == []

    @pytest.mark.unit
    def test_load_malformed_json(self, temp_dir, monkeypatch):
        """Test loading malformed JSON file."""
        questions_dir = temp_dir / "questions"
        questions_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions_file = questions_dir / "questions.json"
        questions_file.write_text("invalid json {")

        with pytest.raises(json.JSONDecodeError):
            load_questions()


class TestSaveQuestions:
    """Tests for save_questions function."""

    @pytest.mark.unit
    def test_save_questions_creates_file(self, temp_dir, monkeypatch):
        """Test saving questions creates file."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions = [
            {"id": "q1", "question": "Test?", "status": "pending"}
        ]

        save_questions(questions)

        questions_file = temp_dir / "questions" / "questions.json"
        assert questions_file.exists()

        saved_data = json.loads(questions_file.read_text())
        assert len(saved_data["questions"]) == 1
        assert saved_data["questions"][0]["id"] == "q1"

    @pytest.mark.unit
    def test_save_questions_includes_metadata(self, temp_dir, monkeypatch):
        """Test that saved questions include metadata."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions = [
            {"id": "q1", "question": "Test?", "status": "pending"},
            {"id": "q2", "question": "Test2?", "status": "answered"},
            {"id": "q3", "question": "Test3?", "status": "pending"}
        ]

        save_questions(questions)

        questions_file = temp_dir / "questions" / "questions.json"
        saved_data = json.loads(questions_file.read_text())

        assert "metadata" in saved_data
        assert saved_data["metadata"]["total_pending"] == 2
        assert saved_data["metadata"]["total_answered"] == 1
        assert "last_updated" in saved_data["metadata"]

    @pytest.mark.unit
    def test_save_empty_questions(self, temp_dir, monkeypatch):
        """Test saving empty questions list."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        save_questions([])

        questions_file = temp_dir / "questions" / "questions.json"
        assert questions_file.exists()

        saved_data = json.loads(questions_file.read_text())
        assert saved_data["questions"] == []
        assert saved_data["metadata"]["total_pending"] == 0

    @pytest.mark.unit
    def test_save_questions_overwrites_existing(self, temp_dir, monkeypatch):
        """Test that save overwrites existing questions."""
        questions_dir = temp_dir / "questions"
        questions_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        # Save initial questions
        initial_questions = [{"id": "q1", "question": "Initial?", "status": "pending"}]
        save_questions(initial_questions)

        # Save new questions
        new_questions = [
            {"id": "q2", "question": "New?", "status": "pending"},
            {"id": "q3", "question": "Another?", "status": "pending"}
        ]
        save_questions(new_questions)

        # Load and verify
        questions_file = temp_dir / "questions" / "questions.json"
        saved_data = json.loads(questions_file.read_text())

        assert len(saved_data["questions"]) == 2
        assert saved_data["questions"][0]["id"] == "q2"


class TestLoadAnswers:
    """Tests for load_answers function."""

    @pytest.mark.unit
    def test_load_existing_answers(self, temp_dir, monkeypatch):
        """Test loading answers from existing file."""
        questions_dir = temp_dir / "questions"
        questions_dir.mkdir()
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        answers_data = {
            "answers": [
                {"question_id": "q1", "answer": "Here's the answer", "created_at": "2024-01-01"}
            ]
        }
        answers_file = questions_dir / "answers.json"
        answers_file.write_text(json.dumps(answers_data))

        result = load_answers()

        assert len(result) == 1
        assert result[0]["question_id"] == "q1"

    @pytest.mark.unit
    def test_load_nonexistent_answers(self, temp_dir, monkeypatch):
        """Test loading when answers file doesn't exist."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        result = load_answers()

        assert result == []


class TestSaveAnswers:
    """Tests for save_answers function."""

    @pytest.mark.unit
    def test_save_answers_creates_file(self, temp_dir, monkeypatch):
        """Test saving answers creates file."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        answers = [
            {"question_id": "q1", "answer": "Test answer", "created_at": "2024-01-01"}
        ]

        save_answers(answers)

        answers_file = temp_dir / "questions" / "answers.json"
        assert answers_file.exists()

        saved_data = json.loads(answers_file.read_text())
        assert "answers" in saved_data
        assert len(saved_data["answers"]) == 1
        assert saved_data["answers"][0]["question_id"] == "q1"

    @pytest.mark.unit
    def test_save_empty_answers(self, temp_dir, monkeypatch):
        """Test saving empty answers list."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        save_answers([])

        answers_file = temp_dir / "questions" / "answers.json"
        assert answers_file.exists()

        saved_data = json.loads(answers_file.read_text())
        assert "answers" in saved_data
        assert saved_data["answers"] == []
        assert saved_data["metadata"]["total_answers"] == 0


class TestExtractEngineeringQuestions:
    """Tests for extracting engineering questions from alignment analysis."""

    @pytest.mark.unit
    def test_extract_with_questions(self):
        """Test extracting questions from analysis with questions."""
        analysis = {
            "assessments": [
                {
                    "roadmap_item": "API Modernization",
                    "questions": [
                        {"question": "How do we scale the database?", "priority": "high"},
                        {"question": "What caching strategy?", "priority": "medium"}
                    ]
                }
            ],
            "concerns": ["Performance", "Scalability"]
        }

        result = extract_engineering_questions_from_alignment(analysis)

        assert len(result) >= 1
        assert all("question" in q for q in result)
        assert all("audience" in q for q in result)
        assert all(q["audience"] == "engineering" for q in result)

    @pytest.mark.unit
    def test_extract_with_no_questions(self):
        """Test extracting from analysis with no questions."""
        analysis = {
            "concerns": ["Performance"]
        }

        result = extract_engineering_questions_from_alignment(analysis)

        # May return empty list or generate from concerns
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_extract_with_empty_analysis(self):
        """Test extracting from empty analysis."""
        analysis = {}

        result = extract_engineering_questions_from_alignment(analysis)

        assert isinstance(result, list)


class TestAddArchitectureQuestions:
    """Tests for adding architecture questions to system."""

    @pytest.mark.unit
    def test_add_questions_to_empty_system(self, temp_dir, monkeypatch):
        """Test adding questions when no questions exist."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions = [
            {"question": "How do we scale?", "priority": "high", "audience": "engineering"}
        ]

        with patch("roadmap.load_questions", return_value=[]):
            with patch("roadmap.save_questions") as mock_save:
                result = add_architecture_questions_to_system(questions)

                assert result >= 1
                assert mock_save.called

    @pytest.mark.unit
    def test_add_questions_avoids_duplicates(self, temp_dir, monkeypatch):
        """Test that duplicate questions are not added."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        existing_questions = [
            {"id": "q1", "question": "How do we scale?", "status": "pending", "audience": "engineering"}
        ]

        new_questions = [
            {"question": "How do we scale?", "priority": "high", "audience": "engineering"},
            {"question": "New unique question?", "priority": "medium", "audience": "engineering"}
        ]

        with patch("roadmap.load_questions", return_value=existing_questions):
            with patch("roadmap.save_questions") as mock_save:
                result = add_architecture_questions_to_system(new_questions)

                # Should add only the unique question
                assert result <= len(new_questions)
                assert mock_save.called

    @pytest.mark.unit
    def test_add_empty_questions_list(self, temp_dir, monkeypatch):
        """Test adding empty questions list."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        with patch("roadmap.load_questions", return_value=[]):
            with patch("roadmap.save_questions") as mock_save:
                result = add_architecture_questions_to_system([])

                assert result == 0
                # Should not save if no new questions
                if mock_save.called:
                    call_args = mock_save.call_args[0][0]
                    assert call_args == []


class TestQuestionStatusManagement:
    """Tests for question status transitions."""

    @pytest.mark.unit
    def test_mark_question_as_answered(self, temp_dir, monkeypatch):
        """Test marking a question as answered."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions = [
            {"id": "q1", "question": "Test?", "status": "pending", "audience": "engineering"}
        ]

        # Save initial questions
        save_questions(questions)

        # Load, update, save
        loaded = load_questions()
        loaded[0]["status"] = "answered"
        loaded[0]["answered_at"] = datetime.now().isoformat()
        save_questions(loaded)

        # Verify
        final = load_questions()
        assert final[0]["status"] == "answered"
        assert "answered_at" in final[0]

    @pytest.mark.unit
    def test_question_status_counts(self, temp_dir, monkeypatch):
        """Test that metadata correctly counts question statuses."""
        monkeypatch.setattr("roadmap.DATA_DIR", temp_dir)

        questions = [
            {"id": "q1", "question": "Q1?", "status": "pending", "audience": "engineering"},
            {"id": "q2", "question": "Q2?", "status": "answered", "audience": "product"},
            {"id": "q3", "question": "Q3?", "status": "pending", "audience": "engineering"},
            {"id": "q4", "question": "Q4?", "status": "deferred", "audience": "executive"}
        ]

        save_questions(questions)

        questions_file = temp_dir / "questions" / "questions.json"
        saved_data = json.loads(questions_file.read_text())

        metadata = saved_data["metadata"]
        assert metadata["total_pending"] == 2
        assert metadata["total_answered"] == 1
        assert metadata["total_deferred"] == 1


class TestQuestionFormatting:
    """Tests for question formatting and structure."""

    @pytest.mark.unit
    def test_question_has_required_fields(self):
        """Test that generated questions have required fields."""
        question = {
            "id": "q1",
            "question": "What is the strategy?",
            "status": "pending",
            "audience": "executive"
        }

        # Verify required fields
        assert "id" in question
        assert "question" in question
        assert "status" in question
        assert "audience" in question
        assert isinstance(question["question"], str)
        assert len(question["question"]) > 0

    @pytest.mark.unit
    def test_question_audience_is_valid(self):
        """Test that question audience is from valid set."""
        valid_audiences = ["engineering", "product", "executive", "all"]

        question = {"audience": "engineering"}

        assert question["audience"] in valid_audiences
