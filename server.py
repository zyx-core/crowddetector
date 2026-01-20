import os
import cv2
import time
import shutil
import numpy as np
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import load_config
from hybrid_engine import HybridEngine
from utils import draw_text_with_background

# Initialize App
app = FastAPI(title="Crowd Detection System API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (Frontend)
os.makedirs("web", exist_ok=True)
app.mount("/static", StaticFiles(directory="web"), name="static")

# Global State
class SystemState:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.engine = HybridEngine("config.yaml")
        self.camera = None
        self.is_running = False
        self.latest_stats = {"count": 0, "fps": 0, "mode": "Initializing"}

state = SystemState()

def get_video_stream():
    """Generator for video stream with hybrid visualization."""
    while True:
        if not state.is_running or state.camera is None:
            time.sleep(0.1)
            continue
            
        success, frame = state.camera.read()
        if not success:
            state.camera.release()
            state.camera = None
            state.is_running = False
            break
            
        # Process Frame via Hybrid Engine
        start_time = time.time()
        result = state.engine.process_frame(frame)
        inference_time = time.time() - start_time
        fps = 1.0 / inference_time if inference_time > 0 else 30.0
        
        # Visualization
        vis_frame = frame.copy()
        mode = result['mode']
        detections = result['detections']
        heatmap = result.get('heatmap')
        count_data = result.get('counts', {})
        
        # Mode 1: Draw Boxes + Tripwire
        if mode == HybridEngine.MODE_1:
            # Draw Tripwire
            line = count_data.get('line')
            if line:
                cv2.line(vis_frame, line[0], line[1], (255, 0, 0), 2)
                
            for det in detections:
                bbox = det['bbox']
                x1, y1, x2, y2 = map(int, bbox)
                
                # Color based on tracking ID or default green
                color = (0, 255, 0)
                if 'id' in det:
                    color = (0, 255, 255) # Yellow for tracked
                
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
                
            # Draw IN/OUT
            in_c = count_data.get('in_count', 0)
            out_c = count_data.get('out_count', 0)
            draw_text_with_background(vis_frame, f"IN: {in_c}", 20, 100, text_color=(0, 255, 0))
            draw_text_with_background(vis_frame, f"OUT: {out_c}", 20, 130, text_color=(0, 0, 255))
                
        # Mode 2: Draw Heatmap Overlay + Optical Flow
        elif mode == HybridEngine.MODE_2 and heatmap is not None:
             # Blend heatmap
             vis_frame = cv2.addWeighted(vis_frame, 0.6, heatmap, 0.4, 0)
             draw_text_with_background(vis_frame, "SURGE MODE", 20, 100, text_color=(0,0,255), bg_color=(0,0,0))
             
             # Visualize Flow
             flow = result.get('flow')
             if flow:
                 direction = flow['direction']
                 mag = flow['magnitude']
                 draw_text_with_background(vis_frame, f"FLOW: {direction}", 20, 130, text_color=(255,165,0))
                 
                 # Draw Arrow for Flow
                 if mag > 0.5:
                     center_x, center_y = vis_frame.shape[1]//2, vis_frame.shape[0]//2
                     end_x = int(center_x + flow['dx'] * 50)
                     end_y = int(center_y + flow['dy'] * 50)
                     cv2.arrowedLine(vis_frame, (center_x, center_y), (end_x, end_y), (255, 165, 0), 3)

        # HUD
        draw_text_with_background(vis_frame, f"Mode: {mode}", 20, 40, text_color=(255, 255, 255), bg_color=(0, 0, 0))
        draw_text_with_background(vis_frame, f"Count: {result['count']}", 20, 70)
        draw_text_with_background(vis_frame, f"FPS: {int(fps)}", vis_frame.shape[1] - 100, 40)
        
        # Update Global Stats
        state.latest_stats = {
            "count": result['count'],
            "fps": int(fps),
            "mode": mode
        }

        ret, buffer = cv2.imencode('.jpg', vis_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/")
async def index():
    try:
        with open("web/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return HTMLResponse(content=f"<h1>Error loading page: {e}</h1>", status_code=500)

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(get_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
async def get_stats():
    stats = state.latest_stats.copy()
    # Add IN/OUT counts if available
    if state.engine.counter:
        stats["in_count"] = state.engine.counter.in_count
        stats["out_count"] = state.engine.counter.out_count
    return JSONResponse(stats)

@app.post("/start_webcam")
async def start_webcam():
    if state.camera is not None:
        state.camera.release()
    
    state.camera = cv2.VideoCapture(0)
    state.source_type = 'webcam'
    state.is_running = True
    state.is_running = True
    # state.counter.reset() # Legacy, removed
    return {"status": "Webcam started"}

@app.post("/stop")
async def stop_stream():
    state.is_running = False
    if state.camera is not None:
        state.camera.release()
        state.camera = None
    return {"status": "Stopped"}

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if state.camera is not None:
        state.camera.release()
        
    state.camera = cv2.VideoCapture(temp_file)
    state.source_type = 'video'
    state.is_running = True
    state.is_running = True
    # state.counter.reset()
    
    return {"status": "Video uploaded and started"}


        
from pydantic import BaseModel

class ToggleModeRequest(BaseModel):
    mode: str

class LineUpdateRequest(BaseModel):
    line: list # [[x1, y1], [x2, y2]]

@app.post("/toggle_mode")
async def toggle_mode(data: ToggleModeRequest):
    mode = data.mode
    if mode:
        state.engine.set_manual_mode(mode)
        return {"status": "success", "mode": mode}
    return JSONResponse(status_code=400, content={"message": "Mode required"})

@app.post("/update_line")
async def update_line(data: LineUpdateRequest):
    line = data.line
    if line and len(line) == 2:
        # Convert to list of tuples
        line_coords = [(int(line[0][0]), int(line[0][1])), (int(line[1][0]), int(line[1][1]))]
        state.engine.update_tripwire(line_coords)
        return {"status": "success", "line": line_coords}
    return JSONResponse(status_code=400, content={"message": "Invalid line data"})

@app.get("/export_csv")
async def export_csv():
    """
    Exports the current session data (IN/OUT counts) to a CSV file.
    """
    import csv
    import io
    from datetime import datetime
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Timestamp', 'Metric', 'Value'])
    
    # Data (Current Snapshot)
    now = datetime.now().isoformat()
    if state.engine.counter:
        writer.writerow([now, 'IN_COUNT', state.engine.counter.in_count])
        writer.writerow([now, 'OUT_COUNT', state.engine.counter.out_count])
        writer.writerow([now, 'TOTAL_COUNT', state.engine.counter.total_count])
    
    output.seek(0)
    
    # Create response
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=crowd_data.csv"
    return response

@app.post("/detect_image")
async def detect_image(file: UploadFile = File(...)):
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Fallback for formats OpenCV doesn't support (like AVIF/WEBP)
        if image is None:
            try:
                from PIL import Image
                import io
                pil_image = Image.open(io.BytesIO(contents))
                # Convert PIL (RGB) to OpenCV (BGR)
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"PIL decoding failed: {e}")
        
        if image is None:
            return JSONResponse(status_code=400, content={"message": "Could not decode image. Please use JPG or PNG."})
        
        # Process via Engine
        result = state.engine.process_frame(image)
        mode = result['mode']
        print(f"DEBUG: Detect Image -> Mode: {mode} (Override: {state.engine.manual_override})")
        
        detections = result['detections']
        heatmap = result.get('heatmap')
        
        # Visualization
        if mode == HybridEngine.MODE_1:
            for det in detections:
                bbox = det['bbox']
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        elif mode == HybridEngine.MODE_2 and heatmap is not None:
             image = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)
        
        # HUD
        draw_text_with_background(image, f"Mode: {mode}", 20, 40)
        draw_text_with_background(image, f"Count: {result['count']}", 20, 70)

        # Encode response
        ret, buffer = cv2.imencode('.jpg', image)
        if not ret:
             return JSONResponse(status_code=500, content={"message": "Could not encode result image"})
             
        import base64
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "count": result['count'],
            "image": f"data:image/jpeg;base64,{img_str}",
            "mode": mode
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
