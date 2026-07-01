import subprocess
import pytest
import requests
import json
import socket
from tests.common_setup import pre_test_setup, check_internet_connection

test_outputs = {}
test_name = None
test_points_awarded = {}
test_response_data = {}

# This script runs ALL tests -- if you want to run separate tests, see the .tests folder
# This test has 1,233 tokens calling OpenAI gtp-4o model which costs $2.50 for 1 million tokens
# So it should cost $.004 or about half a penny for each time they run all test here using pytest

# In GitHub it runs each test separately which calls the API 8 times, so it will cost about $.032 each time they push their code



def test_all():
    test_outputs,test_points_awarded,test_feedback,test_response_data = pre_test_setup()# passing no tests means test everything
    if check_internet_connection():
        assert test_response_data['totalPointsAwarded'] == test_response_data['totalPointsPossible'], test_feedback

    else :
        output = test_outputs["odd_number"]
        assert "3 is an odd number." in output, "Expected full output '3 is an odd number.' not found."

        output = test_outputs["even_number"]
        assert "4 is an even number." in output, "Expected full output '4 is an even number.' not found."

        output = test_outputs["perfect_square"]
        assert "9 has a perfect square root." in output, "Expected full output '9 has a perfect square root.' not printed."

        output = test_outputs["non_perfect_square"]
        assert "8 does not have a perfect square root." in output, "Expected full output '8 does not have a perfect square root.' not printed."

        output = test_outputs["factors_of_9"]
        assert "1,3,9" in output, "Factors of 9 are incorrect OR not printed as '1,3,9'."

        output = test_outputs["factors_of_21"]
        assert "1,3,7,21" in output, "Factors of 21 are incorrect OR not printed as '1,3,7,21'."

        output, count_prompt = test_outputs["program_prompts_for_another_input"]
        assert count_prompt == 2, f"Expected 'Please enter a whole number' to be output twice, but found {count_prompt} occurrences."

        output = test_outputs["program_exits_correctly"]
        assert "Thank you for playing!" in output, "Program does not exit correctly after 'N' input OR 'Thank you for playing!' is not printed."

if __name__ == '__main__':
    pytest.main()