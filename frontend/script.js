// Parse query parameters
const params = new URLSearchParams(window.location.search);
const username = params.get('username');
const room = params.get('room') || 'new';

// Configuration
const API_BASE_URL = "http://127.0.0.1:8000/games";
const WS_BASE_URL = "ws://localhost:8000/ws/game/";

// Utility to fetch CSRF token
async function fetchCsrfToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/get-csrf-token/`);
        if (!response.ok) throw new Error(`Failed to fetch CSRF token: ${response.status}`);
        const { csrfToken } = await response.json();
        return csrfToken;
    } catch (error) {
        console.error("Error fetching CSRF token:", error);
        throw error;
    }
}

// Utility to join a room
async function joinRoom(csrfToken, playerName) {
    try {
        const response = await fetch(`${API_BASE_URL}/join-room`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ name: playerName }),
        });
        if (!response.ok) throw new Error(`Failed to join room: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Error joining room:", error);
        throw error;
    }
}

// WebSocket Manager Class
class WebSocketManager {
    constructor(url, canvasMessageHandler, chatMessageHandler) {
        this.drawer_name = null;
        this.current_word = null;
        this.turn_count = null;

        this.url = url;
        this.canvasMessageHandler = canvasMessageHandler;
        this.chatMessageHandler = chatMessageHandler;
        this.connect();
    }

    connect() {
        this.socket = new WebSocket(this.url);
        this.socket.onopen = () => console.log("Connected to WebSocket server.");
        this.socket.onmessage = this.onMessage.bind(this);
        this.socket.onclose = this.onClose.bind(this);
        this.socket.onerror = this.onError.bind(this);
    }

    updateHeader() {
        // Update drawer name
        const drawerNameElement = document.getElementById("drawer-name");
        drawerNameElement.textContent = this.drawer_name || "Waiting...";

        // Update current word (hidden or hints)
        const wordElement = document.getElementById("word");
        wordElement.textContent = this.current_word || "_ _ _ _";

        // Update turn count
        const counterElement = document.getElementById("counter");
        counterElement.textContent = this.turn_count ? `Turn: ${this.turn_count}` : "";
    }

    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "drawing" || data.type === "clear_canvas") {
                this.canvasMessageHandler(data);
            }
            else if (data.type === "guess" || data.type === "player_joined" || data.type === "player_left") {
                this.chatMessageHandler(data);
            }
            else if (data.type === "new_turn") {
                this.drawer_name = data.name;
                this.turn_count = data.turn;
                this.current_word = data.word;
                this.updateHeader();
            }
            else if (data.type === "hint_update") {
                this.current_word = data.hint;
                this.updateHeader();
            }
            else if (data.type === "leaderboard_update") {
                const leaderboardList = document.getElementById("leaderboard-list");
                leaderboardList.innerHTML = ""; // Clear the list
                const leaderboard = data.leaderboard;

                leaderboard.forEach(player => {
                    const li = document.createElement("li");
                    li.textContent = `${player.name}: ${player.score}`;
                    leaderboardList.appendChild(li);
                });
            } else {
                console.log(`Received message: ${data.type}`, data);
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    }

    onClose() {
        console.warn("WebSocket disconnected. Reconnecting...");
        setTimeout(() => this.connect(), 3000); // Reconnect after 3 seconds
    }

    onError(error) {
        console.error("WebSocket error:", error);
    }

    sendMessage(message) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.warn("WebSocket not open. Message not sent:", message);
        }
    }
}

// Canvas Manager Class
class CanvasManager {
    constructor(wsManager) {
        this.canvas = document.getElementById("drawing-canvas");
        this.ctx = this.canvas.getContext("2d");
        this.wsManager = wsManager;
        this.colorPicker = document.getElementById("color-picker");
        this.brushSizePicker = document.getElementById("brush-size");
        this.clearCanvasButton = document.getElementById('clear-canvas');
        this.drawing = false;
        this.lastX = 0;
        this.lastY = 0;

        this.initializeCanvas();
        this.setupEventListeners();
    }

    initializeCanvas() {
        this.resizeCanvas();
        window.addEventListener("resize", this.resizeCanvas.bind(this));
        this.ctx.lineCap = "round";
        this.ctx.lineJoin = "round";
    }

    resizeCanvas() {
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);

        const oldWidth = this.canvas.width;
        const oldHeight = this.canvas.height;

        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetWidth / 16 * 16; // Maintain 16:9 aspect ratio

        const scaleX = this.canvas.width / oldWidth;
        const scaleY = this.canvas.height / oldHeight;

