# NYU DevOps Project Template

[![CI Build](https://github.com/CSCI-GA-2820-FA24-001/promotions/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA24-001/promotions/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA24-001/promotions/graph/badge.svg?token=Z3A4UWCWVY)](https://codecov.io/gh/CSCI-GA-2820-FA24-001/promotions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

The Promotions Microservice is part of an eCommerce backend designed to provide RESTful services for managing product promotions. It supports full CRUD operations and advanced functionalities like querying and custom actions.

## Overview

This project follows the Model-View-Controller (MVC) design pattern:

- Model (models.py): Handles the business logic for Promotions.
- View (routes.py): Exposes the RESTful API endpoints.
- Controller: Combined logic between service routes and database operations.

All functionality is supported by extensive test coverage (>95%) to ensure reliability during development and deployment.

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
.github             - Include issue/user stories template and CI workflow
.tekton             - YAML files to create and run continuous integration and continuous delivery (CI/CD) pipelines
k8s                 - Kubernetes configuration files, used to manage and deploy applications on a Kubernetes cluster.

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
└── statics                - Front end code

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## API Documentation

The service uses Flask-RESTX to provide Swagger UI for API documentation. Access it at:

- URL: /api/apidocs/

### Key Features

#### Promotions

- Create: `POST /api/promotions`
- Read: `GET /api/promotions/<promotion_id>`
- Update: `PUT /api/promotions/<promotion_id>`
- Delete: `DELETE /api/promotions/<promotion_id>`
- List: `GET /api/promotions`

#### Health Check

- Endpoint: `/health`
- Response: `{"status": "OK"}`


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


## Behavior-Driven Development (BDD)

Behavior-Driven Development (BDD) is implemented to test the application from the end-user's perspective. It ensures that the service behaves as expected when accessed through its UI. Tests are written in Gherkin syntax and executed using `behave` with Selenium.

---

### BDD Features

The BDD tests validate the following operations:
1. **Create a Promotion**: Verify that new promotions can be added through the UI.
2. **Read a Promotion**: Ensure that promotion details can be viewed.
3. **Update a Promotion**: Test that existing promotions can be updated.
4. **Delete a Promotion**: Confirm that promotions can be removed.
5. **List Promotions**: Verify that all promotions are displayed in the UI.
6. **Query Promotions**: Test the ability to filter promotions by specific criteria.
7. **Action on Promotions**: Validate custom actions defined for promotions.

---

### Running BDD Tests

To execute the BDD tests:

   ```bash
   behave
   ```

## Kubernetes Deployment

This microservice is deployed to a Kubernetes cluster using the manifests provided in the `k8s/` directory.

### Local Development Setup

To deploy the application locally, follow these steps:

1. **Create a Kubernetes Cluster**:
   - Use `K3s` or `Minikube` to set up a local cluster.
   - Run the following command to create the cluster:
     ```bash
     make cluster
     ```

2. **Deploy Application and Database**:
   - Apply the Kubernetes manifests:
     ```bash
     kubectl apply -f k8s/
     ```

3. **Verify Deployment**:
   - Check the status of Kubernetes resources:
     ```bash
     kubectl get all
     ```
   - Ensure that pods are in the `Running` state and services are available.

4. **Access the Application Using Ingress**:
   - Access the application at:
     ```
     http://localhost:8080
     ```
### Kubernetes Manifests

The `k8s/` directory contains the necessary manifests for deploying the microservice and its database:

- **Application Deployment**:
  - `deployment.yaml`: Configures the application deployment.
  - `service.yaml`: Exposes the application as a Kubernetes service.
  - `ingress.yaml`: Configures ingress routing to expose the service externally.

- **Database Deployment**:
  - `postgres/`:
    - `statefulset.yaml`: Deploys PostgreSQL as a StatefulSet.
    - `service.yaml`: Exposes the database as a service.



## Continuous Integration and Deployment

### CI with GitHub Actions

Continuous Integration is implemented using GitHub Actions, ensuring that every push to the `master` branch or pull request is validated for quality and functionality. The following steps are automated:

1. **Linting**: Code is checked for style and quality issues using `flake8` and `pylint`.
2. **Unit Tests**: All unit tests are executed with `pytest`.
3. **Code Coverage**: The codebase is analyzed to ensure a minimum of 95% test coverage.

The results of these checks are displayed directly in pull requests, and the repository includes badges for build status and code coverage.

### CD to Kubernetes

Continuous Deployment is automated using a Tekton pipeline. The pipeline is triggered on successful CI completion and performs the following:

1. **Build a Docker Image**
2. **Deploy to Kubernetes**
3. **Run BDD Tests**

### GitHub Actions Workflow

The CI/CD workflow is defined in `.github/workflows/ci.yml`. Key features include:
- Linting and code quality checks.
- Unit tests with coverage reporting.
- Integration with Codecov for test coverage metrics.
- Notifications of build status directly in GitHub.

### Pipeline Status

The build and deployment status is visible through the following badges:

- **Build Status**: ![CI Build](https://github.com/CSCI-GA-2820-FA24-001/promotions/actions/workflows/ci.yml/badge.svg)
- **Code Coverage**: ![codecov](https://codecov.io/gh/CSCI-GA-2820-FA24-001/promotions/graph/badge.svg?token=Z3A4UWCWVY)



## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
