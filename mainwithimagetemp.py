import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from tkinter import *
from PIL import Image, ImageTk
import time
from collections import Counter
import bmi

import board
import busio as io
import adafruit_mlx90614

from time import sleep
import RPi.GPIO as GPIO
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
        self.clear_window()
        self.window_init()
        self.show_start_screen()

    def window_init(self):
        self.geometry("800x400")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 800
        window_height = 400

        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.directory = Path(DirectoryHelper.get_current_working_directory()) / "assets"
        self.canvas = Canvas(
            bg="black",
            height=500,  
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Load a background image if available
        image_path = self.relative_to_assets("image_1.png")
        if image_path.exists():
            self.background_image = PhotoImage(file=str(image_path))
            self.canvas.create_image(
                400.0,  
                200.0,  
                image=self.background_image
            )
        else:
            print(f"Error: {image_path} not found")

    def relative_to_assets(self, path: str) -> Path:
        return self.directory / path

    def show_gif(self, gif_filename, duration_ms, callback=None, **kwargs):
        """
        Display a GIF (or image) on the canvas for a certain duration.
        If the GIF is animated, it will loop automatically.
        After duration_ms milliseconds, callback() is invoked if provided.
        """
        self.clear_window()
        self.window_init()
        gif_path = self.relative_to_assets(gif_filename)
        if gif_path.exists():
            self.gif_image = Image.open(str(gif_path))
            self.frames = []
            try:
                while True:
                    frame = ImageTk.PhotoImage(self.gif_image.copy().resize((800,400)))
                    self.frames.append(frame)
                    self.gif_image.seek(len(self.frames)) 
            except EOFError:
                pass 

            self.gif_label = tk.Label(self, bd=0, relief="flat", bg="black")
            self.gif_label.place(x=0, y=0, bordermode="outside")

            self.animate_gif(0)
        else:
            print(f"Error: {gif_path} not found")
        
        if callback:
         
            self.after(duration_ms, lambda: callback(**kwargs))


    def animate_gif(self, frame_index):
        if not hasattr(self, 'frames') or not self.frames:
            return
        try:
            frame = self.frames[frame_index]
            self.gif_label.config(image=frame)
            frame_index = (frame_index + 1) % len(self.frames)
            self.gif_callback = self.after(100, self.animate_gif, frame_index)
        except tk.TclError:
            return

    def show_start_screen(self):
        self.show_gif("start11.gif", duration_ms=5000)
        btn = ButtonConfig()
        my_label = tk.Label()
        my_label.pack(padx=4, pady=25)
        btn.create_button(10, 2, self, 400, 350, "START", "#1DB954", "#191414", self.show_intro_screen)

    def show_intro_screen(self):
        self.show_gif("start10.gif", duration_ms=5000, callback=self.show_selection_screen)

    def show_selection_screen(self):
        self.clear_window()
        self.window_init()

        btn = ButtonConfig()
        btn.create_button(20, 2, self, 400, 240, "WEIGHT", "#1DB954", "#191414", lambda: self.show_weight_intro(1))
        btn.create_button(20, 2, self, 400, 160, "HEIGHT", "#1DB954", "#191414", lambda: self.show_height_intro(1))
        btn.create_button(20, 2, self, 400, 80, "BMI", "#1DB954", "#191414", self.show_bmi_screen)
        btn.create_button(20, 2, self, 400, 320, "TEMPERATURE", "#1DB954", "#191414", self.show_temperature_intro)

    def show_bmi_screen(self):
        self.clear_window()
        self.window_init()
        self.age = None
        self.gender = None
        self.canvas.create_text(
            150.0,
            30.0,
            anchor="nw",
            text="Please enter your Age and Gender. Then press NEXT",
            fill="#1DB954",
            font=("Arial", 15, "bold")
        )
        self.entry_1 = Entry(
            bd=0,
            bg="#191414",
            fg="#1DB954",
            highlightthickness=0,
            font=("Arial", 20, "bold"),
            borderwidth=3,
            relief="solid",
            justify="center"
        )
        btn_y = 160
        btn_x = 120

        self.entry_1.place(
            x=200,
            y=60,
            width=405.0,
            height=50.0
        )

        btn = ButtonConfig()
        btn.create_button(5, 2, self, btn_x, btn_y, "7", "#1DB954", "#191414", lambda: self.number_pressed(7))
        btn.create_button(5, 2, self, btn_x, btn_y + 70, "4", "#1DB965", "#191414", lambda: self.number_pressed(4))
        btn.create_button(5, 2, self, btn_x, btn_y + 140, "1", "#1DB965", "#191414", lambda: self.number_pressed(1))
        btn.create_button(5, 2, self, btn_x + 74, btn_y + 140, "2", "#1DB965", "#191414", lambda: self.number_pressed(2))
        btn.create_button(5, 2, self, btn_x + 74, btn_y + 70, "5", "#1DB954", "#191414", lambda: self.number_pressed(5))
        btn.create_button(5, 2, self, btn_x + 74, btn_y, "8", "#1DB954", "#191414", lambda: self.number_pressed(8))
        btn.create_button(5, 2, self, btn_x + 148, btn_y + 140, "3", "#1DB954", "#191414", lambda: self.number_pressed(3))
        btn.create_button(5, 2, self, btn_x + 148, btn_y + 70, "6", "#1DB954", "#191414", lambda: self.number_pressed(6))
        btn.create_button(5, 2, self, btn_x + 148, btn_y, "9", "#1DB954", "#191414", lambda: self.number_pressed(9))
        btn.create_button(5, 2, self, btn_x + 222, btn_y, "0", "#1DB954", "#191414", lambda: self.number_pressed(0))
        btn.create_button(5, 5, self, btn_x + 222, btn_y + 105, "C", "#1DB954", "#191414", self.clear_entry)
        btn.create_button(10, 2, self, btn_x + 550, btn_y + 105, "NEXT", "#1DB954", "#191414", self.save_age)
        btn.create_button(5, 5, self, btn_x + 350, btn_y + 105, "MALE", "#1DB954", "#191414", lambda: self.select_gender('male'))
        btn.create_button(5, 5, self, btn_x + 430, btn_y + 105, "FEMALE", "#1DB954", "#191414", lambda: self.select_gender('female'))

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

    def show_height_intro(self, parameter):
        # Show a GIF for height intro
        self.show_gif("height.gif", duration_ms=5000, callback=self.show_height_gathering, parameter=parameter)

    def show_height_gathering(self, parameter):
        self.clear_window()
        self.window_init()
        self.gathering_label = tk.Label(self, text="Waiting for the sensor to settle", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=150)
        time.sleep(2)
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
        
    
        # Wait until distance is below a threshold
        while True:
            distance = measure_distance()
            if distance <= 200:
                break
            print(f"Distance {distance} cm is too large. Retrying...")
            time.sleep(1)

        self.gathering_label.config(text="Gathering information...")
        while True:
            results = []
            for _ in range(5):
                distance = measure_distance()
                results.append(distance)
                print(f"Measurement {len(results)}: {distance} cm")
                time.sleep(1)

            integer_results = [int(d) for d in results]
            counter = Counter(integer_results)
            valid_integers = [k for k, v in counter.items() if v >= 2]

            if valid_integers:
                selected_integer = valid_integers[0]
                filtered_results = [d for d in results if int(d) == selected_integer]
                average_distance = round(sum(filtered_results) / len(filtered_results), 2)
                print(f"Average distance for integer {selected_integer}: {average_distance} cm")
                print(f"height: {213.16 - average_distance} cm")
                GPIO.cleanup()
                self.animate_text("height")
                imp_height = 213.16 - average_distance
                self.after(4000, lambda: self.show_height_display(parameter, imp_height))
                break  
            else:
                print("No two measurements share the same integer. Re-gathering...")

    def show_weight_gathering(self, parameter):
        self.clear_window()
        self.window_init()
        self.gathering_label = tk.Label(self, text="Gathering weight information...", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=150)
        self.animate_text("weight")
        weight = 30
        self.after(6000, lambda: self.show_weight_display(parameter, weight))

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
        self.show_gif("weight.gif", duration_ms=5000, callback=self.show_weight_gathering, parameter=parameter)

    def show_weight_display(self, parameter, weight):
        self.clear_window()
        self.window_init()  
        self.gathering_label = tk.Label(self, text="Weight received...", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=250)
        self.weight = weight
        weight_label = tk.Label(self, text=f"{weight}kg", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        weight_label.place(x=390, y=180, anchor="center") 
        if parameter == 1:
            self.after(5000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#1DB954", "#191414", self.show_bmi_calculating)

    def show_bmi_calculating(self):
        self.show_gif("guide.gif", duration_ms=5000, callback=self.show_bmi_calculation)

    def show_bmi_calculation(self):
        self.clear_window()
        self.window_init()
        _label = tk.Label(self, text=f"BMI = {self.weight}kg / ({self.height}cm)²", font=("Arial", 50, "bold"), padx=30, pady=15, bg="#1DB954", fg="black")
        _label.place(x=400, y=180, anchor="center") 
        self.after(3000, self.show_bmi_result)

    def show_bmi_result(self):
        self.clear_window()
        self.window_init()
        bmi_value = float(self.weight) / (float(self.height) ** 2)
        print(self.weight)
        print(self.height)
        bmi_result = bmi.classify_bmi(bmi_value, self.age, self.gender)
        _label = tk.Label(self, text=f"Your BMI is: {bmi_value:.2f}\nAge: {self.age}\nGender: {self.gender}", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        _label.place(x=400, y=180, anchor="center") 
        _label_result = tk.Label(self, text=f"{bmi_result}", font=("Arial", 25, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        _label_result.place(x=400, y=180, anchor="center")
        self.after(5000, lambda: self.show_start_screen())
        
    def show_height_display(self, parameter, height):
        self.clear_window()
        self.window_init()  
        self.gathering_label = tk.Label(self, text="Height received...", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=150)
        height_value = float(height)
        height_label = tk.Label(self, text=f"{height_value:.2f} cm", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        height_label.place(x=390, y=180, anchor="center") 
        self.height = f"{height_value:.2f}"
        if parameter == 1:
            self.after(5000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#1DB954", "#191414", lambda: self.show_weight_intro(parameter))

    def show_temperature_intro(self):
        self.show_gif("temp.gif", duration_ms=5000, callback=self.show_temp_gathering)

    def show_temp_gathering(self):
        self.clear_window()
        self.window_init()
        i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
        mlx = adafruit_mlx90614.MLX90614(i2c)
        self.gathering_label = tk.Label(self, text="TEMPERATURE", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=190)
        sleep(2)
        ambientTemp = "{:.2f}".format(mlx.ambient_temperature)
        targetTemp = "{:.2f}".format(mlx.object_temperature)
        print("Ambient Temperature:", ambientTemp, "°C")
        print("Target Temperature:", targetTemp,"°C")
  
        temp_label = tk.Label(self, text=targetTemp+"°C", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        temp_label.place(x=390, y=180, anchor="center")
        self.after(5000, lambda: self.show_start_screen())

    def check_enable_next_button(self):
        if self.age is not None and self.gender is not None:
            return True
        else:
            print(self.age)
            print(self.gender)
            return False

    def save_age(self):
        try:
            self.age = int(self.entry_1.get())
            check_if_enabled = self.check_enable_next_button()
            if check_if_enabled:
                self.show_height_intro(0)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid age.")

    def select_gender(self, gender):
        self.gender = gender
        print(f"Gender selected: {self.gender}") 
        if self.check_enable_next_button():
            self.show_height_intro(0)
    def clear_window(self):
        # Cancel any pending callbacks if you stored them, e.g.,
        if hasattr(self, 'gif_callback'):
            self.after_cancel(self.gif_callback)
        for widget in self.winfo_children():
            widget.destroy()
if __name__ == "__main__":
    app = BMICalculator()
    
    app.overrideredirect(1)
    app.mainloop()
