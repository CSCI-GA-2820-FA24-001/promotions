# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Introduction

The Promotions microservice is part of an eCommerce backend project designed to provide RESTful services for managing product promotions. This service allows you to create, read, update, delete, and list promotions, supporting a full CRUD lifecycle. The microservice also exposes metadata about itself at the root endpoint `(/)`.

**Note:** The base service code is contained in `routes.py` while the business logic for manipulating Promotions is in the `models.py` file. This follows the popular Model View Controller (MVC) separation of duties by keeping the model separate from the controller. As such, we have two test suites: one for the model (`test_models.py`) and one for the service itself (`test_routes.py`)

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## API Endpoints

### Root Route (`/`)

#### Description

The root route provides metadata and basic information about the Promotion Service, such as its name, version, and the main endpoint. It serves as an entry point to verify that the API is accessible. This route can be used as a simple health check to ensure that the service is running properly.

#### HTTP Method

-   `GET`

#### Example Request

`GET /` 

#### Response

-   **Status Code**: `200 OK`
-   **Content Type**: `application/json`
-   **Response Body**:
 
    `{
      "service_name": "Promotion Service",
      "version": "v1.0",
      "endpoint": "/promotions"
    }` 

### Create a Promotion
- **URL**: `/promotions`
- **Method**: `POST`
- **Description**: Creates a new promotion.
-   **Response**: Returns the created promotion details with a unique promotion ID.

### Read a Promotion

-   **URL**: `/promotions/<promotion_id>`
-   **Method**: `GET`
-   **Description**: Retrieves details of a specific promotion by its ID.
- **Response**: Returns the detailed information about the specific promotion being requested.
### Update a Promotion

-   **URL**: `/promotions/<promotion_id>`
-   **Method**: `PUT`
-   **Description**: Updates an existing promotion.
-   **Response**: Returns the updated promotion details.

### Delete a Promotion

-   **URL**: `/promotions/<promotion_id>`
-   **Method**: `DELETE`
-   **Description**: Deletes a promotion by its ID.
-   **Response**: Returns a success message.

### List Promotions

-   **URL**: `/promotions`
-   **Method**: `GET`
-   **Description**: Lists all existing promotions.
-   **Response**: Returns an array of promotion objects.


## Running the tests

As developers we always want to run the tests before we change any code. That way we know if we broke the code or if someone before us did. Always run the test cases first!

Run the unit tests using `pytest`

```shell
make test
```

PyTest is configured via the included `setup.cfg` file to automatically include the `--pspec` flag so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

PyTest is also configured to automatically run the `coverage` tool and you should see a percentage-of-coverage report at the end of your tests. If you want to see what lines of code were not tested use:

```shell
coverage report -m
```

This is particularly useful because it reports the line numbers for the code that have not been covered so you know which lines you want to target with new test cases to get higher code coverage.

You can also manually run `pytest` with `coverage` (but settings in `pyporojrct.toml` do this already)

```shell
$ pytest --pspec --cov=service --cov-fail-under=95
```

Try and get as close to 100% coverage as you can.

It's also a good idea to make sure that your Python code follows the PEP8 standard. Both `flake8` and `pylint` have been included in the `pyproject.toml` file so that you can check if your code is compliant like this:

```shell
make lint
```

Which does the equivalent of these commands:

```shell
flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
pylint service tests --max-line-length=127
```

Visual Studio Code is configured to use `pylint` while you are editing. This catches a lot of errors while you code that would normally be caught at runtime. It's a good idea to always code with pylint active.

## Running the service

The project uses `honcho` which gets it's commands from the `Procfile`. To start the service simply use:

```shell
honcho start
```

As a convenience you can aso use:

```shell
make run
```

You should be able to reach the service at: http://0.0.0.0:8080. The port that is used is controlled by an environment variable defined in the `.flaskenv` file which Flask uses to load it's configuration from the environment by default.

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
