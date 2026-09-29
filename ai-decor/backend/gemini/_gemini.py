"""
Room Assistant (FastAPI + Gemini Enhanced)
------------------------------------------
Multimodal conversational assistant using:
- YOLOv8 (Object Detection)
- CLIP-ViT (Image Embeddings)
- SBERT (Text Embeddings)
- Gemini for recommendations + trend analysis + image generation
- TTS (Groq / Whisper / Local)
"""

import os
import io
import time
import base64
import logging
import json
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import torch
from ultralytics import YOLO
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import pyttsx3
import google.generativeai as genai

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
OPENAI_API_KEY = ""
GEMINI_API_KEY = ""
GROQ_TTS_KEY = os.getenv("GROQ_TTS_KEY")
WHISPER_TTS_KEY = os.getenv("WHISPER_TTS_KEY")

PORT = int(os.getenv("PORT", 7860))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("room_assistant")

# ----------------------------
# Initialize models
# ----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

yolo_model = YOLO(os.getenv("YOLO_WEIGHTS", "yolov8n.pt"))
clip_model_name = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained(clip_model_name).to(device)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
sbert_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# ----------------------------
# Helper functions
# ----------------------------
def save_uploaded_file(file: UploadFile) -> str:
    fname = f"{int(time.time())}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, fname)
    with open(path, "wb") as f:
        f.write(file.file.read())
    logger.info(f"Saved uploaded file to {path}")
    return path


def read_image_pil(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def pil_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ----------------------------
# Detection
# ----------------------------
def detect_objects(image_path: str) -> List[Dict]:
    results = yolo_model(image_path, imgsz=1280)
    detections = []
    pil_img = read_image_pil(image_path)
    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue
        for b in boxes:
            coords = b.xyxy[0].cpu().numpy().tolist()
            conf = float(b.conf[0].cpu().numpy())
            cls = int(b.cls[0].cpu().numpy())
            label = yolo_model.model.names[cls]
            x1, y1, x2, y2 = map(int, coords)
            crop = pil_img.crop((x1, y1, x2, y2))
            crop_path = os.path.join(UPLOAD_FOLDER, f"crop_{int(time.time()*1000)}_{label}.jpg")
            crop.save(crop_path)
            detections.append({
                "label": label,
                "conf": conf,
                "box": [x1, y1, x2, y2],
                "crop_path": crop_path
            })
    return detections


# ----------------------------
# Embeddings
# ----------------------------
def embed_image_clip(pil_img: Image.Image) -> np.ndarray:
    inputs = clip_processor(images=pil_img, return_tensors="pt").to(device)
    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)
        emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
    return emb.cpu().numpy()[0]


# ----------------------------
# Heuristic Recommendations (Fallback)
# ----------------------------
def multimodal_recommendations(detections: List[Dict], image_embedding: np.ndarray, user_instruction: str) -> Dict:
    found_labels = [d["label"] for d in detections]
    recommendations = []

    if "chair" not in found_labels:
        recommendations.append({
            "object": "accent chair",
            "position": "near the window",
            "justification": "accent chairs in bold colors are trending for cozy corners",
            "reference_color": "deep teal",
            "trend_analysis": "Colorful accent seating is a 2025 trend emphasizing bold comfort."
        })
    if "plant" not in found_labels:
        recommendations.append({
            "object": "potted plant (Fiddle Leaf Fig)",
            "position": "left corner",
            "justification": "biophilic design trend adds freshness and calm",
            "reference_color": "green",
            "trend_analysis": "Indoor greenery continues to dominate minimalist spaces in 2025."
        })
    if "sofa" in found_labels:
        recommendations.append({
            "object": "throw blanket",
            "position": "on sofa arm",
            "justification": "layering textiles adds warmth and color",
            "reference_color": "mustard yellow",
            "trend_analysis": "Textured throws are trending for visual depth and coziness."
        })

    return {"recommendations": recommendations}


