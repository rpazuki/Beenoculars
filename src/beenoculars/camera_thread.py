import logging
import threading

log = logging.getLogger(__name__)


class CaptureThreadGlobals:
    stop = False
    frame = None


lock_condition = threading.Condition()


class CaptureThread(threading.Thread):
    """A separate thread for capturing images from the camera."""

    def __init__(self, capture):
        threading.Thread.__init__(self)
        self.capture = capture

    def run(self):
        """Continuously captures frames from the video source until stopped.
        This method acquires a lock before reading a frame from the video capture
        device to ensure thread safety. It releases the lock immediately after
        reading the frame. The loop continues to capture frames as long as the
        capture is successful and the global 'stop' flag is not set.

        Globals:
            stop (bool): A flag to stop the frame capturing loop.
            frame (numpy.ndarray): The latest captured frame.

        Raises:
            RuntimeError: If the video capture device fails to read a frame.
        """
        # global stop, frame
        lock_condition.acquire()
        success, frame = self.capture.read()
        CaptureThreadGlobals.frame = frame
        lock_condition.release()
        try:
            # while success and not stop:
            while success and not CaptureThreadGlobals.stop:
                # sleep(.1)
                lock_condition.acquire()
                success, frame = self.capture.read()
                CaptureThreadGlobals.frame = frame
                lock_condition.release()
        except RuntimeError as e:
            log.error("CaptureThread:run: Could not read frame from camera. %s" % e)
