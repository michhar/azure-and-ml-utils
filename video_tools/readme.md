# Usage

## `rtsp-server.py`

This Python script creates an RTSP endpoint locally from a local video file.

### Prerequisites

Install GStreamer in Linux environment:
```
sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-base-apps
sudo apt-get install gir1.2-gst-rtsp-server-1.0
sudo apt-get install python-gst-1.0 python3-gst-1.0
sudo apt-get install python3-opencv
```

See [Getting Started (PyGObject)](https://pygobject.readthedocs.io/en/latest/getting_started.html#ubuntu-getting-started) for more install instructions for Python bindings to GStreamer and other OS instructions.

### Run

```
python3 rtsp-server.py --video <my video file>
```

Using VLC from command line:

```
vlc -v rtsp://127.0.0.1:8554/stream1
```

Using GStreamer:

```
gst-launch-1.0 playbin uri=rtsp://127.0.0.1:8554/stream1
```

## `rtsp-server-live.py`

This Python script creates an RTSP endpoint locally from streams local video device (e.g.  webcam at "/dev/video0").

[See above for prerequisites](#prerequisites)

### Run

```
python3 rtsp-server-live.py --video <my video device location>
```

Using VLC from command line:

```
vlc -v rtsp://127.0.0.1:8554/stream2
```

Using GStreamer:

```
gst-launch-1.0 playbin uri=rtsp://127.0.0.1:8554/stream2
```

## Toubleshooting

### MacOS

- On macos, make sure to have the latest/updated XCode and `brew`.
    - Ensure to have gstreamer _and_ latest plugins:  `brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav` [source](https://stackoverflow.com/questions/32807973/installing-gstreamer-1-0-on-mac-os-x-mavericks)
- Check GStreamer is working in a Desktop environment with: `gst-launch-1.0 autovideosrc device="/dev/video0" ! video/x-raw,width=640,height=480 ! autovideosink` and it should open a window with a test video stream.
- For pip install of `gstreamer-python` (e.g. in https://github.com/jackersson/gst-python-tutorials) you may need to modify your `PKG_CONFIG_PATH` environment variable, e.g. `export PKG_CONFIG_PATH=/usr/local/Cellar/libffi/3.3/lib/pkgconfig/:$PKG_CONFIG_PATH`
- `export LIB_GSTREAMER_PATH=/usr/local/lib/libgstreamer-1.0.dylib`

### General

- `export GST_DEBUG=5` for extensive debugging.