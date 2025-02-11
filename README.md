# [guezzit](https://guezzit.netlify.app/)

A real-time, multiplayer drawing game.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

" Illustra is a real-time, multiplayer drawing game built with Django, Django Channels, and WebSockets. Players can join public or private game rooms, take turns drawing, and guess what is being drawn. The application supports live chat, dynamic game state updates, and a responsive canvas for a smooth drawing experience."

## Features

- **Real-time Multiplayer Drawing:** Players can draw and see each other's drawings in real time.
- **Game Room Management:** Create and join public or private rooms.
- **Turn-based Gameplay:** One player draws while others guess.
- **Live Chat:** Communicate with other players during the game.
- **Scoreboard and Leaderboard:** Track scores and display rankings.
- **Responsive UI:** Works on desktop and mobile devices.
- **WebSocket Communication:** Efficient real-time updates using Django Channels.

## Tech Stack

- **Backend:** Django, Django REST Framework, Django Channels
- **Database:** PostgreSQL
- **Real-time Communication:** WebSockets (using Daphne/Uvicorn and Redis as the channel layer)
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Deployment:** Railway, Docker
- **Other Tools:** dj-database-url, python-decouple/django-environ, WhiteNoise for static files

## Installation

### Prerequisites

- Python 3.8+  
- PostgreSQL  
- Redis (for channel layer)  
- [Pipenv](https://pipenv.pypa.io/en/latest/)

### Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Nahi-shady/Online-Multiplayer-Drawing-Game.git
    cd Online-Multiplayer-Drawing-Game
    ```

2. **Set Up the Virtual Environment:**

    ```bash
        pipenv install --dev
        pipenv shell
    ```

3. **Apply Migrations:**

    ```bash
        python manage.py migrate
    ```

4. **Create a Superuser (Optional):**

    ```bash
        python manage.py createsuperuser
    ```

## Configuration

### Environment Variables

Create a .env file in the project root (make sure it's in your .gitignore) with the following variables:

```bash
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=False
DATABASE_URL=postgres://username:password@your_db_host:your_db_port/your_db_name?sslmode=require
REDIS_URL=redis://your_redis_host:your_redis_port
```

Alternatively, set these environment variables using your hosting platform's configuration settings.

### Settings Modules

The project supports separate settings for development and production. Ensure you set the DJANGO_SETTINGS_MODULE environment variable appropriately:

```bash
export DJANGO_SETTINGS_MODULE=illustra_backend.settings.prod  # for production
```

## Usage

### Running Locally

To run the project locally using Django’s development server:

```bash
python manage.py runserver
```

For Channels (WebSocket) support, you can use Daphne:

```bash
daphne -b 0.0.0.0 -p 8000 illustra_backend.asgi:application
```

### Frontend Interaction

Open your browser and navigate to the homepage (e.g., <http://127.0.0.1:8000/>) to join or create a game room. Follow on-screen instructions to play.

## Deployment

For deploying on Railway (or another hosting provider):

1. **Configure Environment Variables:**
    Set DATABASE_URL, REDIS_URL, DJANGO_SECRET_KEY, etc., using the provider’s dashboard.

2. **Configure the ASGI Server:**

    Use Daphne or Uvicorn as your ASGI server:

    ```bash
    daphne -b 0.0.0.0 -p 8000 illustra_backend. asgi:application
    
3. **Static Files:**

    Ensure static files are collected:

    ```bash
    python manage.py collectstatic --noinput
    ```

## Contributing

I welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Make your changes and commit them (git commit -am 'Add new feature').
4. Push your branch (git push origin feature/your-feature).
5. Create a Pull Request with a clear description of your changes.
6. Please ensure that your contributions adhere to our code style guidelines and that tests pass before submitting.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact Me or open an issue in the repository.
