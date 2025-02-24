def calculate_bmi(weight, height_cm):
    # Convert height from centimeters to meters
    height_m = height_cm / 100
    # BMI formula: weight (kg) / height (m)^2
    return round(weight / (height_m ** 2), 2)

def interpret_bmi(bmi, age, sex):
    # BMI interpretation based on age and sex
    if age < 18:
        return "BMI interpretation for children and teens is different. Consult a doctor."
    else:
        if sex.lower() == "male":
            if bmi < 18.5:
                return "Underweight"
            elif 18.5 <= bmi < 24.9:
                return "Normal weight"
            elif 24.9 <= bmi < 29.9:
                return "Overweight"
            else:
                return "Obese"
        elif sex.lower() == "female":
            if bmi < 18.5:
                return "Underweight"
            elif 18.5 <= bmi < 24.9:
                return "Normal weight"
            elif 24.9 <= bmi < 29.9:
                return "Overweight"
            else:
                return "Obese"
        else:
            return "Invalid sex input. Use 'male' or 'female'."
def bmi(age,sex,height,weight):
    try:
        bmi = calculate_bmi(weight, height)
        status = interpret_bmi(bmi, age, sex)
        return bmi,status
    except ValueError:
        print("Invalid input. Please enter numeric values for age, height, and weight.")

# def main():
#     print("BMI Calculator")
#     try:
#         age = int(input("Enter your age: "))
#         sex = input("Enter your sex (male/female): ").strip().lower()
#         height_cm = float(input("Enter your height in centimeters (e.g., 175): "))
#         weight = float(input("Enter your weight in kilograms (e.g., 70): "))

#         if age <= 0 or height_cm <= 0 or weight <= 0:
#             print("Invalid input. Age, height, and weight must be positive numbers.")
#             return

#         bmi = calculate_bmi(weight, height_cm)
#         status = interpret_bmi(bmi, age, sex)

#         print(f"\nYour BMI is: {bmi}")
#         print(f"Health Status: {status}")

#     except ValueError:
#         print("Invalid input. Please enter numeric values for age, height, and weight.")

# if __name__ == "__main__":
#     main()