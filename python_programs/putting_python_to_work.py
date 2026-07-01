# Ask the user for the radius of the circle
radius = float(input("What is the radius of the circle? "))

# Calculate the diameter
diameter = 2 * radius

# Calculate circumference
circumference = 2 * 3.14 * radius

# Calculate area
area = 3.14 * (radius ** 2)

# Display the results
print(f"A circle with a radius of {radius} units will have a diameter of {diameter} units, "
    f"a circumference of {circumference} units, and an area of {area} square units.")
