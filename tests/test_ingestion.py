from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["project"] == "FORGE"


def test_schedule_tasks_endpoint():
    response = client.get("/api/schedule/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) >= 20


def test_ingestion_upload_and_pipeline():
    response = client.post(
        "/api/ingestion/upload",
        data={
            "source": "web_upload",
            "media_type": "text",
            "raw_text": "Sector B Pier 14 concrete pouring completed",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "ingestion_id" in data
    assert data["status"] == "received_and_processing"


def test_review_tray_endpoint():
    response = client.get("/api/review/tray")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_chain_endpoint():
    response = client.get("/api/audit/chain")
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert "total" in data


def test_audit_verify_endpoint():
    response = client.get("/api/audit/verify")
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data


def test_twilio_messaging_webhook():
    response = client.post(
        "/api/webhooks/twilio/messaging",
        data={
            "From": "whatsapp:+919876543210",
            "Body": "Sector B Pier 14 concrete pouring done",
            "NumMedia": "0",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "whatsapp"
    assert "ingestion_id" in data


def test_ivr_twiml_endpoint():
    response = client.get("/api/webhooks/ivr/twiml")
    assert response.status_code == 200
    assert "Response" in response.text
    assert "Say" in response.text
    assert "Record" in response.text


def test_ivr_simulate_endpoint():
    response = client.post(
        "/api/webhooks/ivr/simulate",
        data={
            "spoken_text": "Zone A excavation completed",
            "caller_phone": "+919854012345",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "ivr"
    assert data["media_type"] == "voice"
    assert "ingestion_id" in data
