Feature:  Gen-Plugin Evaluation

    Scenario: Generate From a Plugin File
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac"
        When gen-plugin is ran with the valid file
        Then I should receive generated plugin files in a temporary directory

    Scenario: Generate From a Plugin File Using overwrite
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac"
        When gen-plugin is ran with the valid file
        And ran again with "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff_overwrite.aac" using overwrite flag
        Then I should receive generated plugin files in a temporary directory

    Scenario: Generate From a Plugin File Using evaluate
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac"
        When gen-plugin is ran with the valid file
        And ran again with "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff_overwrite.aac" using evaluate flag
        Then I should receive generated plugin files in a temporary directory


    Scenario: Generate From a Project File
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_project.aac"
        When gen-project is ran with the valid file
        Then I should receive generated project files in a temporary directory

    Scenario: Run Gen-Plugin on an incomplete plugin File
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff_bad.aac"
        When gen-plugin is ran with the valid file
        Then I should receive a message that the command was not successful

