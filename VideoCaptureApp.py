import tkinter as tk
import traceback
from tkinter.filedialog import asksaveasfilename

import cv2
from PIL import Image, ImageTk
from pygrabber.dshow_graph import FilterGraph


class VideoCaptureApp:
    def __init__(self):
        self.root = tk.Tk()
        self.app = tk.Frame(self.root, bg="white")
        self.app.grid()
        self.feed = tk.Label(self.app)
        self.feed.grid(row=0, column=0, columnspan=3)

        self.graph = FilterGraph()
        self.camera_devices = self.graph.get_input_devices()

        self.selected_cam = tk.StringVar(self.root)
        self.selected_cam.set(self.camera_devices[0])
        self.selected_cam.trace("w", self.switch_camera_feed)

        self.cam_menu = tk.OptionMenu(
            self.app, self.selected_cam, *self.camera_devices)
        self.cam_menu.grid(row=1, column=0)

        self.cam_name = self.selected_cam.get()
        self.root.title(self.cam_name)
        self.cam_index = self.camera_devices.index(self.cam_name)
        self.cap = cv2.VideoCapture(self.cam_index)

        self.refresh_cams_button = tk.Button(
            self.app, text="Refresh Cameras", command=self.refresh_cameras)
        self.refresh_cams_button.grid(row=1, column=1)

        self.save_button = tk.Button(
            self.app, text="Save", command=self.save_frame)
        self.save_button.grid(row=1, column=2)

        tk.Tk.report_callback_exception = self.show_error

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
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.feed.imgtk = imgtk
        self.feed.configure(image=imgtk)
        self.feed.after(1, self.video_stream)

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
        tk.messagebox.showerror('Error', err)

    def run(self):
        self.video_stream()
        self.root.mainloop()


if __name__ == "__main__":
    app = VideoCaptureApp()
    app.run()
