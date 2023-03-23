import tkinter as tk
import traceback
from tkinter.filedialog import asksaveasfilename

import cv2
from PIL import Image, ImageTk
from pygrabber.dshow_graph import FilterGraph


class VideoCaptureApp:
    def __init__(self, camera_devices):
        self.root = tk.Tk()
        self.app = tk.Frame(self.root, bg="white")
        self.app.grid()
        self.feed = tk.Label(self.app)
        self.feed.grid(row=0, column=0, columnspan=4)

        self.camera_devices = camera_devices

        self.selected_cam = tk.StringVar(self.root)
        self.selected_cam.set(self.camera_devices[0])
        self.selected_cam.trace("w", self.switch_camera_feed)

        # Camera selection drop-down
        self.cam_menu = tk.OptionMenu(
            self.app, self.selected_cam, *self.camera_devices)
        self.cam_menu.grid(row=1, column=0)

        # Camera capture initialisation
        self.cam_name = self.selected_cam.get()
        self.root.title(self.cam_name)
        self.cam_index = self.camera_devices.index(self.cam_name)
        self.cap = cv2.VideoCapture(self.cam_index)

        # Refresh button
        self.refresh_cams_button = tk.Button(
            self.app, text="Refresh Cameras", command=self.refresh_cameras)
        self.refresh_cams_button.grid(row=1, column=1)

        # Save button
        self.save_button = tk.Button(
            self.app, text="Save", command=self.save_frame)
        self.save_button.grid(row=1, column=2)

        # Center lines button
        self.save_button = tk.Button(
            self.app, text="Center Lines", command=self.show_centerlines)
        self.save_button.grid(row=1, column=3)

        self.centerlines = False

        tk.Tk.report_callback_exception = self.show_error

    def show_centerlines(self):
        self.centerlines = 1 - self.centerlines

    def draw_centerlines(self, cv2image):
        width, height, _ = cv2image.shape
        halfwidth = width//2
        halfheight = height//2
        line1start = (0, halfwidth)
        line1end = (height, halfwidth)
        line2start = (halfheight, 0)
        line2end = (halfheight, width)
        color = (255, 255, 255)
        cv2image = cv2.line(cv2image, line1start, line1end, color, 1)
        cv2image = cv2.line(cv2image, line2start, line2end, color, 1)
        return cv2image

    def refresh_cameras(self, *args):
        self.camera_devices = self.graph.get_input_devices()
        self.cam_menu = tk.OptionMenu(
            self.app, self.selected_cam, *self.camera_devices)
        self.cam_menu.grid(row=1, column=0)

    def switch_camera_feed(self, *args):
        self.cam_name = self.selected_cam.get()
        self.root.title(self.cam_name)
        self.cam_index = self.camera_devices.index(self.cam_name)
        self.cap.release()
        self.cap.open(self.cam_index)

    def video_stream(self):
        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        if self.centerlines:
            cv2image = self.draw_centerlines(cv2image)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.feed.imgtk = imgtk
        self.feed.configure(image=imgtk)
        self.feed.after(1000//60, self.video_stream)

    def save_frame(self):
        file_path = asksaveasfilename(
            initialfile='image.png',
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")]
        )
        if file_path:
            _, frame = self.cap.read()
            cv2.imwrite(file_path, frame)

    def show_error(self, *args):
        err = traceback.format_exception(*args)
        for line in err:
            print(line)
        exit()
        # tk.messagebox.showerror('Error', err)

    def run(self):
        self.video_stream()
        self.root.mainloop()


if __name__ == "__main__":
    graph = FilterGraph()
    try:
        camera_devices = graph.get_input_devices()
    except ValueError as e:
        tk.messagebox.showerror('Error', "No camera device detected.")
    app = VideoCaptureApp(camera_devices)
    app.run()
