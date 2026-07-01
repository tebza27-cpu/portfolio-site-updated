import requests

def get_summary(book, chapter):
    base_url = 'https://openscriptureapi.org/api/scriptures/v1/lds/en/volume/bookofmormon/'
    # TODO: Create a URL string that will access the API for the given book and chapter
    url = f"{base_url}{book.lower().replace(' ', '')}/{chapter}"
    response = requests.get(url)
    data = response.json()
    return data["chapter"]["summary"]

    # HINT: The URL should be in the format f"{base_url}{book.lower()}/{chapter}"
    # HINT: Use the requests.get() method to access the API and return the JSON data
    # HINT: Extract the summary from the JSON data and return it


def run_summary_tool():

    # Print a welcome message as shown in the example. "Welcome to the Book of Mormon Summary Tool!"
    print("Welcome to the Book of Mormon Summary Tool!")

    # Use a while loop to allow the user to input a book and chapter
    # Ask the user for the book and chapter they would like to view a summary of
    while True:
        try:
            book = input("Which book of the Book of Mormon would you like? ")
            chapter = input(f"Which chapter of {book} are you interested in? ")
            # Use the get_summary() function to retrieve the summary and print it
            summary = get_summary(book, chapter)
            print(f"\nSummary of {book} chapter {chapter}:")
            print(summary)
        except KeyError:
            print("Error: Invalid book or chapter. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
        # Ask the user if they would like to view another summary
        again = input("Would you like to view another (Y/N)? ").strip().lower()
        if again != "y":
            print("Thank you for using Book of Mormon Summary Tool!")
            break
    # If the user does not want to view another summary, print "Thank you for using Book of Mormon Summary Tool!"
    # do not forget to finish or break the loop


if __name__ == "__main__":
    run_summary_tool()