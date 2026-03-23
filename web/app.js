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
            updateStats(data);
        } catch (e) {
            console.error(e);
        }
    }, 500);
}

function updateStats(stats) {
    const count = stats.count || 0;
    const inRoom = stats.in_room_count || 0;
    
    document.getElementById('count-value').innerText = count;
    const inRoomEl = document.getElementById('in-room-value');
    if(inRoomEl) inRoomEl.innerText = inRoom;

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
            updateStats(data);

            imageDropZone.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i><p>Drag & Drop or Click to Upload Image</p>';
        } else {
            const err = await res.json();
            alert(`Error: ${err.message || 'Upload failed'}`);
            imageDropZone.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i><p>Drag & Drop or Click to Upload Image</p>';
        }
    }
});

// --- Zone Editor ---
const canvas = document.getElementById('tripwire-canvas'); // keeping ID to avoid changing index.html fully
const ctx = canvas.getContext('2d');
let isEditing = false;
let isDragging = false;
let selectedHandle = -1; // 0-3 for corners
let zoneCoords = [
    { x: 0.2, y: 0.2 }, 
    { x: 0.8, y: 0.2 }, 
    { x: 0.8, y: 0.8 }, 
    { x: 0.2, y: 0.8 }
]; // Normalized coordinates (0-1)

function initZoneEditor() {
    const resizeCanvas = () => {
        const container = document.querySelector('.view-container');
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            drawZone();
        }
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    canvas.addEventListener('mousedown', (e) => {
        if (!isEditing) return;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        for (let i = 0; i < 4; i++) {
            const px = zoneCoords[i].x * canvas.width;
            const py = zoneCoords[i].y * canvas.height;
            if (dist(mouseX, mouseY, px, py) < 20) {
                isDragging = true;
                selectedHandle = i;
                break;
            }
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const rect = canvas.getBoundingClientRect();
        zoneCoords[selectedHandle].x = Math.max(0, Math.min(1, (e.clientX - rect.left) / canvas.width));
        zoneCoords[selectedHandle].y = Math.max(0, Math.min(1, (e.clientY - rect.top) / canvas.height));
        drawZone();
    });

    canvas.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            selectedHandle = -1;
            updateZoneOnServer();
        }
    });
}

function dist(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

function drawZone() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!isEditing) return;

    ctx.beginPath();
    ctx.moveTo(zoneCoords[0].x * canvas.width, zoneCoords[0].y * canvas.height);
    for (let i = 1; i < 4; i++) {
        ctx.lineTo(zoneCoords[i].x * canvas.width, zoneCoords[i].y * canvas.height);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 255, 255, 0.2)';
    ctx.fill();
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.fillStyle = '#ff00ff';
    for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        ctx.arc(zoneCoords[i].x * canvas.width, zoneCoords[i].y * canvas.height, 8, 0, Math.PI * 2);
        ctx.fill();
    }
}

async function updateZoneOnServer() {
    const W = 640;
    const H = 480;
    const serverZone = zoneCoords.map(p => [p.x * W, p.y * H]);
    const entryEdge = document.getElementById('entry-edge-select').value;
    const exitEdge = document.getElementById('exit-edge-select').value;
    
    try {
        await fetch(`${API_URL}/update_zone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zone: serverZone, entry_edge: entryEdge, exit_edge: exitEdge })
        });
    } catch (e) {
        console.error("Failed to update zone", e);
    }
}

document.getElementById('entry-edge-select').addEventListener('change', () => {
    updateZoneOnServer();
});
document.getElementById('exit-edge-select').addEventListener('change', () => {
    updateZoneOnServer();
});

document.getElementById('edit-zone-btn').addEventListener('click', () => {
    isEditing = !isEditing;
    const btn = document.getElementById('edit-zone-btn');
    const cvs = document.getElementById('tripwire-canvas');

    if (isEditing) {
        btn.style.background = '#eab308';
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Done';
        cvs.style.pointerEvents = 'auto';
        drawZone();
    } else {
        btn.style.background = 'rgba(0,0,0,0.3)';
        btn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Zone';
        cvs.style.pointerEvents = 'none';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
});

initZoneEditor();
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

// --- Live Chart ---
const chartCtx = document.getElementById('countChart').getContext('2d');
const maxDataPoints = 60; // 60 seconds of history
const chartData = {
    labels: [],
    datasets: [
        {
            label: 'In Room',
            data: [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true
        },
        {
            label: 'IN',
            data: [],
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4,
            fill: false
        },
        {
            label: 'OUT',
            data: [],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            fill: false
        }
    ]
};

const countChart = new Chart(chartCtx, {
    type: 'line',
    data: chartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: '#fff' }
            }
        },
        scales: {
            x: {
                ticks: { color: '#aaa' },
                grid: { color: 'rgba(255,255,255,0.1)' }
            },
            y: {
                beginAtZero: true,
                ticks: { color: '#aaa' },
                grid: { color: 'rgba(255,255,255,0.1)' }
            }
        },
        animation: { duration: 0 }
    }
});

// Update chart every second
setInterval(async () => {
    try {
        const res = await fetch(`${API_URL}/stats`);
        if (res.ok) {
            const stats = await res.json();
            const now = new Date().toLocaleTimeString();

            // Add new data point
            chartData.labels.push(now);
            chartData.datasets[0].data.push(stats.in_room_count || 0);
            chartData.datasets[1].data.push(stats.in_count || 0);
            chartData.datasets[2].data.push(stats.out_count || 0);

            // Keep only last 60 points
            if (chartData.labels.length > maxDataPoints) {
                chartData.labels.shift();
                chartData.datasets.forEach(ds => ds.data.shift());
            }

            countChart.update();
        }
    } catch (e) {
        console.error("Chart update error:", e);
    }
}, 1000);

// Session History Logic
const startBtn = document.getElementById('start-count-btn');
const finishBtn = document.getElementById('finish-count-btn');

startBtn.addEventListener('click', async () => {
    try {
        await fetch(`${API_URL}/start_counting`, { method: 'POST' });
        startBtn.style.boxShadow = "0 0 10px #22c55e";
        setTimeout(() => startBtn.style.boxShadow = "none", 1000);
    } catch(e) { console.error("Start count error:", e); }
});

finishBtn.addEventListener('click', async () => {
    try {
        await fetch(`${API_URL}/finish_counting`, { method: 'POST' });
        finishBtn.style.boxShadow = "0 0 10px #ef4444";
        setTimeout(() => finishBtn.style.boxShadow = "none", 1000);
        loadHistory();
    } catch(e) { console.error("Finish count error:", e); }
});

async function loadHistory() {
    try {
        const res = await fetch(`${API_URL}/history`);
        if (!res.ok) return;
        const data = await res.json();
        const tbody = document.getElementById('history-tbody');
        if (!tbody) return;
        tbody.innerHTML = "";
        data.reverse().forEach(record => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1);">${record.date}</td>
                <td style="padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1);">${record.duration}</td>
                <td style="padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); color: #22c55e;">${record.in_count}</td>
                <td style="padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); color: #ef4444;">${record.out_count}</td>
                <td style="padding: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); color: #00ffff;">${record.in_room_end}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch(e) {
        console.error("Failed to load history", e);
    }
}

// Load history on initial mount
loadHistory();

