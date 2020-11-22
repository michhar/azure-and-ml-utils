"""
Creates an RTSP endpoint from a live stream (e.g. webcam) 
at rtsp://127.0.0.1:8554/stream2 using GStreamer Python 
API and OpenCV.
"""
import argparse
import cv2
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from gi.repository import Gst, GstRtspServer, GObject, GLib


class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, video_device, **properties):
        super(SensorFactory, self).__init__(**properties)
        if video_device.isdigit():
            video_device = int(video_device)
        self.cap = cv2.VideoCapture(video_device)
        self.number_frames = 0
        self.fps = 30
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        # self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
        #                      '! rtph264pay config-interval=1 name=pay0 pt=96'
        self.launch_string = """
                                appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ! queue max-size-buffers=1 ! 
                                video/x-h264,width=1920,height=1080,framerate={} ! rtph264pay config-interval=1 pt=99 name=pay0 
                             """.format(self.fps)

    def on_need_data(self, src, length):
        if self.cap.isOpened():
            while True:
                ret, frame = self.cap.read()
                if ret:
                    data = frame.tobytes()
                    buf = Gst.Buffer.new_allocate(None, len(data), None)
                    buf.fill(0, data)
                    buf.duration = self.duration
                    timestamp = self.number_frames * self.duration
                    buf.pts = buf.dts = int(timestamp)
                    buf.offset = timestamp
                    self.number_frames += 1
                    retval = src.emit('push-buffer', buf)
                    print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                                                                                        self.duration,
                                                                                        self.duration / Gst.SECOND))
                    if retval != Gst.FlowReturn.OK:
                        print(retval)

    def do_create_element(self, url):
        pipeline = Gst.parse_launch(self.launch_string)
        pipeline.set_state(Gst.State.PLAYING)
        return pipeline

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, video_device, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory(video_device)
        self.factory.set_shared(True)
        self.get_mount_points().add_factory("/stream2", self.factory)
        self.attach(None)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, default="0",
                        help="Video device for live stream")

    args = parser.parse_args()

    GObject.threads_init()
    Gst.init(None)

    server = GstServer(args.video)
    print("Running as - rtsp://127.0.0.1:8554/stream2")

    loop = GLib.MainLoop()
    loop.run()