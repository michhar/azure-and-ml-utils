"""
Creates an RTSP endpoint at rtsp://127.0.0.1:8554/stream1
using GStreamer Python API.
Based on https://stackoverflow.com/questions/59858898/how-to-convert-a-video-on-disk-to-a-rtsp-stream
Only video, not audio.
"""
import sys
import argparse

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from gi.repository import Gst, GstRtspServer, GObject, GLib

loop = GLib.MainLoop()
Gst.init(None)

class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, video_file):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.video_file = video_file

    def do_create_element(self, url):
        #set mp4 file path to filesrc's location property
        src_demux = "filesrc location={} ! qtdemux name=demux".format(self.video_file)
        h264_transcode = "demux.video_0"
        #uncomment following line if video transcoding is necessary
        #h264_transcode = "demux.video_0 ! decodebin ! queue ! x264enc"
        pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(src_demux, h264_transcode)
        print ("Element created: " + pipeline)
        return Gst.parse_launch(pipeline)

class GstreamerRtspServer():
    def __init__(self, args):
        self.rtspServer = GstRtspServer.RTSPServer()
        factory = TestRtspMediaFactory(args.video)
        factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/stream1", factory)
        self.rtspServer.attach(None)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=str, help="Video media file")

    args = parser.parse_args()
    
    s = GstreamerRtspServer(args)
    loop.run()
