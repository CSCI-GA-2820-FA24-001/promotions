Feature: The promotions service back-end
    As a promotions eCommerce Manager
    I need a RESTful catalog service
    So that I can keep track of all promotions.

    Background:
        Given the following promotions
            | id                                   | name           | description          | start_date           | end_date             | active_status | created_by                           | updated_by                           | extra                    | product_ids   |
            | 550e8400-e29b-41d4-a716-446655440000 | Winter Sale    | Discounted products  | 2024-12-01T00:00:00Z | 2024-12-31T23:59:59Z | True          | 123e4567-e89b-12d3-a456-426614174000 | 123e4567-e89b-12d3-a456-426614174000 | {“category”: “seasonal”} | 101, 102, 103 |
            | 550e8400-e29b-41d4-a716-446655440001 | Clearance Sale | Clearance items only | 2024-11-15T00:00:00Z | 2024-11-30T23:59:59Z | False         | 123e4567-e89b-12d3-a456-426614174000 | 123e4567-e89b-12d3-a456-426614174000 | {“priority”: “high”}     | 101, 202, 203 |

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

    Scenario: Retrieve a Promotion
        When I visit the "Home Page"
        And I switch to the "Retrieve Promotion" tab
        And I set the "ID" to "550e8400-e29b-41d4-a716-446655440000"
        And I press the "Retrieve" button
        Then I should see the message "Success"

    Scenario: Creating a Promotion with an Invalid Creator's UUID
        When I visit the "Home Page"
        And I switch to the "Create A Promotion" tab
        And I set the "Name" to "Cyber Monday Deal"
        And I set the "Description" to "Huge discounts on all electronics"
        And I set the "Product IDs" to "456, 567, 678"
        And I set the "Start Date" to "11-27-2024"
        And I set the "End Date" to "12-03-2024"
        And I select "Active" in the "Active Status" dropdown
        And I set the "Creator's UUID" to "invalid-uuid-format"
        And I set the "Updater's UUID" to "a6fe4a43-dc08-471c-9d33-ebacff755f88"
        And I set the "Additional MetaData" to "{}"
        When I press the "Create" button
        Then I should see the message "Invalid Promotion: body of request contained bad data type badly formed hexadecimal UUID string"

    Scenario: Toggle a Promotion Status
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Name" to "Winter Sale"
        And I press the "Search" button
        Then I should see "Winter Sale" in the search results
        And I should see the promotion "Winter Sale" with "Active" Status in the search results
        When I press the "Toggle" button
        Then I should see the message "Success"
        And I should see the promotion "Winter Sale" with "Inactive" Status in the search results

    Scenario: Creating a Promotion with an Invalid Creator's UUID
        When I visit the "Home Page"
        And I switch to the "Create A Promotion" tab
        And I set the "Name" to "Cyber Monday Deal"
        And I set the "Description" to "Huge discounts on all electronics"
        And I set the "Product IDs" to "456, 567, 678"
        And I set the "Start Date" to "11-27-2024"
        And I set the "End Date" to "12-03-2024"
        And I select "Active" in the "Active Status" dropdown
        And I set the "Creator's UUID" to "invalid-uuid-format"
        And I set the "Updater's UUID" to "a6fe4a43-dc08-471c-9d33-ebacff755f88"
        And I set the "Additional MetaData" to "{}"
        When I press the "Create" button
        Then I should see the message "Invalid Promotion: body of request contained bad data type badly formed hexadecimal UUID string"

    Scenario: Searching promotions by name
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Name" to "Winter Sale"
        And I press the "Search" button
        Then I should see "Winter Sale" in the search results

    Scenario: Searching promotions by name with no results
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Name" to "Nonexistent Promotion"
        And I press the "Search" button
        Then I should see the message "No promotions found"

    Scenario: Successfully searching promotions by product ID
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Product ID" to "101"
        And I press the "Search" button
        Then I should see "101" in the search results

    Scenario: Searching promotions by product ID with no results
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Product ID" to "301"
        And I press the "Search" button
        Then I should see the message "No promotions found"

    Scenario: Searching promotions by multiple fields
        When I visit the "Home Page"
        And I switch to the "Search Promotions" tab
        And I set the "Name" to "Winter Sale"
        And I set the "Start Date" to "2024-12-01T00:00:00"
        And I set the "End Date" to "2024-12-31T23:59:59"
        And I press the "Search" button
        Then I should see the promotion "Winter Sale" between "2024-12-01T00:00:00" and "2024-12-31T23:59:59" in the search results

    Scenario: Updating promotions
        When I visit the "Home Page"
        And I switch to the "Update A Promotion" tab
        And I set the "ID" to "fe0e7528-271e-4e18-b209-4de72cbba141"
        And I set the "Creator's UUID" to "fe0e7528-271e-4e18-b209-4de72cbba142"
        And I set the "Updater's UUID" to "fe0e7528-271e-4e18-b209-4de72cbba143"
        And I set the "Name" to "not_free"
        And I set the "Description" to "sss"
        And I set the "Product IDs" to "prod_3"
        And I set the "Start Date" to "11/12/2024"
        And I set the "End Date" to "11/25/2024"
        And I set the "Active Status" to "Inactive"
        And I press the "Update" button
        Then I should see the message "Update successful!"

# TODO: Add sad path for update promotions when fixing backend logic