        this.ctx.scale(scaleX, scaleY);
        this.ctx.putImageData(imageData, 0, 0);

        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    }

    setupEventListeners() {
        this.colorPicker.addEventListener("input", () => {
            this.ctx.strokeStyle = this.colorPicker.value;
        });
        this.brushSizePicker.addEventListener("input", () => {
            this.ctx.lineWidth = this.brushSizePicker.value;
        });

        this.clearCanvasButton.addEventListener('click', this.sendClearCanvas.bind(this));

        // Mouse events
        this.canvas.addEventListener("mousedown", this.startDrawing.bind(this));
        this.canvas.addEventListener("mousemove", this.draw.bind(this));
        this.canvas.addEventListener("mouseup", this.stopDrawing.bind(this));
        this.canvas.addEventListener("mouseout", this.stopDrawing.bind(this));

        // Touch events
        this.canvas.addEventListener("touchstart", this.startTouchDrawing.bind(this));
        this.canvas.addEventListener("touchmove", this.touchDraw.bind(this));
        this.canvas.addEventListener("touchend", this.stopDrawing.bind(this));
        this.canvas.addEventListener("touchcancel", this.stopDrawing.bind(this));
    }

    normalizeTouchEvent(e) {
        const rect = this.canvas.getBoundingClientRect();
        const touch = e.touches[0] || e.changedTouches[0];
        return {
            x: touch.clientX - rect.left,
            y: touch.clientY - rect.top,
        };
    }

    startDrawing(e) {
        this.drawing = true;
        [this.lastX, this.lastY] = [e.offsetX, e.offsetY];
    }

    startTouchDrawing(e) {
        e.preventDefault(); // Prevent scrolling or zooming
        const { x, y } = this.normalizeTouchEvent(e);
        this.drawing = true;
        [this.lastX, this.lastY] = [x, y];
    }

    draw(e) {
        if (!this.drawing || this.wsManager.drawer_name === username) return;

        const currentX = e.offsetX;
        const currentY = e.offsetY;

        const drawingData = {
            type: "drawing",
            start: { x: this.lastX, y: this.lastY },
            end: { x: currentX, y: currentY },
            color: this.ctx.strokeStyle,
            thickness: this.ctx.lineWidth,
        };
        this.wsManager.sendMessage(drawingData);

        this.renderIncomingDrawing(drawingData);
        [this.lastX, this.lastY] = [currentX, currentY];
    }

    touchDraw(e) {
        if (!this.drawing || this.wsManager.drawer_name === username) return;
        e.preventDefault(); // Prevent scrolling or zooming

        const { x: currentX, y: currentY } = this.normalizeTouchEvent(e);

        const drawingData = {
            type: "drawing",
            start: { x: this.lastX, y: this.lastY },
            end: { x: currentX, y: currentY },
            color: this.ctx.strokeStyle,
            thickness: this.ctx.lineWidth,
        };
        this.wsManager.sendMessage(drawingData);

        [this.lastX, this.lastY] = [currentX, currentY];
    }

    stopDrawing() {
        this.drawing = false;
        this.ctx.beginPath();
    }
    
    websocketActions(event) {
        if (event.type === "drawing") {
            this.renderIncomingDrawing(event)
        }
        else if (event.type === "clear_canvas") {
            this.eraseDrawing()
        }
    }

    sendClearCanvas() {
        const data = {type: "clear_canvas"}
        console.log(data)
        this.wsManager.sendMessage(data)
    }

    eraseDrawing() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    renderIncomingDrawing(data) {
        const { start, end, color, thickness } = data;
        this.ctx.beginPath();
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = thickness;
        this.ctx.moveTo(start.x, start.y);
        this.ctx.lineTo(end.x, end.y);
        this.ctx.stroke();
    }
}


class ChatManager {
    constructor(wsManager) {
        this.chatInput = document.getElementById("chat-input");
        this.chatSendButton = document.getElementById("send-message");
        this.chatMessages = document.getElementById("chat-messages");
        this.wsManager = wsManager;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Send message on button click
        this.chatSendButton.addEventListener("click", this.sendMessage.bind(this));

        // Send message on Enter key
        this.chatInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                this.sendMessage.bind(this);
            }
        });
    }

    sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Prepare message payload
        const chatMessage = {
            type: "guess",
            guess: message,
        };

        // Send message via WebSocket
        this.wsManager.sendMessage(chatMessage);

        // Clear the input field
        this.chatInput.value = "";
    }

    displayMessage(message) {
        const messageElement = document.createElement("div");
        messageElement.className = `chat-message`;
        if (message.type === "guess") {
            messageElement.textContent = `${message.name}: ${message.guess}`;
            if (message.correct === true) {    
                messageElement.className = 'green-text';
            }
        } else if (message.type === "player_joined") {
            messageElement.textContent = `${message.id} joined room`;
            messageElement.className = 'green-text';
        } else if (message.type === "player_left") {
            messageElement.textContent = `${message.id} left room`;
            messageElement.className = 'red-text';
        }
        this.chatMessages.appendChild(messageElement);

        // Scroll to the latest message
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}


// Initialize game
async function initializeGame(playerName) {
    try {
        const csrfToken = await fetchCsrfToken();
        const { id: playerId, room: roomId } = await joinRoom(csrfToken, playerName);
        const wsUrl = `${WS_BASE_URL}${roomId}/${playerId}/`;

        console.log("Joined room:", roomId, "as player:", playerId);

        const wsManager = new WebSocketManager(wsUrl, (canvasdata) => canvasManager.websocketActions(canvasdata), (chatdata) => chatManager.displayMessage(chatdata));
        const canvasManager = new CanvasManager(wsManager);
        const chatManager = new ChatManager(wsManager);
    } catch (error) {
        console.error("Error initializing game: ", error);
    }
}

// Start the game
initializeGame(username);
