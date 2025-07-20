# 📝 FastAPI Blog Backend

A simple and robust blog backend built with **FastAPI**, **MongoDB**, and **Redis**.  
It supports user authentication, post creation, comments, and search – all wrapped in a clean microservice architecture and ready for production or local testing.

---

## 🚀 Features

- 🔐 JWT-based user registration and login
- 📝 Create, update, delete and search blog posts
- 💬 Add and manage comments on posts
- ⚡ Async support using `motor` and `httpx`
- 🧪 Full testing coverage with `pytest` and `httpx`
- 🐳 Docker & Docker Compose setup for local development

---

## 🧰 Tech Stack

- Python 3.9
- FastAPI
- MongoDB (via `motor`)
- Redis (optional for caching / rate limits)
- JWT authentication (`python-jose`)
- Docker & docker-compose

---

## ⚙️ How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/ramati101/yaballe.git
cd yaballe
```


### Build and start the containers
- docker-compose --env-file .env.docker build
- docker-compose --env-file .env.docker up

### * FastAPI doc will be available at: http://localhost:8000/docs


### Running Tests From inside the Docker container
- Open a shell inside the app container - 'docker exec -it blog-app bash'
- 'pytest tests/'
