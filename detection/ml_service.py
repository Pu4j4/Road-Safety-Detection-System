import os
import numpy as np
import cv2
import time
import logging
from PIL import Image, ImageDraw
from skimage.transform import resize as sk_resize

logger = logging.getLogger(__name__)

_lane_model    = None
_pothole_model = None

MODEL_INPUT_SIZE = (160, 80)
ORIGINAL_SIZE    = (1280, 720)


class LaneState:
    def __init__(self):
        self.recent_fit = []
        self.avg_fit    = []

_lane_state = LaneState()


def _load_onnx_model(model_path, name):
    """Load any ONNX model using onnxruntime."""
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        logger.info(f"✅ {name} ONNX model loaded.")
        return session
    except Exception as e:
        logger.error(f"❌ {name} ONNX model failed: {e}")
        return None


def load_models():
    global _lane_model, _pothole_model
    from django.conf import settings
    _lane_model    = _load_onnx_model(str(settings.LANE_MODEL_PATH),    'Lane')
    _pothole_model = _load_onnx_model(str(settings.POTHOLE_MODEL_PATH), 'Pothole')


def get_lane_model():
    global _lane_model
    if _lane_model is None:
        from django.conf import settings
        _lane_model = _load_onnx_model(str(settings.LANE_MODEL_PATH), 'Lane')
    return _lane_model


def get_pothole_model():
    global _pothole_model
    if _pothole_model is None:
        from django.conf import settings
        _pothole_model = _load_onnx_model(str(settings.POTHOLE_MODEL_PATH), 'Pothole')
    return _pothole_model


# ── Lane Detection ────────────────────────────────────────────────

def _process_lane_frame(frame):
    session = get_lane_model()
    if session is None:
        raise RuntimeError("Lane model not loaded.")

    small = sk_resize(
        frame, (MODEL_INPUT_SIZE[1], MODEL_INPUT_SIZE[0], 3),
        preserve_range=True, anti_aliasing=True
    ).astype(np.float32)
    small = small[None, :, :, :]

    input_name = session.get_inputs()[0].name
    prediction = session.run(None, {input_name: small})[0][0] * 255

    _lane_state.recent_fit.append(prediction)
    if len(_lane_state.recent_fit) > 5:
        _lane_state.recent_fit = _lane_state.recent_fit[1:]

    _lane_state.avg_fit = np.mean(np.array(_lane_state.recent_fit), axis=0)
    blanks     = np.zeros_like(_lane_state.avg_fit).astype(np.uint8)
    lane_drawn = np.dstack((blanks, _lane_state.avg_fit.astype(np.uint8), blanks))
    lane_image = sk_resize(
        lane_drawn, frame.shape,
        preserve_range=True, anti_aliasing=True
    ).astype(np.uint8)
    return cv2.addWeighted(frame, 1, lane_image, 1, 0)


def detect_lanes_video(input_path, output_path):
    _lane_state.recent_fit = []
    _lane_state.avg_fit    = []

    start  = time.time()
    cap    = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")

    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_path, fourcc, fps, ORIGINAL_SIZE)

    processed = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame  = cv2.resize(frame, ORIGINAL_SIZE)
            result = _process_lane_frame(frame)
            out.write(result)
            processed += 1
    finally:
        cap.release()
        out.release()

    return {
        'frames_processed':   processed,
        'total_frames':       total,
        'processing_time_ms': (time.time() - start) * 1000,
        'fps':                fps,
    }


# ── Pothole Detection ─────────────────────────────────────────────

def _run_pothole_onnx(session, img_pil):
    """Run ONNX pothole model on a PIL image, return boxes and scores."""
    orig_w, orig_h = img_pil.size

    # Resize to model input size
    img_resized = img_pil.resize((640, 640))
    img_array   = np.array(img_resized).astype(np.float32) / 255.0
    img_array   = img_array.transpose(2, 0, 1)[None, :, :, :]  # NCHW

    input_name = session.get_inputs()[0].name
    outputs    = session.run(None, {input_name: img_array})[0]  # shape: (1, 5, 8400)

    # Parse YOLO output
    predictions = outputs[0].T  # (8400, 5) → x,y,w,h,conf
    boxes, scores = [], []

    for pred in predictions:
        x, y, w, h = pred[:4]
        conf        = float(pred[4])
        if conf < 0.25:
            continue
        # Convert from 640x640 back to original size
        x1 = int((x - w / 2) * orig_w / 640)
        y1 = int((y - h / 2) * orig_h / 640)
        x2 = int((x + w / 2) * orig_w / 640)
        y2 = int((y + h / 2) * orig_h / 640)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(orig_w, x2), min(orig_h, y2)
        boxes.append([x1, y1, x2, y2])
        scores.append(round(conf, 3))

    return boxes, scores


def detect_potholes_image(input_path, output_path):
    session = get_pothole_model()
    if session is None:
        raise RuntimeError("Pothole model not loaded.")

    start  = time.time()
    img    = Image.open(input_path).convert("RGB")
    boxes, scores = _run_pothole_onnx(session, img)

    draw = ImageDraw.Draw(img)
    detections = []
    for i, (box, score) in enumerate(zip(boxes, scores)):
        x1, y1, x2, y2 = box
        draw.rectangle((x1, y1, x2, y2), outline="red", width=3)
        detections.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'confidence': score})
    img.save(output_path)

    return {
        'pothole_count':      len(boxes),
        'pothole_detected':   len(boxes) > 0,
        'detections':         detections,
        'processing_time_ms': (time.time() - start) * 1000,
    }


def detect_potholes_video(input_path, output_path):
    session = get_pothole_model()
    if session is None:
        raise RuntimeError("Pothole model not loaded.")

    start  = time.time()
    cap    = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")

    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w      = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    total_potholes = 0
    pothole_found  = False
    processed      = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            img_pil       = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            boxes, scores = _run_pothole_onnx(session, img_pil)
            draw          = ImageDraw.Draw(img_pil)
            for box in boxes:
                x1, y1, x2, y2 = box
                draw.rectangle((x1, y1, x2, y2), outline="red", width=3)
            if boxes:
                pothole_found   = True
                total_potholes += len(boxes)
            out.write(cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR))
            processed += 1
    finally:
        cap.release()
        out.release()

    return {
        'pothole_count':      total_potholes,
        'pothole_detected':   pothole_found,
        'frames_processed':   processed,
        'processing_time_ms': (time.time() - start) * 1000,
    }
