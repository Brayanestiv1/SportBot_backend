import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

# Crear cliente de prueba
client = TestClient(app)

class TestAPIEndpoints:
    """Pruebas unitarias y de integración para los endpoints de la API"""

    @patch("app.services.agent.AgentService.process_query", new_callable=AsyncMock)
    def test_chat_endpoint_valid_message(self, mock_agent):
        """Prueba el endpoint POST /chats/message con mensaje válido"""
        # Configurar mock del agente
        mock_agent.return_value = {
            "reply": "Hola! Soy BaekhoBot, tu especialista en productos de Taekwondo.",
            "sources": [],
            "relevance_score": 0.95,
            "context_used": []
        }

        # Datos de prueba
        test_message = {"message": "Hola, ¿cómo estás?"}

        # Realizar solicitud POST al endpoint de chat
        response = client.post("/api/v1/chats/message", json=test_message)

        # Verificar código de estado
        assert response.status_code == 200

        # Verificar estructura de respuesta
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "data" in data
        assert "reply" in data["data"]

        # Verificar que el agente fue llamado
        mock_agent.assert_called_once()

    @patch("app.services.agent.AgentService.process_query", new_callable=AsyncMock)
    def test_chat_endpoint_empty_message(self, mock_agent):
        """Prueba el endpoint POST /chats/message con mensaje vacío"""
        test_message = {"message": ""}
        response = client.post("/api/v1/chats/message", json=test_message)

        # Debe fallar la validación pydantic → 422
        assert response.status_code == 422

    @patch("app.services.agent.AgentService.process_query", new_callable=AsyncMock)
    def test_chat_endpoint_missing_message(self, mock_agent):
        """Prueba el endpoint POST /chats/message sin campo message"""
        test_message = {"user_id": 1}
        response = client.post("/api/v1/chats/message", json=test_message)

        # Validación Pydantic → 422
        assert response.status_code == 422

    @patch("app.services.agent.AgentService.process_query", new_callable=AsyncMock)
    def test_chat_endpoint_with_user_id(self, mock_agent):
        """Prueba el endpoint POST /chats/message con user_id"""
        mock_agent.return_value = {
            "reply": "Respuesta personalizada para el usuario.",
            "sources": [],
            "relevance_score": 0.9,
            "context_used": []
        }

        test_message = {"message": "Hola, necesito ayuda", "user_id": 123, "context_limit": 5}
        response = client.post("/api/v1/chats/message", json=test_message)

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data["data"]

    def test_admin_chats_endpoint(self):
        """Prueba el endpoint GET /admin/chats (debe retornar 404 si no está implementado)"""
        # Realizar solicitud GET al endpoint de admin chats
        response = client.get("/admin/chats")
        
        # Verificar que retorna 404 (Not Found) ya que no está implementado
        assert response.status_code == 404

    def test_admin_chat_by_id_endpoint(self):
        """Prueba el endpoint GET /admin/chats/{id} (debe retornar 404 si no está implementado)"""
        # Realizar solicitud GET al endpoint de admin chat específico
        response = client.get("/admin/chats/1")
        
        # Verificar que retorna 404 (Not Found) ya que no está implementado
        assert response.status_code == 404
