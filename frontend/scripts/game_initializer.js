import {fetchCsrfToken, joinRoom} from './utils.js'
import WebSocketManager from './managers/websocket_manager.js'
import CanvasManager from './managers/canvas_manager.js'
import ChatManager from './managers/chat_manager.js'

// Parse query parameters
const params = new URLSearchParams(window.location.search);
const username = params.get('username');
const room_code = params.get('room_code') || '';
const room_type = params.get('room_type') || 'public';

console.log(username, room_code, room_type);

// Configuration
const WS_BASE_URL = "ws://localhost:8000/ws/game/";

// Initialize game
export async function initializeGame(player_name, room_code, room_type) {
    try {
        const csrfToken = await fetchCsrfToken();
        const response = await joinRoom(csrfToken, player_name, room_code, room_type);
        
        if (response === null || response === false) {
            window.location.href = `index.html`
            return
        }

        const { id: playerId, room: roomId } = response
        const wsUrl = `${WS_BASE_URL}${roomId}/${playerId}/`;
        console.log("Joined room:", roomId, "as player:", playerId);

        const wsManager = new WebSocketManager(wsUrl, player_name, (canvasdata) => canvasManager.websocketActions(canvasdata), (chatdata) => chatManager.displayMessage(chatdata));
        const canvasManager = new CanvasManager(wsManager);
        const chatManager = new ChatManager(wsManager);

        // Create a button to start the game
        const startButtonContainer = document.getElementById('start-game');
        const newGameButton = document.createElement("button");
        newGameButton.className = 'btn'
        newGameButton.textContent = "Start New Game";
        newGameButton.addEventListener("click", handleNewGameClick);
        startButtonContainer.appendChild(newGameButton);

        // Handle new game button click
        function handleNewGameClick() {
            if (!wsManager.game_started) {

                const message = { type: "new_game" };
                wsManager.sendMessage(message); 
            }
        }

    } catch (error) {
        console.error("Error initializing game: ", error);
        window.location.href = 'index.html';
        alert(error)
    }
}

// Start the game
initializeGame(username, room_code, room_type);