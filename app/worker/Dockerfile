FROM google/shaka-packager:latest as shaka
FROM petnion/ffmpeg-python

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt && \
    pip install awscli requests

# copy shaka
COPY --from=shaka /usr/bin/packager \
                    /usr/bin/mpd_generator \
                    /usr/bin/pssh-box.py \
                    /usr/bin/
COPY --from=shaka /usr/bin/pyproto /usr/bin/pyproto

# copy project
COPY . .

ENTRYPOINT []