import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from tkinter import *
from PIL import Image, ImageTk
import time
from collections import Counter
import bmi
# import board
# import busio as io
# import adafruit_mlx90614
from time import sleep
from hx711 import HX711
#import RPi.GPIO as GPIO
import threading

class DirectoryHelper:
    @staticmethod
    def get_current_working_directory():
        return os.getcwd()

class ButtonConfig():
    def __init__(self):
        self.bordercolor = "yellow"

    def create_button(self, swidth, sheight, w, x, y, text, bcolor, fcolor, cmd):
        def on_enter(e):
            mybutton['background'] = bcolor
            mybutton['foreground'] = fcolor

        def on_leave(e):
            mybutton['background'] = fcolor
            mybutton['foreground'] = bcolor

        mybutton = Button(w,
            borderwidth=3,
            highlightthickness=0,
            bd=3,
            highlightbackground=self.bordercolor,
            highlightcolor=self.bordercolor,
            relief="solid",
            height=sheight,
            width=swidth,
            text=text,
            font=("Arial", 15, "bold"),
            fg=bcolor,
            bg=fcolor,
            activebackground=bcolor,
            activeforeground=fcolor,
            command=cmd
        )

        mybutton.bind("<Enter>", on_enter)
        mybutton.bind("<Leave>", on_leave)
        mybutton.place(x=x, y=y, anchor="center")

class BMICalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.age = None
        self.gender = None
        self.height = None
        self.weight = None
        self.configure(bg="black")
        self.overrideredirect(1)
        self.window_init()
        self.preload_assets()
        self.show_start_screen()

    def window_init(self):
        self.geometry("800x450")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 800
        window_height = 450

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.directory = Path(DirectoryHelper.get_current_working_directory()) / "assets"
        
        # Use a single canvas for all content
        self.canvas = Canvas(
            bg="black",
            height=450,  
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

    def preload_assets(self):
        # Preload all GIFs and images
        self.background_image = self.load_image("frame.png")
        self.intro_gif_frames = self.load_gif("introduction.gif")
        self.height_gif_frames = self.load_gif("height.gif")
        self.weight_gif_frames = self.load_gif("weight.gif")
        self.temp_gif_frames = self.load_gif("temp.gif")

    def load_image(self, path: str):
        image_path = self.relative_to_assets(path)
        if image_path.exists():
            return ImageTk.PhotoImage(file=str(image_path))
        else:
            print(f"Error: {image_path} not found")
            return None

    def load_gif(self, gif_filename):
        gif_path = self.relative_to_assets(gif_filename)
        if gif_path.exists():
            gif_image = Image.open(str(gif_path))
            frames = []
            try:
                while True:
                    frame = ImageTk.PhotoImage(gif_image.copy().resize((800, 450)))
                    frames.append(frame)
                    gif_image.seek(len(frames))
            except EOFError:
                pass
            return frames
        else:
            print(f"Error: {gif_path} not found")
            return []

    def relative_to_assets(self, path: str) -> Path:
        return self.directory / path

    def show_gif(self, frames, duration_ms, callback=None, **kwargs):
        self.clear_canvas()
        if frames:
            self.gif_label = tk.Label(self, bd=0, relief="flat", bg="black")
            self.gif_label.place(x=0, y=0, bordermode="outside")
            self.animate_gif(frames, 0)
        if callback:
            self.after(duration_ms, lambda: callback(**kwargs))

    def animate_gif(self, frames, frame_index):
        if frames:
            frame = frames[frame_index]
            self.gif_label.config(image=frame)
            frame_index = (frame_index + 1) % len(frames)
            self.gif_callback = self.after(100, self.animate_gif, frames, frame_index)

    def show_start_screen(self):
        self.show_gif(self.intro_gif_frames, duration_ms=3000)
        btn = ButtonConfig()
        btn.create_button(10, 2, self, 400, 350, "START", "#A1E3F9", "#191414", self.show_selection_screen)

    def show_selection_screen(self):
        self.clear_canvas()
        btn = ButtonConfig()
        btn.create_button(20, 2, self, 400, 270, "WEIGHT", "#A1E3F9", "#191414", lambda: self.show_weight_intro(1))
        btn.create_button(20, 2, self, 400, 190, "HEIGHT", "#A1E3F9", "#191414", lambda: self.show_height_intro(1))
        btn.create_button(20, 2, self, 400, 110, "BMI", "#A1E3F9", "#191414", self.show_bmi_screen)
        btn.create_button(20, 2, self, 400, 350, "TEMPERATURE", "#A1E3F9", "#191414", self.show_temperature_intro)

    def clear_canvas(self):
        # Clear only the canvas content instead of destroying all widgets
        self.canvas.delete("all")
        if hasattr(self, 'gif_callback'):
            self.after_cancel(self.gif_callback)

    def show_bmi_screen(self):
        self.clear_canvas()
        self.age = None
        self.gender = None
        self.canvas.create_text(
            100.0,
            50.0,
            anchor="nw",
            text="Please enter your Age and Gender. Then press NEXT",
            fill="#3674B5",
            font=("Arial", 15, "bold")
        )
        self.entry_1 = Entry(
            bd=0,
            bg="#191414",
            fg="#A1E3F9",
            highlightthickness=0,
            font=("Arial", 20, "bold"),
            borderwidth=3,
            relief="solid",
            justify="center"
        )

        self.error_label = Label(
        text="",
        font=("Arial", 12),
        fg="red",
        bg="#191414"
        )
        self.error_label.place(x=450, y=150)
        btn_y = 190
        btn_x = 120

        self.entry_1.place(
            x=150,
            y=90,
            width=405.0,
            height=50.0
        )

        btn = ButtonConfig()
        btn.create_button(4, 2, self, btn_x, btn_y, "7", "#A1E3F9", "#191414", lambda: self.number_pressed(7))
        btn.create_button(4, 2, self, btn_x, btn_y + 70, "4", "#A1E3F9", "#191414", lambda: self.number_pressed(4))
        btn.create_button(4, 2, self, btn_x, btn_y + 140, "1", "#A1E3F9", "#191414", lambda: self.number_pressed(1))
        btn.create_button(4, 2, self, btn_x + 85, btn_y + 140, "2", "#A1E3F9", "#191414", lambda: self.number_pressed(2))
        btn.create_button(4, 2, self, btn_x + 85, btn_y + 70, "5", "#A1E3F9", "#191414", lambda: self.number_pressed(5))
        btn.create_button(4, 2, self, btn_x + 85, btn_y, "8", "#A1E3F9", "#191414", lambda: self.number_pressed(8))
        btn.create_button(4, 2, self, btn_x + 170, btn_y + 140, "3", "#A1E3F9", "#191414", lambda: self.number_pressed(3))
        btn.create_button(4, 2, self, btn_x + 170, btn_y + 70, "6", "#A1E3F9", "#191414", lambda: self.number_pressed(6))
        btn.create_button(4, 2, self, btn_x + 170, btn_y, "9", "#A1E3F9", "#191414", lambda: self.number_pressed(9))
        btn.create_button(4, 2, self, btn_x + 255, btn_y, "0", "#A1E3F9", "#191414", lambda: self.number_pressed(0))
        btn.create_button(4, 5, self, btn_x + 255, btn_y + 105, "C", "#A1E3F9", "#191414", self.clear_entry)
        btn.create_button(10, 2, self, btn_x + 590, btn_y + 205, "NEXT", "#A1E3F9", "#191414", self.save_age)
        btn.create_button(7, 5, self, btn_x + 390, btn_y + 75, "MALE", "#A1E3F9", "#191414", lambda: self.select_gender('male'))
        btn.create_button(7, 5, self, btn_x + 490, btn_y + 75, "FEMALE", "#A1E3F9", "#191414", lambda: self.select_gender('female'))

    def number_pressed(self, number):
        current_value = self.entry_1.get()
        if not str(number).isdigit():
            return
        if current_value != "" and int(current_value + str(number)) > 120:
            return
        if current_value == "0" and str(number) == "0":
            return
        new_value = current_value + str(number)
        if 1 <= int(new_value) <= 120:
            self.entry_1.delete(0, 'end')
            self.entry_1.insert(0, new_value)
        else:
            return

    def clear_entry(self):
        self.entry_1.delete(0, 'end')
        self.age = None

    def show_height_intro(self, parameter):
        self.show_gif(self.height_gif_frames, duration_ms=3000, callback=self.show_height_gathering, parameter=parameter)

    def show_height_gathering(self, parameter):
        self.clear_canvas()
        self.gathering_label = tk.Label(self, text="Waiting for the sensor to settle", font=("Arial", 20, "bold"), bg="#A1E3F9", fg="black")
        self.gathering_label.pack(pady=150)
        TRIG = 23
        ECHO = 24
        SPEED_OF_SOUND = 34300
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.output(TRIG, False)

        def measure_distance():
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()

            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * SPEED_OF_SOUND) / 2
            return round(distance, 2)

        def gather_data():
            results = []
            for _ in range(5):
                distance = measure_distance()
                if distance >= 214:
                    continue
                results.append(distance)
                time.sleep(0.00001)

            integer_results = [int(d) for d in results]
            counter = Counter(integer_results)
            valid_integers = [k for k, v in counter.items() if v >= 2]

            if valid_integers:
                selected_integer = valid_integers[0]
                filtered_results = [d for d in results if int(d) == selected_integer]
                average_distance = round(sum(filtered_results) / len(filtered_results), 2)
                if 40 <= average_distance <= 200:
                    height = 214.16 - average_distance
                    self.after(4000, lambda: self.show_height_display(parameter, height))
                    GPIO.cleanup()
            else:
                print("No valid measurement found. Retrying...")
                self.after(1000, gather_data)  # Retry gathering data after 1 second

        threading.Thread(target=gather_data).start()  # Start gathering the data in a separate thread

    def show_weight_gathering(self, parameter):
        self.clear_canvas()
        self.gathering_label = tk.Label(self, text="Gathering weight information...", font=("Arial", 20, "bold"), bg="#A1E3F9", fg="black")
        self.gathering_label.pack(pady=150)
        val = hx.get_weight(5)
        self.animate_text("weight")
        weight = f"{val:.2f}" # Use the calculated average weight
        self.after(3000, lambda: self.show_weight_display(parameter, weight))

    def animate_text(self, weight_height):
        if weight_height == "weight":
            extra_text = "Stay Still"
        elif weight_height == "height":
            extra_text = "Stand straight"
        texts = [
            "Gathering information.",
            "Gathering information. Please wait...",
            f"Gathering information. Please wait... {extra_text}..."
        ]
        def update_text(index):
            if index < len(texts):
                self.gathering_label.config(text=texts[index])
                self.after(1000, update_text, index + 1)
        update_text(0)

    def show_weight_intro(self, parameter):
        self.show_gif(self.weight_gif_frames, duration_ms=3000, callback=self.show_weight_gathering, parameter=parameter)

    def show_weight_display(self, parameter, weight):
        self.clear_canvas()
        self.gathering_label = tk.Label(self, text="Weight received...", font=("Arial", 20, "bold"), bg="#A1E3F9", fg="black")
        self.gathering_label.pack(pady=250)
        self.weight = weight
        weight_label = tk.Label(self, text=f"{weight}kg", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#A1E3F9", fg="black")
        weight_label.place(x=390, y=180, anchor="center") 
        if parameter == 1:
            self.after(3000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#A1E3F9", "#191414", self.show_bmi_calculation)

    def show_bmi_calculation(self):
        self.clear_canvas()
        _label = tk.Label(self, text=f"BMI = {self.weight}kg / ({self.height}cm)²", font=("Arial", 50, "bold"), padx=30, pady=15, bg="#A1E3F9", fg="black")
        _label.place(x=400, y=180, anchor="center")
        self.after(2000, self.show_bmi_result)

    def show_bmi_result(self):
        self.clear_canvas()
        bmi_value,status = bmi.bmi(self.age,self.gender,self.height,self.weight)
        _label = tk.Label(self, text=f"Your BMI is: {bmi_value:.2f}\nAge: {self.age}\nGender: {self.gender}", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#A1E3F9", fg="black")
        _label.place(x=400, y=180, anchor="center")
        _label_result = tk.Label(self, text=f"{status}", font=("Arial", 25, "bold"), padx=50, pady=15, bg="#A1E3F9", fg="black")
        _label_result.place(x=400, y=180, anchor="center")
        self.after(3000, lambda: self.show_start_screen())

    def show_height_display(self, parameter, height):
        self.clear_canvas()
        self.gathering_label = tk.Label(self, text="Height received...", font=("Arial", 20, "bold"), bg="#A1E3F9", fg="black")
        self.gathering_label.pack(pady=150)
        height_value = float(height)
        height_label = tk.Label(self, text=f"{height_value:.2f} cm", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#A1E3F9", fg="black")
        height_label.place(x=390, y=180, anchor="center") 
        self.height = f"{height_value:.2f}"
        if parameter == 1:
            self.after(3000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#A1E3F9", "#191414", lambda: self.show_weight_intro(parameter))

    def show_temperature_intro(self):
        self.show_gif(self.temp_gif_frames, duration_ms=3000, callback=self.show_temp_gathering)

    def show_temp_gathering(self):
        self.clear_canvas()
        i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
        mlx = adafruit_mlx90614.MLX90614(i2c)
        self.gathering_label = tk.Label(self, text="TEMPERATURE", font=("Arial", 20, "bold"), bg="#A1E3F9", fg="black")
        self.gathering_label.pack(pady=190)
        newtargetTemp = 0.9844 * mlx.object_temperature + 3.8967
        print("Target Temperature: {:.2f} °C".format(newtargetTemp))
        temp_label = tk.Label(self, text="{:.2f} °C".format(newtargetTemp), font=("Arial", 50, "bold"), padx=50, pady=15, bg="#A1E3F9", fg="black")
        temp_label.place(x=390, y=180, anchor="center")
        self.after(3000, lambda: self.show_start_screen())

    def check_enable_next_button(self):
        if self.age is None and self.gender is None:
            self.error_label.config(text="Please enter a valid age and select gender")
            return False
        elif self.age is None:
            self.error_label.config(text="Please enter a valid age")
            return False
        elif self.gender is None:
            self.error_label.config(text="Please select gender")
            return False
        else:
            self.error_label.config(text="")
            return True

    def save_age(self):
        try:
            self.age = int(self.entry_1.get())
            check_if_enabled = self.check_enable_next_button()
            if check_if_enabled:
                self.show_height_intro(0)
        except ValueError:
            if not self.gender:
                self.error_label.config(text="Please select gender")
            if hasattr(self, 'error_label'):
                self.error_label.config(text="Please enter a valid age.")

    def select_gender(self, gender):
        try:
            self.gender = gender
            self.age = int(self.entry_1.get())
            print(f"Gender selected: {self.gender}") 
            check_if_enabled = self.check_enable_next_button()
            if check_if_enabled:
                self.show_height_intro(0)
        except ValueError:
            if not self.gender:
                self.error_label.config(text="Please select gender")
            if hasattr(self, 'error_label'):
                self.error_label.config(text="Please enter a valid age.")

if __name__ == "__main__":
    hx = HX711(5, 6)
    referenceUnit = 114
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()

    app = BMICalculator()
    app.mainloop()