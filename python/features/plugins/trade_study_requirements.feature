Feature:  Trade study document model with requirements example

    Scenario Outline:  Ensure all requirements are parsed and loaded into context
        Given I have the "./features/trade_study/doc/cookie_trade_study.aac" file
        When I load the "./features/trade_study/doc/cookie_trade_study.aac" file
        Then I should have 28 total req definitions
        And I should have 3 total req_spec definitions
        And I should have 5 total model definitions
        And I should have requirement id <req_id>

        Examples: Requirement IDs
            |req_id |
            |DOC-001    |
            |DOC-002    |
            |DOC-003    |
            |DOC-004    |
            |TS-001    |
            |TS-002    |
            |TS-003    |
            |TS-004    |
            |TS-005    |
            |TS-006    |
            |TS-007    |
            |TS-008    |
            |TS-009    |
            |TS-010    |
            |GCD-001    |
            |GCD-002    |
            |GCD-003    |
            |GCD-004    |
            |GCD-005    |
            |GCD-006    |
            |GCD-007    |
            |GCD-008    |
            |GCD-009    |
            |GCD-010    |
            |GCD-011    |
            |GCD-012    |
            |GCD-013    |
            |GCD-014    |
