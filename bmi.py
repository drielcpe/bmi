
def interpret_bmi_adult(bmi):
    """Interpret BMI for adults (18+ years old)."""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

def interpret_bmi_child(bmi, age, sex):
    """Interpret BMI for children and adolescents (2 to 17 years old) using CDC growth charts."""
    # Simplified interpretation based on BMI-for-age percentiles
    if bmi < 5:
        return "Underweight"
    elif 5 <= bmi < 85:
        return "Normal weight"
    elif 85 <= bmi < 95:
        return "Overweight"
    else:
        return "Obese"

def classify_bmi(bmi,age,sex):
    try:
      
        if age >= 18:
            interpretation = interpret_bmi_adult(bmi)
        else:
            interpretation = interpret_bmi_child(bmi, age, sex)
        
        print(f"\nYour BMI is: {bmi:.2f}")
        print(f"Interpretation: {interpretation}")
        return interpretation
    
    except ValueError:
        print("Invalid input. Please enter numeric values for age, height, and weight.")

