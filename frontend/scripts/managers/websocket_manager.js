// WebSocket Manager Class

export default class WebSocketManager {
    constructor(url, playerName, canvasMessageHandler, chatMessageHandler) {
        this.playerName = playerName;
        this.drawer_name = null;
        this.current_word = null;
        this.turn_count = null;
        this.game_started = false;
        this.skip_turn = false;

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
        // // Update drawer name
        const drawerNameElement = document.getElementById("timer");
        drawerNameElement.textContent = "0";

        // Update current word (hidden or hints)
        const wordElement = document.getElementById("word");
        wordElement.textContent = this.current_word || "_ _ _ _";

        // Update turn count
        const counterElement = document.getElementById("counter");
        counterElement.textContent = this.turn_count ? `Round: ${this.turn_count}` : "Round:";
    }

    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            const chatMessageTypes = new Set(["guess", "chat_message", "player_joined", "player_left"]);
            const drawingMessageTypes = new Set(["drawing", "clear_canvas"])

            if (drawingMessageTypes.has(data.type)) {
                this.canvasMessageHandler(data);
            }
            else if (chatMessageTypes.has(data.type)){
                this.chatMessageHandler(data);
                this.updateHeader()
                if (this.game_started) {
                    const startButton = document.getElementById('start-game');
                    startButton.style.display = 'none';
                }
            }
            else if (data.type === 'ping'){
                console.log('pong')
            }
            else if (data.type === 'new_game') {
                this.game_started = true;

                const startButtonContainer = document.getElementById('start-game');
                startButtonContainer.style.display = 'none';

                let seconds = data.timeout; // Start countdown from this value
            
                const modal = document.getElementById('new-game-modal');
                const header = document.getElementById('timer');
                modal.style.display = 'flex'; // Show the modal
                 
                // Countdown logic
                const countdown = setInterval(() => {
                    seconds--; // Decrease the seconds by 1
                    header.textContent = seconds; // Update the timer display
            
                    // Stop the timer at 0
                    if (seconds <= 1) {
                        clearInterval(countdown);
                        header.textContent = "Don't lose!";

                        setTimeout(() => {
                            modal.style.display = 'none'; 
                          }, 2000)            
                    }   
                }, 1000);
            }
            else if (data.type === "new_turn") {
                this.drawer_name = data.drawer;
                this.turn_count = data.turn;
                this.skip_turn = false;
                this.updateHeader();

                let seconds = data.timeout; // Start countdown from this value
                const header = document.getElementById('countdown');
                header.textContent = seconds;
                
                // Countdown logic
                const countdown = setInterval(() => {
                    seconds--; // Decrease the seconds by 1
                    header.textContent = seconds; // Update the timer display
            
                    // Stop the timer at 0
                    if (seconds <= 2  || this.skip_turn) {
                        clearInterval(countdown);
                        console.log(this.skip_turn)
                        setTimeout(() => {
                            header.textContent = "timeout";
                        }, 2000)            
                    }
                }, 1000);
                header.textContent = 0;
            }
            else if (data.type === "hint_update") {
                this.current_word = data.hint;
                this.updateHeader();
            }
            else if (data.type === "skipping_turn") {
                this.skip_turn = true
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
            } 
            else if (data.type === 'display_score') {
                const timeout = data.timeout;
                const scoreboard = data.scoreboard;
                const modal = document.getElementById('scoreboard-modal');

                // Display scoreboard in the modal
                const scoreboardList = document.getElementById('score-lists');
                scoreboardList.innerHTML = ''; // Clear previous choice
                
                const guessWord = document.getElementById('guess-word');
                guessWord.textContent = `The word is: ${data.word}`;

                scoreboard.forEach(player => {
                    const li = document.createElement('li');
                    li.textContent = `${player.name}: ${player.score}`;
                    
                    scoreboardList.appendChild(li);
                });

                modal.style.display = 'flex'

                setTimeout(() => {
                    const modal = document.getElementById('scoreboard-modal');
                    if (modal.style.display === 'flex') {
                        modal.style.display = 'none';}
                }, timeout * 1000);
            } 
            else if (data.type === 'word_choices' && this.drawer_name === this.playerName) {
                const wordChoices = data.choices;
                const timeout = data.timeout;

                const modal = document.getElementById('word-choice-modal');
                
                // Display word choices in the modal
                const wordChoicesList = document.getElementById('word-choices');
                wordChoicesList.innerHTML = ''; // Clear previous choices
                wordChoices.forEach(word => {
                  const li = document.createElement('li');
                  li.textContent = word;
                  li.addEventListener('click', () => {
                    // Send the chosen word to the server
                    this.socket.send(JSON.stringify({
                      type: 'word_chosen',
                      word: word,
                      name: this.playerName,
                    }));
                    // Hide the modal
                    modal.style.display = 'none';
                  });
                  wordChoicesList.appendChild(li);
                });
                modal.style.display = 'flex'; // Show the modal
                
                setTimeout(() => {
                    const modal = document.getElementById('word-choice-modal');
                    if (modal.style.display === 'flex') {
                        modal.style.display = 'none';}
                }, timeout * 1000);
            }
            else if (data.type === 'drawer_choosing_word' && this.drawer_name !== this.playerName){
                const timeout = data.timeout;

                const modal = document.getElementById('drawer-choosing-modal')
                const header = document.getElementById('drawer-choosing')
                header.textContent = `${this.drawer_name} is choosing a word...`

                modal.style.display = 'flex'; // Show the modal
                setTimeout(() => {
                    const modal = document.getElementById('drawer-choosing-modal');
                    if (modal.style.display === 'flex') {
                        modal.style.display = 'none';}
                }, timeout * 1000);
            }
            else if (data.type === 'clear_modal') {
                const modals = document.getElementsByClassName('modal');
                if (modals.length === 0) {
                    console.warn("No modals found to clear.");
                }
                for (const modal of modals) {
                    modal.style.display = 'none'; // Set display to none for each modal
                }
            }
            else {
                console.log(this.playerName, '----', this.drawer_name)
                console.log(`Received message: ${data.message}`,);
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    }

    onClose() {
        console.warn("WebSocket disconnected. Reconnecting...");
        // setTimeout(() => this.connect(), 3000); // Reconnect after 3 seconds
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
