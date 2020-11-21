# Usage

**`rtsp-server.py`**

This Python script creates an RTSP endpoint locally from a local video file.

Install GStreamer in Linux environment:
```
sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-base-apps
sudo apt-get install gir1.2-gst-rtsp-server-1.0
sudo apt-get install python-gst-1.0 python3-gst-1.0
sudo apt-get install python3-opencv
```

Run with:

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
