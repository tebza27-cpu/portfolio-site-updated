# TO-DO import math

# TO-DO Determine if number is even or odd

# TO-DO Determine if number has perfect square root

# TO-DO Determine all factors of number
import math

def main():
    play_game = True

    while play_game:
        # Prompt user for input
        number = int(input("Enter a whole number (i.e., an integer): "))

        print(f"\nThe number you entered is {number}.")

        # Check even, odd, or zero
        if number == 0:                           # If it's zero, we print that it's zero
            print("0 is an even number.")
        elif number % 2 == 0:                     # If it divides evenly by 2, it's even
            print(f"{number} is an even number.")
        else:                                     # Otherwise, it's odd
            print(f"{number} is an odd number.")

        # Check for perfect square root
        if number >= 0:
            root = math.sqrt(number)
            if int(root) == root:               # If the result is a whole number, then the original number is a perfect square
                print(f"{number} has a perfect square root.")
            else:
                print(f"{number} does not have a perfect square root.")
        else:
            print(f"{number} does not have a real square root.")

        # Find all the factors of the number
        factors = []
        for i in range(1, number + 1):      # A for loop goes from 1 up to the number
            if number % i == 0:
                factors.append(i)           # If it divides evenly, it's a factor

        print(f"The factors of {number} are {','.join(map(str, factors))}.")

        # Ask user if they want to continue
        again = input("\nWould you like to enter another number? (Y/N): ")   
        if again.lower() != "y":                
            play_game = False               
            print("\nThank you for playing!")

if __name__ == "__main__":
    main()