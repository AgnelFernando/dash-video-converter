
# 📼 DASH Video Converter

This project is a scalable, production-ready video processing pipeline that automatically converts uploaded videos into **MPEG-DASH** format for adaptive streaming. It supports multiple resolutions (e.g., 360p, 720p), generates video thumbnails, and uploads outputs to AWS S3.

Built using **FastAPI**, **Celery**, **Redis**, **FFmpeg**, **Shaka Packager**, and **Docker**.

---

## 🚀 Features

- 🎥 Convert videos into MPEG-DASH with 360p and 720p tracks
- ⚡ Asynchronous task execution using Celery and Redis
- ☁️ Upload/download videos to/from AWS S3
- 🖼️ Generate preview thumbnails
- 📊 Monitor tasks via [Flower](https://flower.readthedocs.io/en/latest/)
- 🔐 API key–protected endpoints
- 🔧 Easily deployable with Docker Compose + Traefik reverse proxy

---

## 📁 Project Structure

```

dash-video-converter/
├── app/
│   ├── api/               # FastAPI endpoints & dependencies
│   ├── db/                # SQLAlchemy models & CRUD operations
│   ├── worker/            # Celery config and video processing tasks
│   ├── Dockerfile         # Shared by web and worker services
│   └── requirements.txt   # Python dependencies
├── docker-compose.yml
├── docker-compose.override.yml
└── README.md

````

---

## 🛠️ Technologies Used

- **FastAPI** – REST API server
- **Celery** – Background job queue for video processing
- **Redis** – Message broker between FastAPI and Celery
- **FFmpeg** – Video transcoding to different bitrates/resolutions
- **Shaka Packager** – MPEG-DASH segmenting & manifest generation
- **AWS S3** – Cloud storage for input/output videos
- **Flower** – Real-time monitoring of Celery workers
- **Docker Compose** – Service orchestration
- **Traefik** – Optional HTTPS reverse proxy with automatic TLS

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/AgnelFernando/dash-video-converter.git
cd dash-video-converter
````

### 2. Configure Environment Variables

Create these files:

* `app/api/api.env`
* `app/worker/worker.env`

And include required variables:

```env
# api.env & worker.env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_INPUT_BUCKET=your_input_bucket
S3_OUTPUT_BUCKET=your_output_bucket
S3_THUMBNAIL_OUTPUT_BUCKET=your_thumbnail_bucket
MAIN_API_ENDPOINT=http://localhost:8080
MAIN_API_KEY=your_api_key
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 3. Build and Run the Application

```bash
docker-compose up --build
```

The services that will start:

* **FastAPI** on `http://localhost:8080`
* **Celery Worker**
* **Redis**
* **Flower Dashboard** on `http://localhost:5556`

---

## 📬 API Usage

### 🔒 Authentication

All endpoints require an API key via header:

```http
ApiKey: your_api_key
```

### 🎦 POST `/video/encoding`

Trigger a video processing task.

#### Request Body:

```json
{
  "object_key": "your-s3-input-file.mp4",
  "base_url": "https://cdn.example.com/output/",
  "video_id": "abc123",
  "has_audio": true
}
```

#### Example Response:

```json
"e53da4fe-124b-4f6c-9f76-24fc83982f7b"  // task ID
```

---

### 📊 GET `/video/encoding/{task_id}`

Check status of a video encoding task.

#### Example Response:

```json
{
  "task_id": "e53da4fe-...",
  "task_status": "SUCCESS",
  "task_result": "abc123"
}
```

---

## 🌐 Traefik HTTPS Setup

The `docker-compose.override.yml` provides support for running behind Traefik with Let's Encrypt.

Update `traefik.toml` and domain entries as needed.

---

Great call — I provided a high-level breakdown earlier but didn’t include a dedicated “How It Works” section in the `README`. Here’s a clearly written version you can add right before the “📬 API Usage” section:

---

## 🔄 How it Works

The video processing pipeline works in **two stages** using FastAPI, Celery, FFmpeg, and Shaka Packager.

### 📥 1. Client Upload Request

* A client sends a **video encoding request** (just metadata, not the file) to the FastAPI API.
* The video must already exist in a configured **S3 input bucket**.

### ⚙️ 2. Initial DASH Generation (720p)

* The FastAPI server queues a task `create_initial_dash` via **Celery**.
* This task:

  * Downloads the original video from S3
  * Transcodes it to 720p using **FFmpeg**
  * Segments it into MPEG-DASH format using **Shaka Packager**
  * Uploads DASH output and a **video preview thumbnail** to S3
  * Marks the request status as `SUCCESS`

### 📦 3. Secondary Resolution (360p)

* Once the initial DASH is ready, a second task `create_dash` is automatically triggered.
* This task:

  * Generates the 360p version
  * Updates the DASH manifest with multiple qualities
  * Syncs the final output to S3 again

### 🔁 4. Status & Notification

* The API provides a `GET /video/encoding/{task_id}` endpoint for checking status.
* Once a task completes (or fails), a notification is sent to a configured backend endpoint.

