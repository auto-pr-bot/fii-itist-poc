# Conference Participant Registration & Display System

A small serverless web application designed for live events (originally built for Fii IT-ist). It lets attendees submit their names via a simple form and displays registered participants on an animated "wall of fame" page. The app is implemented as an AWS Serverless application (SAM) using Lambda, API Gateway, SQS and DynamoDB.

## Key Features

- User registration form with mobile-friendly UI
- Animated participants "wall of fame" (Kahoot-style) with auto-polling
- Lightweight data collection: participant name, detected phone model (from User-Agent) and client IP
- Serverless architecture with SQS queuing and DynamoDB persistence
- Simple, single Lambda function that routes requests to small handler modules

## Architecture

![Architecture Diagram](docs/architecture-diagram.png)

Built using AWS Serverless technologies:

- AWS Lambda (Runtime: Python 3.12) — request routing and business logic
- Amazon API Gateway — exposes the web endpoints
- Amazon SQS — message queue for asynchronous processing
- Amazon DynamoDB — persistent storage for requests/participants
- AWS SAM — infrastructure as code and deployment tooling

The SAM template is in template.yaml and declares:
- A single Lambda function (hello_world/app.lambda_handler)
- An SQS queue (fii-task-queue)
- A DynamoDB table (participants)

## Code layout (important files)

- hello_world/app.py — Lambda entrypoint + routing
- hello_world/handlers/ — request handlers:
  - home.py — GET / (returns the HTML form)
  - form.py — POST /form (processes submissions, sends to SQS)
  - results.py — GET /results (returns the animated results HTML)
  - default.py — catch-all for other requests; writes to SQS + DynamoDB
  - formular.py — alternative form handler (unused by router)
- hello_world/templates/ — HTML pages (form.html, results.html)
- hello_world/utils/ — helper utilities:
  - request_helpers.py — header normalization, IP extraction, body reading
  - phone_detector.py — parse phone model from User-Agent
- template.yaml — SAM template defining resources and environment variables
- samconfig.toml — optional SAM CLI configuration

## API Endpoints

| Method | Endpoint   | Description                                    |
| ------ | ---------- | ---------------------------------------------- |
| GET    | /          | Displays participant registration form (form.html) |
| POST   | /form      | Accepts JSON { "name": "..." } — queues data to SQS |
| GET    | /results   | Returns the animated results page (results.html) |

Notes:
- POST /form expects a JSON body with a "name" field. The handler extracts the User-Agent to infer a phone model and extracts client IP (X-Forwarded-For or requestContext.identity.sourceIp). It sends a JSON message to SQS with { name, phoneModel, ip } and returns 200 on success.
- The results page currently uses mock data (see results.html). There is no dedicated /participants API implemented in this repository — the results page has a placeholder API_ENDPOINT value and USE_MOCK_DATA is set to true by default.

## Environment variables

The function's environment variables are set in the SAM template (template.yaml). The following environment variables are used by the code:

- SQS_QUEUE_URL — URL of the SQS queue (set to the TaskQueue resource in template.yaml)
- DYNAMODB_TABLE — DynamoDB table name (set to ParticipantsTable in template.yaml)

When running locally with `sam local start-api` you will need to provide values for these environment variables (see Local Development below).

## Deployment

Prerequisites:
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Docker (required when building with containers)

Build and deploy:

```bash
# Build (use container to match Lambda environment)
sam build --use-container

# Deploy with guided configuration (first time)
sam deploy --guided

# Or if you already have samconfig.toml configured:
sam deploy
```

The SAM template exports:
- ApiGatewayUrl (base URL)
- SQSQueueUrl
- DynamoDBTable

## Local Development

You can run the API locally using the SAM CLI. Because the function expects SQS and DynamoDB environment variables, you should provide those when running locally. Example env file (env.json):

env.json
{
  "ProxyFunction": {
    "SQS_QUEUE_URL": "https://sqs.local/queue/fii-task-queue",
    "DYNAMODB_TABLE": "participants"
  }
}

Start the local API:

```bash
sam local start-api --env-vars env.json
```

Notes:
- If you want to exercise code that sends messages to SQS or writes to DynamoDB locally, you can point the env vars to localstack endpoints or to actual AWS resources. Alternatively, you can mock the AWS clients in tests.
- The results page (results.html) uses mock data by default (USE_MOCK_DATA = true). To integrate it with a real participants API, implement an endpoint (e.g. GET /participants) that returns { "participants": ["Name 1", "Name 2", ...] }.

## Testing

Unit/integration tests can be added under tests/. The repository includes a test dependencies file (tests/requirements.txt).

To run tests locally, create a virtualenv and install dependencies, then run pytest:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r tests/requirements.txt
pytest
```

(There are no unit tests included by default in this repo; add tests under tests/unit or tests/integration.)

## Implementation details / behaviour notes

- Routing: hello_world/app.lambda_handler inspects event['httpMethod'] and event['path'] to route to handlers:
  - GET /         -> handle_home
  - POST /form    -> handle_form
  - GET /results  -> handle_results
  - any other     -> handle_default
- Submission flow (POST /form):
  - Expects JSON body with "name"
  - Validates presence of name, returns 400 if missing or JSON invalid
  - Parses User-Agent header with hello_world/utils/phone_detector.py to infer phone model (iPhone, iPad, Android model snippet, or Mobile/Unknown)
  - Extracts client IP from X-Forwarded-For header or requestContext.identity.sourceIp
  - Sends a message to SQS with the submission (name, phoneModel, ip)
- Default handler (catch-all) logs/queues the incoming request and writes an item to DynamoDB (table name from DYNAMODB_TABLE env var)

## Known limitations / TODOs

- The results page uses mock data and does not call a real participants API out-of-the-box. To show live participants, implement a GET /participants handler that reads from DynamoDB (or another source) and returns a JSON array of names.
- There is an extra handler file hello_world/handlers/formular.py that mirrors form.py but the router currently routes only POST /form to form.py's handler. Remove or consolidate duplicate code if desired.

## Contributing

Contributions are welcome. Suggestions:
- Add a real /participants endpoint which queries DynamoDB for the latest participants
- Add input validation and deduplication on the ingestion path
- Add unit and integration tests (pytest)

## Troubleshooting

- "Missing environment variables" when running locally: provide an env file to sam local start-api or export SQS_QUEUE_URL and DYNAMODB_TABLE in your shell.
- AWS permissions: template.yaml grants the Lambda function permission to send messages to the SQS queue and write to the DynamoDB table via SAM policy templates. Ensure the deploying role has permission to create these resources.

## License

This project is provided as-is for demonstration purposes. Update or add a LICENSE file as needed.
