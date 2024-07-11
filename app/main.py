from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sounddevice as sd
import numpy as np
import librosa
import joblib
import uvicorn
import threading
import asyncio
import logging
from typing import List

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

duration = 2
sample_rate = 16000

is_detecting = False
detection_thread = None

model = joblib.load('app/models/xgb_test.pkl')

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def extract_features(audio):
    sr = 16000

    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfccs = np.mean(mfccs, axis=1)

    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    chroma = np.mean(chroma, axis=1)

    contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    contrast = np.mean(contrast, axis=1)

    centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    centroid = np.mean(centroid, axis=1)

    combined_features = np.hstack([mfccs, chroma, contrast, centroid])
    return combined_features

async def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    audio_data = indata[:, 0]
    print(f"Audio data: {audio_data[:10]}... (length: {len(audio_data)})")
    logging.info(f"Audio data: {audio_data[:10]}... (length: {len(audio_data)})")
    
    features = extract_features(audio_data)
    features = features.reshape(1, -1)
    prediction = model.predict(features)
    is_fake = prediction[0]

    print(f"Prediction: {is_fake}")
    logging.info(f"Prediction: {is_fake}")

    result = 'fake' if is_fake else 'real'
    
    print(f"Detected {result} audio")
    logging.info(f"Detected {result} audio")

    await manager.send_message(result)

def detect_fake_audio():
    global is_detecting
    try:
        with sd.InputStream(callback=lambda indata, frames, time, status: asyncio.run(audio_callback(indata, frames, time, status)), channels=1, samplerate=sample_rate, blocksize=int(sample_rate * duration)):
            print("Listening...")
            logging.info("Listening...")
            while is_detecting:
                sd.sleep(duration * 1000)
    except Exception as e:
        print(f"Exception: {str(e)}")
        logging.info(f"Exception: {str(e)}")

@app.post("/start_detection")
async def start_detection():
    global is_detecting, detection_thread

    if not is_detecting:
        is_detecting = True
        detection_thread = threading.Thread(target=detect_fake_audio)
        detection_thread.start()
    return JSONResponse(content={'status': 'detection_started'})

@app.post("/stop_detection")
async def stop_detection():
    global is_detecting, detection_thread
    is_detecting = False
    if detection_thread:
        detection_thread.join()
    return JSONResponse(content={'status': 'detection_stopped'})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

