
// WebSocket Manager
class WebSocketManager {
    constructor(url, onMessageHandler) {
        this.socket = new WebSocket(url);
        this.onMessageHandler = onMessageHandler;

        this.socket.onopen = this.onOpen.bind(this);
        this.socket.onmessage = this.onMessage.bind(this);
        this.socket.onclose = this.onClose.bind(this);
        this.socket.onerror = this.onError.bind(this);
    }

    onOpen() {
        console.log("Connected to WebSocket server.");
    }

    onMessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'drawing') {
            this.onMessageHandler(data);
        }
        else if (data.type === 'player_joined') {
            console.log('Player -', data.id, ' joined the group');
        }
        else if (data.type === 'player_left') {
            console.log('Player -', data.id, ' left the group');
        }
        else if (data.type === 'leaderboard_update') {
            console.log('Player Leaderboard')
            // const leaderboard = data.leaderboard
            // leaderboard.forEach(player => {
            //     console.log(player.name, player.score)
            // });
        }
        else if (data.type === 'message') {
            console.log(data.type, ": ", data.message )
        }
        else if (data.type === 'new_turn') {
            console.log(data.type, "drawer: ", data.drawer, 'turn: ', data.turn)
        }
        else {
            console.log('other', data)
        }
    }
    
    onClose() {
        console.log("Disconnected from WebSocket server.");
    }

    onError(error) {
        console.error("WebSocket error:", error);
    }
    
    sendMessage(message) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.warn("WebSocket is not open. Message not sent:", message);
        }
    }
}

// Canvas Manager
class CanvasManager {
    constructor(canvasId, wsManager) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext("2d");
        this.colorPicker = document.getElementById('color');
        this.brushSizePicker = document.getElementById('brush-size');
        
        this.wsManager = wsManager;

        this.drawing = false;
        this.lastX = 0;
        this.lastY = 0;

        this.initializeCanvas();
    }

    initializeCanvas() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;

        // Set initial brush settings
        this.ctx.strokeStyle = this.colorPicker.value;
        this.ctx.lineWidth = this.brushSizePicker.value;
        this.ctx.lineCap = 'round'; // Smooth edges
        this.ctx.lineJoin = 'round'; // Smooth edges
        
        // Update brush settings
        this.colorPicker.addEventListener('input', () => {
            this.ctx.strokeStyle = this.colorPicker.value;
        });

        this.brushSizePicker.addEventListener('input', () => {
            this.ctx.lineWidth = this.brushSizePicker.value;
        });

        
        // Event listeners for drawing
        this.canvas.addEventListener("mousedown", this.startDrawing.bind(this));
        this.canvas.addEventListener("mousemove", this.draw.bind(this));
        this.canvas.addEventListener("mouseup", this.stopDrawing.bind(this));
        this.canvas.addEventListener("mouseout", this.stopDrawing.bind(this));
    }

    startDrawing(e) {
        this.drawing = true;
        [this.lastX, this.lastY] = [e.offsetX, e.offsetY];
    }

    draw(e) {
        if (!this.drawing) return;

        const currentX = e.offsetX;
        const currentY = e.offsetY;

        // Draw locally
        // this.ctx.beginPath();
        // this.ctx.moveTo(this.lastX, this.lastY);
        // this.ctx.lineTo(currentX, currentY);
        // this.ctx.strokeStyle = "#000000"; // Default color
        // this.ctx.lineWidth = 2; // Default line width
        // this.ctx.stroke();
        console.log(`From (${this.lastX}, ${this.lastY}) to (${e.offsetX}, ${e.offsetY})`);

        // Broadcast drawing data to the server
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
        this.ctx.beginPath()
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
