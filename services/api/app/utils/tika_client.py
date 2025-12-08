import os, requests

TIKA_URL = os.getenv("TIKA_URL", "http://tika:9998")

def extract_text_via_tika(content: bytes, filename: str) -> str:
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Accept": "text/plain"
    }
    r = requests.put(f"{TIKA_URL}/tika", data=content, headers=headers, timeout=None)
    r.raise_for_status()
    return r.text
