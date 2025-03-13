def calculate_bmi(weight, height_cm):
    # Convert height from centimeters to meters
    height_m = float(height_cm) / 100
    # BMI formula: weight (kg) / height (m)^2
    return round(float(weight) / (height_m ** 2), 2)

def classify_bmi(bmi, sex, age):
    """
    Classifies BMI based on age, sex, and estimated percentile ranges for teens.
    Converts to an equivalent adult BMI category if the person is an adult.
    """
    if age >= 2 and age < 20:  # Teenagers (13-19)
        if sex.lower() == "male":
            if bmi < 17.5:
                return "Underweight"
            elif 17.5 <= bmi < 23.0:
                return "Healthy Weight"
            elif 23.0 <= bmi < 27.0:
                return "Overweight"
            else:
                return "Obese"
        
        elif sex.lower() == "female":
            if bmi < 17.0:
                return "Underweight"
            elif 17.0 <= bmi < 24.0:
                return "Healthy Weight"
            elif 24.0 <= bmi < 28.0:
                return "Overweight"
            else:
                return "Obese"
        
        else:
            return "Invalid input: Please enter 'male' or 'female'."
    
    else:  # Adults (20+)
        if sex.lower() == "male":
            if bmi < 18.5:
                return "Underweight"
            elif 18.5 <= bmi < 24.9:
                return "Healthy Weight"
            elif 25.0 <= bmi < 29.9:
                return "Overweight"
            else:
                return "Obese"
        
        elif sex.lower() == "female":
            if bmi < 18.5:
                return "Underweight"
            elif 18.5 <= bmi < 24.9:
                return "Healthy Weight"
            elif 25.0 <= bmi < 29.9:
                return "Overweight"
            else:
                return "Obese"
        
        else:
            return "Invalid input: Please enter 'male' or 'female'."
def bmi(age,sex,height,weight):
    try:
        bmi = calculate_bmi(weight, height)
        status = classify_bmi(bmi, sex, age)
        return bmi,status
    except ValueError:
        print("Invalid input. Please enter numeric values for age, height, and weight.")

def main():
    print("BMI Calculator")
    try:
        age = int(input("Enter your age: "))
        sex = input("Enter your sex (male/female): ").strip().lower()
        height_cm = float(input("Enter your height in centimeters (e.g., 175): "))
        weight = float(input("Enter your weight in kilograms (e.g., 70): "))

        if age <= 0 or height_cm <= 0 or weight <= 0:
            print("Invalid input. Age, height, and weight must be positive numbers.")
            return

        bmi = calculate_bmi(weight, height_cm)
        print(bmi)
        status = classify_bmi(float(bmi), sex,age)

        print(f"\nYour BMI is: {bmi}")
        print(f"Health Status: {status}")

    except ValueError:
        print("Invalid input. Please enter numeric values for age, height, and weight.")

if __name__ == "__main__":
    main()