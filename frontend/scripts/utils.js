// Configuration
const API_BASE_URL = "http://127.0.0.1:8000/games";

// Utility to fetch CSRF token
export async function fetchCsrfToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/get-csrf-token/`, {
            credentials: 'include', // Ensures cookies (CSRF token) are sent
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch CSRF token: ${response.status}`);
        }

        const data = await response.json(); // Wait for JSON parsing
        return data.csrfToken; // Ensure correct property name
    } catch (error) {
        console.error("Error fetching CSRF token:", error);
        throw error;
    }
}


// Utility to join a room
export async function joinRoom(csrfToken, player_name, room_code, room_type) {
    try {
        const response = await fetch(`${API_BASE_URL}/join-room`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ name: player_name, unique_code: room_code, type: room_type }),
        });
        if (!response.ok) {
            throw new Error(`Failed to join room: ${response.status}`);
        }
        return await  response.json();
    } catch (error) {
        console.error("Error joining room:", error);
        throw error;
    }
}
