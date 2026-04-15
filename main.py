from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
import os
import uuid
import httpx
import asyncio
from typing import List

app = FastAPI(title="Medical Image Analysis Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory=OUTPUT_DIR), name="images")


# ===============================
# 🔧 PREPROCESS
# ===============================
def preprocess(image_bytes: bytes) -> np.ndarray:
    file_bytes = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image invalide ou non lisible")
    img = cv2.resize(img, (256, 256))
    return img


async def fetch_image(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


def compare_two(image1: np.ndarray, image2: np.ndarray) -> dict:
    diff = cv2.absdiff(image1, image2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    change_pixels = int(np.sum(thresh > 0))
    total_pixels = thresh.size
    variation = round((change_pixels / total_pixels) * 100, 2)

    if variation > 15:
        evolution = "AGGRAVATION"
    elif variation > 5:
        evolution = "MODIFICATION"
    else:
        evolution = "STABLE"

    heatmap_color = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(
        cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR), 0.7,
        heatmap_color, 0.3, 0
    )
    filename = f"heatmap_{uuid.uuid4().hex}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(filepath, overlay)

    return {
        "evolution": evolution,
        "variation": variation,
        "heatmap": f"http://localhost:8000/images/{filename}"
    }


# ===============================
# 📦 Modèles requête
# ===============================
class MultiCompareRequest(BaseModel):
    img_urls: List[str]


# ===============================
# 🚀 API MULTI-IMAGES (N images)
# ===============================
@app.post("/compare-evolution-multi")
async def compare_multi(req: MultiCompareRequest):
    """
    Compare N images successives (2, 3, 4... images).
    Retourne une liste de comparaisons entre chaque paire consécutive.
    """
    urls = req.img_urls
    if len(urls) < 2:
        return {"error": "Au moins 2 images requises", "comparaisons": []}

    # Télécharger toutes les images en parallèle
    try:
        raw_images = await asyncio.gather(*[fetch_image(url) for url in urls])
    except Exception as e:
        return {"error": f"Erreur téléchargement: {str(e)}", "comparaisons": []}

    # Prétraitement
    processed: List[np.ndarray] = []
    for i, raw in enumerate(raw_images):
        try:
            processed.append(preprocess(raw))
        except Exception as e:
            return {"error": f"Image {i+1} invalide: {str(e)}", "comparaisons": []}

    # Comparaisons successives (N-1 paires)
    comparaisons = []
    for i in range(len(processed) - 1):
        result = compare_two(processed[i], processed[i + 1])
        result["from_index"] = i
        result["to_index"] = i + 1
        result["from_url"] = urls[i]
        result["to_url"] = urls[i + 1]
        comparaisons.append(result)

    # Résumé global
    variations = [c["variation"] for c in comparaisons]
    evolutions = [c["evolution"] for c in comparaisons]

    if "AGGRAVATION" in evolutions:
        global_evolution = "AGGRAVATION"
    elif "MODIFICATION" in evolutions:
        global_evolution = "MODIFICATION"
    else:
        global_evolution = "STABLE"

    return {
        "total_comparaisons": len(comparaisons),
        "global_evolution": global_evolution,
        "variation_moyenne": round(sum(variations) / len(variations), 2),
        "variation_max": round(max(variations), 2),
        "comparaisons": comparaisons
    }


# ===============================
# 🔁 Ancien endpoint (rétrocompat)
# ===============================
@app.post("/compare-evolution")
async def compare_legacy(img1: UploadFile, img2: UploadFile):
    image1 = preprocess(await img1.read())
    image2 = preprocess(await img2.read())
    return compare_two(image1, image2)


# ===============================
# ❤️ Health check
# ===============================
@app.get("/health")
def health():
    return {"status": "ok"}