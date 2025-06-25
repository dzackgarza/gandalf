Feature: Simple Greeter CLI
  As a user of the CLI tool
  I want to be greeted by name
  So that I feel welcomed.

  Scenario: Greeting with a provided name
    Given the greeter CLI application is available
    When I run the application with the name "Alice"
    Then the output should be "Hello, Alice!"

  Scenario: Greeting without a provided name (default behavior)
    Given the greeter CLI application is available
    When I run the application without providing a name
    Then the output should be "Hello, World!"

  Scenario: Greeting with a different name
    Given the greeter CLI application is available
    When I run the application with the name "Bob"
    Then the output should be "Hello, Bob!"
