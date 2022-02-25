# MPEG-DASH Video converter

Server use FFmpeg, S3, Docker, Python, Shaka Packager to create MPEG-DASH video from a given video.

### Flow of Application:
1. Place the input video in INPUT_S3_BUCKET
2. send video encoding request to server endpoint and return task id
3. Download the video from INPUT_S3_BUCKET and create MPEG-DASH with 360p, 720p  
variations.
4. And upload to OUTPUT_S3_BUCKETS
5. optinally send result of video encoding to given api endpoint
