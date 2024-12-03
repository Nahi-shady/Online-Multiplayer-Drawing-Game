
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
