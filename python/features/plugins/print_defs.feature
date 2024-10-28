Feature:  Print-Defs Evaluation

    Scenario: Print Definitions from Context
        When print-defs is called from terminal
        Then I should receive a list of definitions to the terminal
