"""Tests for the agent skill routing and detection."""
import pytest
from unittest.mock import patch, MagicMock
from agent import detect_skill


class TestSkillDetection:
    def test_detect_ship30_essay(self):
        assert detect_skill("Write a Ship 30 for 30 essay about growth") == "ship30"

    def test_detect_ship30_keyword(self):
        assert detect_skill("Can you write a ship 30 essay?") == "ship30"

    def test_detect_essay_keyword(self):
        assert detect_skill("Write an essay about retention") == "ship30"

    def test_detect_30_for_30(self):
        assert detect_skill("Give me a 30 for 30 piece on pricing") == "ship30"

    def test_detect_qa_default(self):
        assert detect_skill("What is product-market fit?") == "qa"

    def test_detect_qa_growth_question(self):
        assert detect_skill("How do I improve retention?") == "qa"

    def test_detect_qa_metrics(self):
        assert detect_skill("What metrics should I track?") == "qa"

    def test_detect_case_insensitive(self):
        assert detect_skill("WRITE AN ESSAY about growth") == "ship30"
        assert detect_skill("Ship 30 FOR 30 style") == "ship30"


class TestGenerateResponse:
    @patch("agent.get_llm")
    @patch("agent.retrieve_context")
    def test_generate_response_returns_three_values(self, mock_retrieve, mock_llm):
        mock_retrieve.return_value = ("Some context", ["source.md"])
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="Test answer")
        mock_llm.return_value = mock_llm_instance

        from agent import generate_response
        reply, sources, skill = generate_response("What is PMF?", [])
        
        assert isinstance(reply, str)
        assert isinstance(sources, list)
        assert skill in ["qa", "ship30", "error"]

    @patch("agent.get_llm")
    @patch("agent.retrieve_context")
    def test_generate_response_routes_to_ship30(self, mock_retrieve, mock_llm):
        mock_retrieve.return_value = ("Context", ["source.md"])
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="```markdown\n# Essay\n```")
        mock_llm.return_value = mock_llm_instance

        from agent import generate_response
        reply, sources, skill = generate_response("Write a Ship 30 essay about growth", [])
        
        assert skill == "ship30"

    @patch("agent.get_llm")
    @patch("agent.retrieve_context")
    def test_generate_response_handles_llm_error(self, mock_retrieve, mock_llm):
        mock_retrieve.return_value = ("Context", ["source.md"])
        mock_llm.return_value = None  # LLM unavailable

        from agent import generate_response
        reply, sources, skill = generate_response("What is PMF?", [])
        
        assert isinstance(reply, str)  # Should return error message, not crash


class TestRetrieveContext:
    @patch("agent.SessionLocal")
    def test_retrieve_empty_results(self, mock_session_local):
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
        mock_session_local.return_value = mock_db

        from agent import retrieve_context
        context, sources = retrieve_context("nonexistent topic")
        
        assert isinstance(context, str)
        assert isinstance(sources, list)
