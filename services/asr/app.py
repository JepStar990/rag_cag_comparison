from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import os, tempfile, shutil

# Small default; change to "large-v3" if you have GPU
MODEL_SIZE = os.getenv("ASR_MODEL", "base")

model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
app = FastAPI(title="ASR Service")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    segments, info = model.transcribe(temp_path, beam_size=1)
    text = " ".join([seg.text for seg in segments])
    try:
        os.remove(temp_path)
    except Exception:
        pass
    return {"text": text, "language": info.language}
