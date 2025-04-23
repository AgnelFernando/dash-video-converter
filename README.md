# MPEG-DASH Video Converter

A Python-based server application that automates the conversion of input videos into MPEG-DASH format using FFmpeg and Shaka Packager. It integrates with AWS S3 for storage and utilizes Docker for containerized deployment.

## Features

- Converts videos to MPEG-DASH format with 360p and 720p resolutions.
- Supports input and output via AWS S3 buckets.
- Containerized using Docker and orchestrated with Docker Compose.
- Optional callback to notify external services upon completion.

## Architecture Overview

1. **Input**: Upload your video file to the designated `INPUT_S3_BUCKET`.
2. **Request**: Send a video encoding request to the server's API endpoint; receive a task ID in response.
3. **Processing**: The server downloads the video from `INPUT_S3_BUCKET`, processes it into MPEG-DASH format with specified resolutions.
4. **Output**: The processed video is uploaded to `OUTPUT_S3_BUCKET`.
5. **Notification**: Optionally, the server sends the result of the video encoding to a specified API endpoint.

## Prerequisites

- Docker and Docker Compose installed on your system.
- AWS credentials with access to the specified S3 buckets.

## Setup and Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/AgnelFernando/dash-video-converter.git
   cd dash-video-converter
   ```


2. **Configure Environment Variables**:

   Create a `.env` file in the root directory with the following content:

   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   INPUT_S3_BUCKET=your_input_bucket
   OUTPUT_S3_BUCKET=your_output_bucket
   CALLBACK_URL=optional_callback_url
   ```


3. **Build and Run the Docker Containers**:

   ```bash
   docker-compose up --build
   ```


## Usage

1. **Upload Video**:

   Place your input video file into the specified `INPUT_S3_BUCKET`.

2. **Send Encoding Request**:

   Make a POST request to the server's API endpoint to initiate the encoding process. The server will respond with a task ID.

3. **Monitor Progress**:

   Use the task ID to query the status of the encoding process.

4. **Retrieve Output**:

   Once processing is complete, the MPEG-DASH formatted video will be available in the `OUTPUT_S3_BUCKET`.

5. **Receive Notification**:

   If a `CALLBACK_URL` is provided, the server will send a POST request to this URL with the result of the encoding process.

## API Endpoints

- **POST /encode**:

  Initiates the encoding process.

  **Request Body**:

  
```json
  {
    "video_filename": "example.mp4"
  }
  ```


  **Response**:

  
```json
  {
    "task_id": "unique_task_identifier"
  }
  ```


- **GET /status/{task_id}**:

  Retrieves the status of the specified encoding task.

  **Response**:

  
```json
  {
    "status": "processing" 
  }
  ```
 or "completed", "failed"


## Directory Structure


```plaintext
dash-video-converter/
├── app/
│   ├── main.py
│   ├── encoder.py
│   └── utils.py
├── docker-compose.yml
├── docker-compose.override.yaml
├── .gitignore
└── README.md
```


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FFmpeg](https://ffmpeg.org/)
- [Shaka Packager](https://github.com/shaka-project/shaka-packager)
- [Docker](https://www.docker.com/)
- [AWS S3](https://aws.amazon.com/s3/)
