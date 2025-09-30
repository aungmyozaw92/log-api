from unittest.mock import patch


def test_export_enqueue(client):
    with patch("app.api.logs.get_queue") as mock_get_queue:
        mock_q = mock_get_queue.return_value
        mock_job = mock_q.enqueue.return_value
        mock_job.get_id.return_value = "job-123"

        r = client.post("/api/v1/logs/export")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "job_id" in data["data"]

