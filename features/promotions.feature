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