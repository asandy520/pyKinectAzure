import os
import sys
import time
import json
import numpy as np
import pykinect_azure as pykinect
import threading

class SkeletonTracker:
    def __init__(self):
        self.event = threading.Event()

        # Initialize the library
        pykinect.initialize_libraries(track_body=True)

        # Start device
        self.device = pykinect.start_device()

        # Start body tracker
        self.body_tracker = pykinect.start_body_tracker()

        # Initialize buffers
        self.depth_buffer = []
        self.skeleton_buffer = []

    def save_skeleton_data(self, skeleton_data, save_dir):
        # Save skeleton data to JSON file
        filename = os.path.join(save_dir, f"{int(time.time_ns())}.json")
        with open(filename, "w") as f:
            json.dump(skeleton_data, f)

    def save_depth_image(self, depth_image, save_dir):
        # Save the depth image with timestamp as filename
        filename = os.path.join(save_dir, f"{int(time.time_ns())}.npy")
        np.save(filename, depth_image)

    def track_skeleton(self, save_dir):
        while True:
            # Get capture
            capture = self.device.update()

            # Get body tracker frame
            body_frame = self.body_tracker.update()

            # Get the depth image from the capture
            ret, depth_image = capture.get_depth_image()

            if not ret:
                continue

            # Get skeleton data
            skeletons = body_frame.json()

            # Add depth image and skeleton data to buffers
            self.depth_buffer.append(depth_image)
            self.skeleton_buffer.append(skeletons)

            if self.event.is_set():
                break

            if self.depth_buffer and self.skeleton_buffer:
                # Get the latest depth image and skeleton data
                depth_image = self.depth_buffer.pop(0)
                skeletons = self.skeleton_buffer.pop(0)

                # Save only if event is not set
                if not self.event.is_set():
                    # Threading to save JSON and NPY concurrently
                    threading.Thread(target=self.save_skeleton_data, args=(skeletons, save_dir)).start()
                    threading.Thread(target=self.save_depth_image, args=(depth_image, save_dir)).start()

    def stop_tracking(self):
        self.event.set()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python SkeletonTracker.py <save_dir>")
        sys.exit(1)

    save_dir = sys.argv[1]
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)
    tracker = SkeletonTracker()
    tracker.track_skeleton()