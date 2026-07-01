# *****************************************************************************
# *                                                                           *
# *   IMPORTANT: DO NOT MODIFY THIS FILE                                      *
# *                                                                           *
# *   This testing file is provided to help you check the functionality of    *
# *   your code and understand the requirements for this assignment.          *
# *                                                                           *
# *   Please review the tests carefully to understand what is expected, but   *
# *   DO NOT make any changes to this file. Modifying this file will          *
# *   interfere with the grading system, lead to incorrect results, and       *
# *   will be flagged as cheating.                                            *
# *                                                                           *
# *   Focus on writing your own code to meet the requirements outlined in the *
# *   tests.                                                                  *
# *                                                                           *
# *****************************************************************************


import pytest
from common_setup import pre_test_setup, check_internet_connection

def test_all():
    test_outputs, test_points_awarded, test_feedback, test_response_data = pre_test_setup()  # passing no tests means test everything
    if check_internet_connection():
        assert test_response_data['totalPointsAwarded'] == test_response_data['totalPointsPossible'], test_feedback
    else:
        output = test_outputs["menu_and_input_validation"]
        assert "thanks for using my finance" in output.lower()

        output = test_outputs["gross_pay_calculation"]
        assert "gross pay" in output.lower() and "4392" in output.lower()
        assert "federal tax" in output and "439.20" in output.lower()
        assert "state tax" in output and "219.60" in output.lower()
        assert "social security" in output.lower() and "272.30" in output.lower()
        assert "net pay" in output.lower() and "3460.90" in output.lower()

        output = test_outputs["revenue_and_expenses"]
        assert all(keyword.lower() in output.lower() for keyword in ["revenue", "3460.90", "expenses", "-2200.00", "discretionary", "1260.90"])

if __name__ == '__main__':
    pytest.main()
