import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from tkinter import *
from PIL import Image, ImageTk
import cv2
from tkvideo import tkvideo
import cv2
from PIL import Image, ImageTk
import bmi
import height

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


        self.title("BMI Calculator")
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
            height=400,  
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

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

    def stop_video(self):
        if hasattr(self, 'cap') and self.cap is not None:
            if self.cap.isOpened():
                self.cap.release()
            self.cap = None 
            print("Video stopped successfully.")

    def show_start_screen(self):
        self.stop_video()
        self.clear_window()
        self.window_init() 
        video_path = self.relative_to_assets("start11.mp4")  
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")  
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.updates_video()
        else:
            print(f"Error: {video_path} not found")

        btn = ButtonConfig()
        my_label = tk.Label()
        my_label.pack(padx=4, pady=25)
        btn.create_button(10, 2, self, 400, 350, "START", "#1DB954", "#191414", self.show_intro_screen)

    def show_intro_screen(self):
        self.clear_window()
        self.window_init()
        video_path = self.relative_to_assets("start10.mp4")  
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")  
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.update_video()
           
        else:
            print(f"Error: {video_path} not found")
        video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.after(video_duration * 700, self.show_selection_screen)  

    def update_video(self):
        if not hasattr(self, "video_label") or not self.video_label.winfo_exists():
            print("Label no longer exists, stopping update.")
            return 
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(frame)
                self.video_label.config(image=frame)
                self.video_label.image = frame 
                self.after(30, self.update_video)
            else:
                print("Video ended, stopping...")
                self.stop_video()  
        else:
            print("Video capture not initialized or already stopped.")

    def updates_video(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                if hasattr(self, 'video_label') and self.video_label.winfo_exists():
                    self.video_label.config(image=img)
                    self.video_label.image = img
                self.after(30, self.updates_video)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.updates_video()
        else:
            print("Error: Video capture is not available or initialized.")

    def show_selection_screen(self):
        self.clear_window()
        self.window_init()

        btn = ButtonConfig()
        btn.create_button(20,2,self,400, 240, "WEIGHT", "#1DB954", "#191414", lambda : self.show_weight_intro(1))
        btn.create_button(20,2,self,400, 160, "HEIGHT", "#1DB954", "#191414", lambda : self.show_height_intro(1))
        btn.create_button(20,2,self,400, 80, "BMI", "#1DB954", "#191414", self.show_bmi_screen)
        btn.create_button(20,2,self,400, 320, "TEMPERATURE", "#1DB954", "#191414", self.show_temperature_intro)

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
        btn_y =  160
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
        btn.create_button(10, 2, self, btn_x + 550, btn_y + 105, "NEXT", "#1DB954", "#191414",self.save_age)
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

    def show_height_intro(self,parameter):
        self.clear_window()
        self.window_init()
        video_path = self.relative_to_assets("height.mp4")  
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")  
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.update_video()
           
        else:
            print(f"Error: {video_path} not found")
        video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.after(video_duration * 700, lambda: self.show_height_gathering(parameter))  

    def show_height_gathering(self,parameter):
        self.clear_window()
        self.window_init()
        self.gathering_label = tk.Label(self, text="Gathering information...", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=150)
        self.animate_text("height")
        #python to get height
        imp_height = height.gather_height()
        self.after(4000, lambda: self.show_height_display(parameter,imp_height))

    def show_weight_gathering(self,parameter):
        self.clear_window()
        self.window_init()
        self.gathering_label = tk.Label(self, text="Gathering information...", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=150)
        self.animate_text("weight")
        #function to get weight
        weight = 30
        self.after(6000, lambda: self.show_weight_display(parameter,weight))

    def animate_text(self,weight_height):
        if weight_height == "weight":
            weight_height = "Stay Still"
        elif weight_height == "height":
            weight_height = "Stand straight"
        texts = [
            "Gathering information.",
            "Gathering information. Please wait...",
            f"Gathering information. Please wait... {weight_height}..."
        ]
        def update_text(index):
            if index < len(texts):
                self.gathering_label.config(text=texts[index])
                self.after(1000, update_text, index + 1)
        update_text(0)

    def show_weight_intro(self,parameter):
        self.clear_window()
        self.window_init()
        video_path = self.relative_to_assets("weight.mp4")
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.update_video()
        else:
            print(f"Error: {video_path} not found")
        video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.after(video_duration * 700, lambda: self.show_weight_gathering(parameter))

    def show_weight_display(self,parameter,weight):
        self.clear_window()
        self.window_init()  # Initialize the window
        self.gathering_label = tk.Label(self, text="Weight received..", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=250)
        self.weight =weight
        weight_label = tk.Label(self, text=f"{weight}kg", font=("Arial", 50, "bold"), padx=50,pady=15, bg="#1DB954", fg="black")
        weight_label.place(x=390, y=180, anchor="center") 

        if parameter == 1:
            self.after(5000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#1DB954", "#191414", self.show_bmi_calculating)

    def show_bmi_calculating(self):
        self.clear_window()
        self.window_init()
        video_path = self.relative_to_assets("guide.mp4")
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.update_video()
        else:
            print(f"Error: {video_path} not found")
        video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.after(video_duration * 800, self.show_bmi_calculation)

    def show_bmi_calculation(self):
        self.clear_window()
        self.window_init()

        _label = tk.Label(self, text=f"BMI = {self.weight}kg / ({self.height}m)²", font=("Arial", 50, "bold"), padx=30,pady=15, bg="#1DB954", fg="black")
        _label.place(x=400, y=180, anchor="center") 
        self.after(3000,self.show_bmi_result)

    def show_bmi_result(self):
        self.clear_window()
        self.window_init()
        bmi_value = float(self.weight) / (float(self.height) ** 2)

        print(self.weight)
        print(self.height)
        bmi_result =bmi.classify_bmi(bmi_value,self.age,self.gender)

       
        _label = tk.Label(self, text=f"Your BMI is: {bmi_value:.2f}\nAge: {self.age}\nGender: {self.gender}", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        _label.place(x=400, y=180, anchor="center") 
        _label_result = tk.Label(self, text=f"{bmi_result}", font=("Arial", 25, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")
        _label_result.place(x=400, y=180, anchor="center")
       

        self.after(5000, lambda: self.show_start_screen())
        
    def show_height_display(self,parameter,height):
        self.clear_window()
        self.window_init()  
        self.gathering_label = tk.Label(self, text="Height received..", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=250)
        height_label = tk.Label(self, text=f"{height:.2f}m", font=("Arial", 50, "bold"), padx=50, pady=15, bg="#1DB954", fg="black")

        height_label.place(x=390, y=180, anchor="center") 
        self.height = f"{height:.2f}"
        if parameter == 1:
            self.after(5000, lambda: self.show_start_screen())
        else:
            btn = ButtonConfig()
            btn.create_button(20, 2, self, 390, 300, "Next", "#1DB954", "#191414", lambda: self.show_weight_intro(parameter))

    def show_temperature_intro(self):
        self.clear_window()
        self.window_init()  
        video_path = self.relative_to_assets("temp.mp4")  
        if video_path.exists():
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_label = tk.Label(self, bd=0, relief="flat")  
            self.video_label.place(x=0, y=0, bordermode="outside")
            self.update_video()
        else:
            print(f"Error: {video_path} not found")
        video_duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.after(video_duration * 700,self.show_temp_gathering)  

    def show_temp_gathering(self):
        self.clear_window()
        self.window_init()
        self.gathering_label = tk.Label(self, text="TEMPERATURE", font=("Arial", 20, "bold"), bg="#1DB954", fg="black")
        self.gathering_label.pack(pady=190)

        weight_label = tk.Label(self, text="36.6", font=("Arial", 50, "bold"), padx=50,pady=15, bg="#1DB954", fg="black")
        weight_label.place(x=390, y=180, anchor="center")
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
        check_if_enabled = self.check_enable_next_button()
        if check_if_enabled:
            self.show_height_intro(0)

    def show_height_screen(self):
        self.clear_window()
        label = tk.Label(self, text="Enter your Height (in cm)", font=("Arial", 14), bg='black', fg='white')
        label.pack(pady=20)
        self.height_entry = tk.Entry(self)
        self.height_entry.pack(pady=10)
        next_button = tk.Button(self, text="Next", command=self.save_height)
        next_button.pack(pady=10)

    # def save_height(self):
    #     try:
    #         self.height = float(self.height_entry.get())
    #         self.calculate_bmi()
    #     except ValueError:
    #         messagebox.showerror("Invalid input", "Please enter a valid height.")

    # def calculate_bmi(self):
    #     weight = 70
    #     height_in_meters = self.height / 100
    #     bmi = weight / (height_in_meters ** 2)
    #     messagebox.showinfo("Your BMI", f"Your BMI is: {bmi:.2f}\nAge: {self.age}\nGender: {self.gender}")
    #    # self.after(5000, self.show_age_screen)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = BMICalculator()
    app.mainloop()