# Define variables
BACKEND_DIR=my_flask_app
FRONTEND_DIR=nextjs
TEST_DIR=tests
DOCKER_IMAGE_NAME_BACKEND=sveerisetti/flask-backend
DOCKER_IMAGE_NAME_FRONTEND=sveerisetti/nextjs-frontend

# For formatting we use the black formatter for Python and prettier for JavaScript
# For testing we use pytest which references the test_jaydoc_module.py in the tests directory
# For linting we use flake8 for Python and eslint for JavaScript
PYTHON_FORMATTER=black
JS_FORMATTER=npx prettier --write
TEST_RUNNER=pytest
PYTHON_LINTER=flake8
JS_LINTER=npx eslint

# Here we install the dependencies for the backend
install-backend:
	@pip install -r $(BACKEND_DIR)/requirements.txt

# Here we install dependencies for the frontend
install-frontend:
	@npm install --prefix $(FRONTEND_DIR)

# Here we format the code using the black formatter for backend
format-backend:
	@$(PYTHON_FORMATTER) $(BACKEND_DIR)

# Here we format the code using the prettier formatter for frontend
format-frontend:
	@$(JS_FORMATTER) $(FRONTEND_DIR)

# Here we lint the code using flake8 for backend
lint-backend:
	@$(PYTHON_LINTER) $(BACKEND_DIR) --config=.flake8

# Here we run the tests using pytest
test-backend:
	@$(TEST_RUNNER) $(TEST_DIR)

# Here we build the Docker image for the backend
build-backend:
	@docker build -t $(DOCKER_IMAGE_NAME_BACKEND) $(BACKEND_DIR)

# Here we build the Docker image for the frontend
build-frontend:
	@docker build -t $(DOCKER_IMAGE_NAME_FRONTEND) $(FRONTEND_DIR)

# Here we run all steps for the backend in sequence
backend: install-backend format-backend lint-backend test-backend build-backend

# Here we run all steps for the frontend in sequence
frontend: install-frontend format-frontend build-frontend

# Combo command to run all steps for both backend and frontend
all: backend frontend

# Here we run docker-compose to build and start both services
compose-up:
	@docker-compose up --build

.PHONY: install-backend install-frontend format-backend lint-backend lint-frontend test-backend build-backend build-frontend backend frontend all
