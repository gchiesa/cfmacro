# Created by gchiesa at 02/02/2020
Feature: Inline Stack Processor Integration tests
  # Enter feature description here

    Scenario Outline: Template with inline stack
        Given   a local template loaded from fixture <input>
        And     a template loaded from fixture <module> is present on s3 with the key <key>
        Then    the outcome template match the template loaded from the fixture <outcome>

        Examples: sources
            | input          | module                | bucket        | key                            | outcome                |
            | test2.template | test2_module.template | 0123456789012 | path/to/module/module.template | test2_outcome.template |

