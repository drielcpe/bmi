import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from tkinter import *
from PIL import Image, ImageTk
import time
from collections import Counter
import bmi
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
        self.hide_mouse_cursor() 
        self.show_start_screen()
    def hide_mouse_cursor(self):
        # Hide the mouse cursor
        self.config(cursor="none")  
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
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        self.show_gif(self.intro_gif_frames, duration_ms=3000)
        btn = ButtonConfig()
        btn.create_button(10, 2, self, 400, 320, "START", "#211C84", "#ffffff", self.show_selection_screen)

    def show_selection_screen(self):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        btn = ButtonConfig()
        btn.create_button(20, 2, self, 400, 270, "WEIGHT", "#211C84", "#ffffff", lambda: self.show_weight_intro(1))
        btn.create_button(20, 2, self, 400, 190, "HEIGHT", "#211C84", "#ffffff", lambda: self.show_height_intro(1))
        btn.create_button(20, 2, self, 400, 110, "BMI", "#211C84", "#ffffff", self.show_bmi_screen)
        btn.create_button(20, 2, self, 400, 350, "TEMPERATURE", "#211C84", "#ffffff", self.show_temperature_intro)

    def clear_canvas(self):
        # Clear all widgets from the canvas
        for widget in self.winfo_children():
            if widget != self.canvas:  # Keep the canvas intact
                widget.destroy()
        self.canvas.delete("all")
        if hasattr(self, 'gif_callback'):
            self.after_cancel(self.gif_callback)

    def show_bmi_screen(self):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
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
            bg="#ffffff",
            fg="#211C84",
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
        bg="#ffffff"
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
        btn.create_button(4, 2, self, btn_x, btn_y, "7", "#211C84", "#ffffff", lambda: self.number_pressed(7))
        btn.create_button(4, 2, self, btn_x, btn_y + 70, "4", "#211C84", "#ffffff", lambda: self.number_pressed(4))
        btn.create_button(4, 2, self, btn_x, btn_y + 140, "1", "#211C84", "#ffffff", lambda: self.number_pressed(1))
        btn.create_button(4, 2, self, btn_x + 85, btn_y + 140, "2", "#211C84", "#ffffff", lambda: self.number_pressed(2))
        btn.create_button(4, 2, self, btn_x + 85, btn_y + 70, "5", "#211C84", "#ffffff", lambda: self.number_pressed(5))
        btn.create_button(4, 2, self, btn_x + 85, btn_y, "8", "#211C84", "#ffffff", lambda: self.number_pressed(8))
        btn.create_button(4, 2, self, btn_x + 170, btn_y + 140, "3", "#211C84", "#ffffff", lambda: self.number_pressed(3))
        btn.create_button(4, 2, self, btn_x + 170, btn_y + 70, "6", "#211C84", "#ffffff", lambda: self.number_pressed(6))
        btn.create_button(4, 2, self, btn_x + 170, btn_y, "9", "#211C84", "#ffffff", lambda: self.number_pressed(9))
        btn.create_button(4, 2, self, btn_x + 255, btn_y, "0", "#211C84", "#ffffff", lambda: self.number_pressed(0))
        btn.create_button(4, 5, self, btn_x + 255, btn_y + 105, "C", "#211C84", "#ffffff", self.clear_entry)
        btn.create_button(10, 2, self, btn_x + 590, btn_y + 205, "NEXT", "#211C84", "#ffffff", self.save_age)
        btn.create_button(7, 5, self, btn_x + 390, btn_y + 75, "MALE", "#211C84", "#ffffff", lambda: self.select_gender('male'))
        btn.create_button(7, 5, self, btn_x + 490, btn_y + 75, "FEMALE", "#211C84", "#ffffff", lambda: self.select_gender('female'))

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
        self.show_gif(self.height_gif_frames, duration_ms=4500, callback=self.show_height_gathering, parameter=parameter)

    def show_height_gathering(self, parameter):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        self.gathering_label = tk.Label(self, text="Height received...", font=("Arial", 20, "bold"), bg="#211C84", fg="#ffffff")
        self.gathering_label.pack(pady=150)
        # Hardcoded height value
        height = 175.0  # Example height in cm
        self.height = f"{height:.2f}"
        self.after(2000, lambda: self.show_height_display(parameter, height))

    def show_weight_gathering(self, parameter):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        self.gathering_label = tk.Label(self, text="Weight received...", font=("Arial", 20, "bold"), bg="#211C84", fg="#ffffff")
        self.gathering_label.pack(pady=150)
        # Hardcoded weight value
        weight = 70.5  # Example weight in kg
        self.weight = f"{weight:.2f}"
        self.after(2000, lambda: self.show_weight_display(parameter, weight))

    def show_weight_intro(self, parameter):
        self.show_gif(self.weight_gif_frames, duration_ms=5000, callback=self.show_weight_gathering, parameter=parameter)

    def show_weight_display(self, parameter, weight):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        self.gathering_label = tk.Label(self, text="Weight received...", font=("Arial", 20, "bold"), bg="#211C84", fg="#ffffff")
        self.gathering_label.pack(pady=250)
        weight_label = tk.Label(self, text=f"{weight}kg", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#211C84", fg="#ffffff")
        weight_label.place(x=390, y=180, anchor="center") 
        if parameter == 1:
            self.after(3000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#211C84", "#ffffff", self.show_bmi_calculation)

    def show_bmi_calculation(self):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        _label = tk.Label(self, text=f"BMI = {self.weight}kg / ({self.height}cm)²", font=("Arial", 35, "bold"), padx=30, pady=15, bg="#211C84", fg="#ffffff")
        _label.place(x=400, y=180, anchor="center")
        self.after(2000, self.show_bmi_result)

    def show_bmi_result(self):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        bmi_value, status = bmi.bmi(self.age, self.gender, float(self.height), float(self.weight))
        _label = tk.Label(self, text=f"BMI is: {bmi_value:.2f}\nAge: {self.age}\nGender: {self.gender}", font=("Arial", 25, "bold"), padx=50, pady=15, bg="#211C84", fg="#ffffff")
        _label.place(x=350, y=180, anchor="center")
        _label_result = tk.Label(self, text=f"{status}", font=("Arial", 25, "bold"), padx=50, pady=15, bg="#211C84", fg="#ffffff")
        _label_result.place(x=350, y=300, anchor="center")
        self.after(3000, lambda: self.show_start_screen())

    def show_height_display(self, parameter, height):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        self.gathering_label = tk.Label(self, text="Height received...", font=("Arial", 20, "bold"), bg="#211C84", fg="#ffffff")
        self.gathering_label.pack(pady=150)
        height_label = tk.Label(self, text=f"{height:.2f} cm", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#211C84", fg="#ffffff")
        height_label.place(x=390, y=180, anchor="center") 
        if parameter == 1:
            self.after(3000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#211C84", "#ffffff", lambda: self.show_weight_intro(parameter))

    def show_temperature_intro(self):
        self.show_gif(self.temp_gif_frames, duration_ms=4000, callback=self.show_temp_gathering)

    def show_temp_gathering(self):
        self.clear_canvas()
        # Display background image
        self.canvas.create_image(400, 225, image=self.background_image)
        # Hardcoded temperature value
        temperature = 36.5  # Example temperature in °C
        self.gathering_label = tk.Label(self, text="TEMPERATURE", font=("Arial", 20, "bold"), bg="#211C84", fg="#ffffff")
        self.gathering_label.pack(pady=190)
        temp_label = tk.Label(self, text=f"{temperature:.2f} °C", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#211C84", fg="#ffffff")
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
    app = BMICalculator()
    app.mainloop()