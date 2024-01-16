Feature:  Check definitions example provided in documentation

    Scenario:  Check the Definitions Example
        Given I have the "./docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" model
        When I check the "./docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the First Inheritance Example
        Given I have the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" model
        When I check the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the Second Inheritance Example
        Given I have the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" model
        When I check the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the All Possible Plugin Example
        Given I have the "./docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" model
        When I check the "./docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the Do Stuff Plugin Example
        Given I have the "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" model
        When I check the "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" model
        Then I should receive a message that the check was successful
