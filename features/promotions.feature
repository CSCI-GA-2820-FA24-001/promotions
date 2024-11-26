Feature: The promotions service back-end
    As a promotions eCommerce Manager
    I need a RESTful catalog service
    So that I can keep track of all promotions.

Background:
    Given the following promotions
        | id                                   | name           | description          | start_date           | end_date             | active_status | created_by                           | updated_by                           | extra                    |
        | 550e8400-e29b-41d4-a716-446655440000 | Winter Sale    | Discounted products  | 2024-12-01T00:00:00Z | 2024-12-31T23:59:59Z | True          | 123e4567-e89b-12d3-a456-426614174000 | 123e4567-e89b-12d3-a456-426614174000 | {“category”: “seasonal”} |
        | 550e8400-e29b-41d4-a716-446655440001 | Clearance Sale | Clearance items only | 2024-11-15T00:00:00Z | 2024-11-30T23:59:59Z | False         | 123e4567-e89b-12d3-a456-426614174000 | 123e4567-e89b-12d3-a456-426614174000 | {“priority”: “high”}     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotion Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promotion
    When I visit the "Home Page"
    And I switch to the "Create A Promotion" tab
    And I set the "Name" to "Black Friday Sale"
    And I set the "Description" to "Description For Black Friday Sale"
    And I set the "Product IDs" to "123, 234, 345"
    And I set the "Start Date" to "11-24-2024"
    And I set the "End Date" to "11-30-2024"
    And I select "Active" in the "Active Status" dropdown
    And I set the "Creator's UUID" to "a6fe4a43-dc08-471c-9d33-ebacff755f88"
    And I set the "Updater's UUID" to "a6fe4a43-dc08-471c-9d33-ebacff755f88"
    And I set the "Additional MetaData" to "{}"
    And I press the "Create" button
    Then I should see the message "Success"
