Feature:  Gen-Plugin Evaluation

    Scenario: Generate From a Plugin File
        Given I have a valid "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac"
        When Gen-Plugin is ran with the valid plugin file
        Then I should receive generated files in a temporary directory

