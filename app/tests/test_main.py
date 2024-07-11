import pytest
from httpx import AsyncClient
import numpy as np
from unittest.mock import patch
from app.main import app, extract_features

@pytest.mark.asyncio
async def test_start_detection():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/start_detection")
    assert response.status_code == 200
    assert response.json() == {"status": "detection_started"}

@pytest.mark.asyncio
async def test_stop_detection():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/stop_detection")
    assert response.status_code == 200
    assert response.json() == {"status": "detection_stopped"}

def test_extract_features():
    dummy_audio = np.random.randn(16000)
    features = extract_features(dummy_audio)
    assert features.shape == (33,)

# @patch("app.main.sd.InputStream")
# def test_audio_callback(mock_input_stream):
#     from app.main import audio_callback

#     dummy_data = np.random.randn(8000, 1)
#     mock_input_stream.return_value.read.return_value = dummy_data, 0

#     indata = dummy_data
#     frames = 8000
#     time = None
#     status = None

#     audio_callback(indata, frames, time, status)