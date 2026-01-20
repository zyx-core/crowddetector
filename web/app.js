const API_URL = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId, btn);
        });
    });
});

function switchTab(tabId, activeBtn) {
    // Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    activeBtn.classList.add('active');

    // Content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabId}-tab`).classList.add('active');

    // Reset View
    stopStream();
}

// Stats Polling
let statsInterval = null;

function startStatsPolling() {
    if (statsInterval) clearInterval(statsInterval);
    statsInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/stats`);
            const data = await res.json();
            updateStats(data.count);
        } catch (e) {
            console.error(e);
        }
    }, 500);
}

function updateStats(count) {
    document.getElementById('count-value').innerText = count;

    const densityEl = document.getElementById('density-value');
    if (count < 10) {
        densityEl.innerText = "Low";
        densityEl.style.color = "#22c55e";
    } else if (count < 20) {
        densityEl.innerText = "Medium";
        densityEl.style.color = "#eab308";
    } else {
        densityEl.innerText = "High";
        densityEl.style.color = "#ef4444";
    }
}

// Mode Switching
document.getElementById('mode-select').addEventListener('change', async (e) => {
    const selectedMode = e.target.value;
    console.log(`Switching mode to: ${selectedMode}`);

    try {
        const response = await fetch(`${API_URL}/toggle_mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: selectedMode })
        });
        const result = await response.json();

        if (!response.ok) {
            console.error("Failed to switch mode:", result);
            alert("Failed to switch mode. Check console.");
        }
    } catch (e) {
        console.error("Error switching mode:", e);
        alert("Error connecting to server.");
    }
});


// Stop Everything
async function stopStream() {
    await fetch(`${API_URL}/stop`, { method: 'POST' });
    document.getElementById('video-stream').style.display = 'none';
    document.getElementById('result-display').style.display = 'none';
    document.getElementById('placeholder-view').style.display = 'block';
    if (statsInterval) clearInterval(statsInterval);
}

// Webcam
async function startWebcam() {
    await stopStream();
    const res = await fetch(`${API_URL}/start_webcam`, { method: 'POST' });
    if (res.ok) {
        showVideoFeed();
    }
}

// Video Upload
const videoDropZone = document.getElementById('video-drop-zone');
const videoInput = document.getElementById('video-input');

videoDropZone.addEventListener('click', () => videoInput.click());

videoInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        await stopStream();
        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        videoDropZone.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><p>Uploading...</p>';

        const res = await fetch(`${API_URL}/upload_video`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            videoDropZone.innerHTML = '<i class="fa-solid fa-film"></i><p>Drag & Drop or Click to Upload Video</p>';
            showVideoFeed();
        }
    }
});

function showVideoFeed() {
    const imgStream = document.getElementById('video-stream');
    imgStream.src = `${API_URL}/video_feed?t=${new Date().getTime()}`;
    imgStream.style.display = 'block';
    document.getElementById('placeholder-view').style.display = 'none';
    startStatsPolling();
}

// Image Upload
const imageDropZone = document.getElementById('image-drop-zone');
const imageInput = document.getElementById('image-input');

imageDropZone.addEventListener('click', () => imageInput.click());

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        await stopStream();
        const formData = new FormData();
        formData.append('file', file);

        imageDropZone.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i><p>Processing...</p>';

        const res = await fetch(`${API_URL}/detect_image`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            const resultImg = document.getElementById('result-display');
            resultImg.src = data.image;
            resultImg.style.display = 'block';
            document.getElementById('placeholder-view').style.display = 'none';
            updateStats(data.count);

            imageDropZone.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i><p>Drag & Drop or Click to Upload Image</p>';
        } else {
            const err = await res.json();
            alert(`Error: ${err.message || 'Upload failed'}`);
            imageDropZone.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i><p>Drag & Drop or Click to Upload Image</p>';
        }
    }
});

// --- Tripwire Editor ---
const canvas = document.getElementById('tripwire-canvas');
const ctx = canvas.getContext('2d');
let isEditing = false;
let isDragging = false;
let selectedHandle = -1; // 0 for start, 1 for end
let lineCoords = [{ x: 0, y: 0.6 }, { x: 1, y: 0.6 }]; // Normalized coordinates (0-1)

function initTripwireEditor() {
    const resizeCanvas = () => {
        const container = document.querySelector('.view-container');
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            drawTripwire();
        }
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    canvas.addEventListener('mousedown', (e) => {
        if (!isEditing) return;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const p1 = { x: lineCoords[0].x * canvas.width, y: lineCoords[0].y * canvas.height };
        const p2 = { x: lineCoords[1].x * canvas.width, y: lineCoords[1].y * canvas.height };

        if (dist(mouseX, mouseY, p1.x, p1.y) < 20) {
            isDragging = true;
            selectedHandle = 0;
        } else if (dist(mouseX, mouseY, p2.x, p2.y) < 20) {
            isDragging = true;
            selectedHandle = 1;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const rect = canvas.getBoundingClientRect();
        lineCoords[selectedHandle].x = Math.max(0, Math.min(1, (e.clientX - rect.left) / canvas.width));
        lineCoords[selectedHandle].y = Math.max(0, Math.min(1, (e.clientY - rect.top) / canvas.height));
        drawTripwire();
    });

    canvas.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            selectedHandle = -1;
            updateLineOnServer();
        }
    });
}

function dist(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

function drawTripwire() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!isEditing) return;

    const p1 = { x: lineCoords[0].x * canvas.width, y: lineCoords[0].y * canvas.height };
    const p2 = { x: lineCoords[1].x * canvas.width, y: lineCoords[1].y * canvas.height };

    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.fillStyle = '#ff00ff';
    ctx.beginPath();
    ctx.arc(p1.x, p1.y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(p2.x, p2.y, 8, 0, Math.PI * 2);
    ctx.fill();
}

async function updateLineOnServer() {
    const W = 640;
    const H = 480;
    const serverLine = [
        [lineCoords[0].x * W, lineCoords[0].y * H],
        [lineCoords[1].x * W, lineCoords[1].y * H]
    ];
    try {
        await fetch(`${API_URL}/update_line`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ line: serverLine })
        });
    } catch (e) {
        console.error("Failed to update tripwire", e);
    }
}

document.getElementById('edit-tripwire-btn').addEventListener('click', () => {
    isEditing = !isEditing;
    const btn = document.getElementById('edit-tripwire-btn');
    const cvs = document.getElementById('tripwire-canvas');

    if (isEditing) {
        btn.style.background = '#eab308';
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Done';
        cvs.style.pointerEvents = 'auto';
        drawTripwire();
    } else {
        btn.style.background = 'rgba(0,0,0,0.3)';
        btn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Line';
        cvs.style.pointerEvents = 'none';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
});

// CSV Export
document.getElementById('export-btn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/export_csv`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `crowd_data_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Export failed");
        }
    } catch (e) {
        console.error("Export error:", e);
        alert("Export error");
    }
});

initTripwireEditor();
