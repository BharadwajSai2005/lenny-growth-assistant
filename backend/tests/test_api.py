"""Tests for the FastAPI endpoints."""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Set env vars before importing app
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/lenny"
os.environ["LLM_PROVIDER"] = "local"

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "llm_provider" in data
        assert "database" in data

    def test_health_shows_provider(self):
        response = client.get("/health")
        data = response.json()
        assert data["llm_provider"] in ["local", "cloud"]


class TestConfigEndpoint:
    def test_config_returns_provider(self):
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "llm_provider" in data
        assert "model" in data
        assert "ollama_base_url" in data

    @patch.dict(os.environ, {"LLM_PROVIDER": "cloud"})
    def test_config_cloud_provider(self):
        response = client.get("/config")
        data = response.json()
        assert data["model"] == "claude-3-haiku-20240307"

    @patch.dict(os.environ, {"LLM_PROVIDER": "local", "OLLAMA_MODEL": "phi3"})
    def test_config_local_provider(self):
        response = client.get("/config")
        data = response.json()
        assert data["llm_provider"] == "local"


class TestChatEndpoint:
    @patch("main.generate_response")
    def test_chat_creates_session(self, mock_gen):
        mock_gen.return_value = ("Test reply", ["source.md"], "qa")
        response = client.post("/chat", json={"message": "What is PMF?"})
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["reply"] == "Test reply"
        assert data["sources"] == ["source.md"]
        assert data["skill_used"] == "qa"

    @patch("main.generate_response")
    def test_chat_with_session_id(self, mock_gen):
        mock_gen.return_value = ("Reply 2", [], "qa")
        # First create a session
        response1 = client.post("/chat", json={"message": "Hello"})
        if response1.status_code == 200:
            sid = response1.json()["session_id"]
            response2 = client.post("/chat", json={"session_id": sid, "message": "Follow up"})
            assert response2.status_code == 200
            assert response2.json()["session_id"] == sid

    def test_chat_missing_message(self):
        response = client.post("/chat", json={})
        assert response.status_code == 422  # Validation error

    @patch("main.generate_response")
    def test_chat_ship30_skill(self, mock_gen):
        mock_gen.return_value = ("```markdown\n# Essay\n```", ["source.md"], "ship30")
        response = client.post("/chat", json={"message": "Write a Ship 30 essay about growth"})
        assert response.status_code == 200
        data = response.json()
        assert data["skill_used"] == "ship30"


class TestSessionsEndpoint:
    def test_create_session(self):
        response = client.post("/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