# ----------------------------
# Gemini-based Recommendations
# ----------------------------
def get_gemini_recommendations(detections: List[Dict], user_instruction: str = "") -> Dict:
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. Using heuristic fallback.")
        return multimodal_recommendations(detections, None, user_instruction)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        detected_labels = [d["label"] for d in detections]
        scene_summary = ", ".join(detected_labels)
        prompt = f"""
        You are an experienced interior design assistant.
        The room currently contains: {scene_summary}.
        Based on current home design trends in 2025, recommend 3 to 5 new items that will enhance the space.
        For each recommendation include:

        -"Room Color Analysis": give list of codes of colors used in the room and define a theme
        -"Room Lightening Analysis": give me an analysis of the current lightening of the room as well
        - "object": item name
        - "position": where to place it in the room
        - "reference_color": suggested color/material add the color codes
        - "justification": why it fits this space
        - "trend_analysis": why this item/trend is relevant in 2025 give reference on the basis of which trend analysis is done
        {f"User instruction: {user_instruction}" if user_instruction else ""}
        Respond **only** with a JSON list of objects, e.g.:
        [
          {{
            "object": "Painting",
            "position": "in the center of the room",
            "reference_color": "matte brass",
            "justification": "adds ambient light and complements the warm tones",
            "trend_analysis": "Warm metallics and ambient lighting are trending in 2025."
          }}
        ]
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("🔹 Sending recommendation prompt to Gemini-lite")
        response = model.generate_content(prompt)
        raw = getattr(response, "text", None)
        logger.info(f"🔸 Raw Gemini response: {raw!r}")

        if not raw and hasattr(response, "candidates"):
            try:
                raw = response.candidates[0].content.parts[0].text
                logger.info(f"🔸 Extracted from candidates: {raw!r}")
            except Exception:
                logger.warning("⚠️ No textual content in Gemini-candidates.")

        text_output = (raw or "").strip()
        if not text_output:
            logger.warning("⚠️ Gemini returned empty text — fallback.")
            return multimodal_recommendations(detections, None, user_instruction)

        # extract JSON array
        jstart = text_output.find("[")
        jend = text_output.rfind("]")
        if jstart != -1 and jend != -1:
            text_output = text_output[jstart:jend+1]

        try:
            recs = json.loads(text_output)
        except Exception as je:
            logger.error(f"❌ JSON parse failed: {je}")
            logger.debug(f"Raw content: {text_output}")
            return multimodal_recommendations(detections, None, user_instruction)

        if not isinstance(recs, list) or len(recs) == 0:
            logger.warning("⚠️ Parsed recommendations empty — fallback.")
            return multimodal_recommendations(detections, None, user_instruction)

        logger.info(f"✅ Gemini-lite recommendations parsed: {recs}")
        return {"recommendations": recs}

    except Exception as e:
        logger.error(f"❌ Gemini-lite request failed: {type(e).__name__}: {e}")
        return multimodal_recommendations(detections, None, user_instruction)

# ----------------------------
# Annotation + Visualization
# ----------------------------
def annotate_image(image_path: str, detections: List[Dict], recommendations: List[Dict]) -> str:
    im = read_image_pil(image_path).convert("RGBA")
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default()

    for d in detections:
        x1, y1, x2, y2 = d["box"]
        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 255), width=3)
        draw.text((x1 + 4, y1 + 4), f"{d['label']} {d['conf']:.2f}", fill=(255,255,255,255), font=font)

    w, h = im.size
    y_offset = 20
    for rec in recommendations:
        draw.text((w - 350, y_offset),
                  f"Add: {rec['object']} ({rec['position']})",
                  fill=(255,255,255,255), font=font)
        y_offset += 20

    outpath = os.path.join(OUTPUT_FOLDER, f"annotated_{int(time.time())}.png")
    im.save(outpath)
    return outpath


# ----------------------------
# Gemini Image Generation
# ----------------------------
def generate_final_room_image(original_path: str, recommendations: List[Dict]) -> str:
    if not GEMINI_API_KEY or not recommendations:
        logger.warning("No Gemini API key or no recommendations — returning original image.")
        outpath = os.path.join(OUTPUT_FOLDER, f"final_{int(time.time())}.png")
        read_image_pil(original_path).save(outpath)
        return outpath

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-image-lite")
        prompt = f"""
        Modify this room photo by adding the following décor items in a photorealistic manner:
        {json.dumps(recommendations, ensure_ascii=False, indent=2)}
        Ensure lighting, perspective, and existing furniture remain coherent.
        Return ONLY the final image (no extra text).
        """

        with open(original_path, "rb") as f:
            image_data = f.read()

        response = model.generate_content(
            [prompt, {"mime_type": "image/png", "data": image_data}],
            stream=False,
        )

        rawimg_b64 = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "image_bytes"):
                rawimg_b64 = candidate.image_bytes
            elif hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                rawimg_b64 = candidate.content.parts[0].inline_data.data

        if not rawimg_b64:
            raise ValueError("No image bytes in Gemini-image response")

        outpath = os.path.join(OUTPUT_FOLDER, f"final_{int(time.time())}.png")
        with open(outpath, "wb") as f:
            f.write(base64.b64decode(rawimg_b64))
        logger.info(f"✅ Generated final image via Gemini-image-lite: {outpath}")
        return outpath

    except Exception as e:
        logger.error(f"❌ Gemini-image-lite generation failed: {e}")
        outpath = os.path.join(OUTPUT_FOLDER, f"final_{int(time.time())}_fallback.png")
        read_image_pil(original_path).save(outpath)
        return outpath

    except Exception as e:
        logger.error(f"Gemini image generation failed: {e}")
        outpath = os.path.join(OUTPUT_FOLDER, f"final_{int(time.time())}_fallback.png")
        read_image_pil(original_path).save(outpath)
        return outpath

# ----------------------------
# TTS
# ----------------------------
def speak_text_local(text: str, out_path: Optional[str] = None):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    if out_path:
        engine.save_to_file(text, out_path)
        engine.runAndWait()
    else:
        engine.say(text)
        engine.runAndWait()


def tts_via_provider(text: str, outfile: str):
    if GROQ_TTS_KEY or WHISPER_TTS_KEY:
        logger.info("External TTS call placeholder")
    else:
        speak_text_local(text, outfile)


# ----------------------------
# FastAPI setup
# ----------------------------
app = FastAPI(title="Room Assistant (Gemini Enhanced)", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(
    image_file: UploadFile = File(...),
    instruction: Optional[str] = Form(""),
    produce_audio: Optional[str] = Form("false")
):
    produce_audio_flag = produce_audio.lower() == "true"

    saved_path = save_uploaded_file(image_file)
    detections = detect_objects(saved_path)
    pil_img = read_image_pil(saved_path)
    image_emb = embed_image_clip(pil_img)

    rec_output = get_gemini_recommendations(detections, instruction)
    recommendations = rec_output["recommendations"]

    annotated_path = annotate_image(saved_path, detections, recommendations)
    #final_image_path = generate_final_room_image(saved_path, recommendations)

    audio_path = None
    if produce_audio_flag:
        summary = (
            f"Recommended: {', '.join(r['object'] for r in recommendations)}."
        )
        audio_path = os.path.join(OUTPUT_FOLDER, f"summary_{int(time.time())}.mp3")
        tts_via_provider(summary, audio_path)
    logger.info(f"Recommendations: {[r['object'] for r in recommendations]}")
    return JSONResponse({
        "detections": detections,
        "recommendations": recommendations,
        "annotated_image_b64": annotated_path,
        #"final_image_b64": final_image_path,
        "audio_path": audio_path
    })


@app.get("/")
async def root():
    return {"message": "Room Assistant (Gemini Enhanced) is running. POST /analyze with image_file, instruction, produce_audio."}



