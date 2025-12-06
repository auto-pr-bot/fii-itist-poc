# Conference Participant Registration & Display System

A serverless web application built for a live conference ([Fii IT-ist](https://fii-itist.asii.ro/)), enabling participant registration with an engaging visual display. The system collects a participant's name (and metadata such as phone model and IP) through a web form and displays registered names on a dynamic "wall of fame".

## Key Features

- User Registration Form: Clean, mobile-responsive interface for attendees to submit their names
- Dynamic Results Display: Kahoot-style animated wall of fame with auto-refreshing display
- Real-time Polling: Results page polls every 5 seconds (client-side) to show new participants
- Data Collection: Captures participant name, inferred phone model (from User-Agent) and IP address
- Serverless Architecture: Built with AWS Lambda + API Gateway, SQS and DynamoDB
- Dual Storage: SQS queue for asynchronous processing and DynamoDB for persistent storage

## Architecture

![Architecture Diagram](docs/architecture-diagram.png)

Built using AWS Serverless technologies:

- AWS Lambda (Python 3.12): Request routing and business logic
- API Gateway: RESTful API endpoints (proxy integration)
- Amazon SQS: Message queue for form submissions / events
- Amazon DynamoDB: Persistent storage for participant events
- AWS SAM: Infrastructure as Code and local development tooling

The AWS SAM template (template.yaml) provisions the Lambda function, an SQS queue and a DynamoDB table. The Lambda environment variables SQS_QUEUE_URL and DYNAMODB_TABLE are wired to the created resources.

## What is implemented in this repository

- Lambda routing and handlers: hello_world/app.py routes requests to handlers in hello_world/handlers/
- Handlers:
  - GET /               -> hello_world/handlers/home.py (serves the HTML form)
  - POST /form          -> hello_world/handlers/form.py (validates input, extracts metadata, sends message to SQS)
  - GET /results        -> hello_world/handlers/results.py (serves the animated results HTML)
  - All other requests  -> hello_world/handlers/default.py (catch-all: logs and stores request to SQS and DynamoDB)
- Static HTML templates live under hello_world/templates/
  - form.html (registration form + client-side POST to /form)
  - results.html (animated participants wall — currently uses client-side mock data by default)
- AWS clients singletons: hello_world/aws_clients.py (boto3 clients)
- Simple utils for parsing user-agent and request helpers: hello_world/utils/

## API Endpoints

| Method | Endpoint   | Description                                    |
| ------ | ---------- | ---------------------------------------------- |
| GET    | /          | Displays participant registration form (HTML)  |
| POST   | /form      | Processes form submission and queues data to SQS |
| GET    | /results   | Shows animated wall of registered participants (HTML) |
| *      | *          | Catch-all handler records request to SQS + DynamoDB |

Notes:
- The results page currently uses mock data client-side (see hello_world/templates/results.html, set USE_MOCK_DATA = false when a real GET /participants endpoint is available).
- There is no dedicated GET /participants endpoint implemented in this repository; results.html has a placeholder API_ENDPOINT = "/participants" for future implementation.

## Data and Resources

- Environment variables used by the Lambda function:
  - SQS_QUEUE_URL — URL of the SQS queue used to send form messages
  - DYNAMODB_TABLE — DynamoDB table name for storing request/participant records
- Resources created by template.yaml:
  - SQS queue: fii-task-queue (logical name TaskQueue)
  - DynamoDB table: participants (logical name ParticipantsTable, partition key "id")

## Local development

Prerequisites:
- AWS SAM CLI (sam)
- Docker (for `sam build --use-container` if needed)
- Python 3.12 runtime (for parity with deployed Lambda)

Build and run locally:

# Build
sam build --use-container

# Start the local API (defaults to port 3000)
sam local start-api

Access endpoints locally (default port 3000):
- Registration form: http://localhost:3000/
- Submit form (example):
  curl -X POST "http://localhost:3000/form" -H "Content-Type: application/json" -d '{"name":"Jane Doe"}'
- Results page (HTML): http://localhost:3000/results

Local environment notes:
- When running locally, the Lambda will attempt to use boto3 to contact AWS services. For end-to-end local testing you can:
  - Configure AWS credentials to use real AWS resources; or
  - Point SQS/DynamoDB calls to localstack or other local emulators and set the SQS_QUEUE_URL/DYNAMODB_TABLE environment variables accordingly.
- The SAM CLI will use the environment variables from the template when deployed. For local testing you can override environment variables via the sam CLI or export them in your shell.

Example: run a single invocation with a fixture event
sam local invoke ProxyFunction -e events/get-root.json

## Deployment

Deploy using SAM:

# Build
sam build --use-container

# Deploy (guided the first time)
sam deploy --guided

Note: samconfig.toml in the repo contains example deploy configuration (stack name, region, etc.). The SAM template (template.yaml) defines the IAM policies required for SQS send and DynamoDB write for the Lambda.

## Testing

Unit / integration tests can be added under tests/. The repository includes a tests/requirements.txt with pytest and test dependencies.

To run tests (if present):
pip install -r tests/requirements.txt
pytest

## Implementation details / developer notes

- Runtime: Python 3.12 (see template.yaml)
- AWS clients: boto3 is used inside hello_world/aws_clients.py and hello_world/services.py
- Form handler: hello_world/handlers/form.py
  - Validates a JSON body with a "name" field
  - Extracts phone model via User-Agent parsing and client IP from the API Gateway event
  - Sends a message to SQS with {"name","phoneModel","ip"}
- Results page (hello_world/templates/results.html)
  - Currently displays mock participant data by default (USE_MOCK_DATA = true). When you implement a /participants endpoint that returns { "participants": ["Name A", "Name B", ...] }, set USE_MOCK_DATA = false and update API_ENDPOINT accordingly to point to the real endpoint.
- Catch-all handler (hello_world/handlers/default.py)
  - Records arbitrary requests by sending a message to the SQS queue and a record to DynamoDB (table name from env var).

## Example cURL

Submit a participant:
curl -X POST "https://<API_GATEWAY_URL>/form" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice"}'

Fetch the results page (HTML):
curl "https://<API_GATEWAY_URL>/results"

## Contributing

Contributions, bug reports and improvements are welcome. If you add a server endpoint (for example a participants list endpoint), please:
- Update hello_world/templates/results.html to point API_ENDPOINT to the new endpoint and set USE_MOCK_DATA to false
- Add appropriate unit / integration tests
- Update this README to document the new API

## License

This project is provided as-is for demonstration purposes.
