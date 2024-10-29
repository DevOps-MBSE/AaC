Feature:  Print-Defs Evaluation

    Scenario: Print Definitions from Context
        When "print-defs" is called with args " " and flags " "
        Then I should receive a list of definitions to the terminal

    Scenario: Print Definitions from Context with Core-Only
        When "print-defs" is called with args " " and flags "--core-only"
        Then I should receive a list of core definitions to the terminal
