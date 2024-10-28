Feature:  Print-Defs Evaluation

    Scenario: Print Definitions from Context
        When print-defs is called from terminal
        Then I should receive a list of definitions to the terminal

    Scenario: Print Definitions from Context with Core-Only
        When print-defs is called from terminal with the core_only flag
        Then I should receive a list of core definitions to the terminal
