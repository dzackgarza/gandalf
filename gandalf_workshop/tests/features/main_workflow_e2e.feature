Feature: Main Gandalf Workshop Workflow E2E
  As a user
  I want to submit a prompt to the Gandalf Workshop CLI
  So that my commission is processed.

  Scenario: User submits a prompt and receives processing confirmation
    When I run the Gandalf Workshop CLI with the prompt "create a simple hello world script"
    Then the output should indicate the commission was received
    And the output should show a commission ID being assigned
    And the output should indicate the commission was processed
