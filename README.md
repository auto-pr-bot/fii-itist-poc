# Conference Participant Registration & Display System

A small serverless web application created for a live conference (Fii IT-ist). It enables real-time participant registration via a simple web form and displays registered names on a dynamic "wall of fame" that updates periodically. The system collects participant name, detects phone model from the User-Agent, and records the client's IP address. It uses AWS serverless primitives for scalability and minimal operational overhead.

Contents
- What this project does
- Key features
- Architecture & components
- API endpoints
- Local development
- Build & deployment
- Configuration & environment
- Running tests
- Notes & troubleshooting

What this project does
- Presents a simple, mobile-friendly registration form at the root URL.
- Accepts form submissions (name) and records metadata (phone model, client IP).
- Pushes form events to an SQS queue and stores request records in DynamoDB.
- Displays a stylized "participants wall" page that polls periodically for changes (mocked locally).

Key Features
- Simple, responsive registration form
- Animated "wall of fame" results page
- Lightweight User-Agent parsing to infer phone model
- Captures client IP address
- Uses Amazon SQS for event processing and DynamoDB for persistent storage
- Packaged and deployed using AWS SAM (Serverless Application Model)

Architecture & components
- AWS Lambda (Python 3.12): request routing and handlers (hello_world/app.py)
- Amazon API Gateway: REST endpoints (configured via template.yaml)
- Amazon SQS: queue for processing submissions
- Amazon DynamoDB: persistent storage for requests / participants
- AWS SAM: infrastructure-as-code and local testing support

Project layout (important files)
- hello_world/ : Lambda application code and templates
  - app.py — main request router (lambda_handler)
  - handlers/ — individual endpoint handlers (home, form, results, default)
  - templates/ — HTML for form and results
  - utils/ — helpers (request parsing, UA phone detection)
  - aws_clients.py / services.py — shared boto3 clients (sqs, dynamodb)
- template.yaml — SAM template (defines Lambda, SQS, DynamoDB)
- samconfig.toml — optional SAM CLI config for deployment
- tests/ — tests and test dependencies
- README.md — this file

API Endpoints
| Method | Endpoint   | Description                                    |
| ------ | ---------- | ---------------------------------------------- |
| GET    | /          | Serve the participant registration form        |
| POST   | /form      | Accept form submission, queue data to SQS      |
| GET    | /results   | Serve the animated wall-of-fame results page   |
| *      | other      | Catch-all handler records requests to SQS/DynamoDB |

Local development

Requirements
- Docker (recommended for `sam build --use-container` and `sam local` commands)
- AWS SAM CLI (latest stable is recommended)
- Python 3.8+ for local development, but Lambda runtime is configured as Python 3.12 in template.yaml
- pip (or poetry/pipenv) to install dependencies
- Optional: AWS CLI & credentials if you interact with real AWS resources

Install runtime/test dependencies
It's recommended to use a virtual environment.

Unix / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hello_world/requirements.txt
pip install -r tests/requirements.txt
```

Windows (PowerShell):
```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r hello_world/requirements.txt
pip install -r tests/requirements.txt
```

Run the API locally
You can run the API locally using the SAM CLI. This emulates API Gateway + Lambda on your machine:

```bash
# Build function artifacts
sam build

# Start the API locally (default port 3000)
sam local start-api
```

Then open:
- Registration form: http://localhost:3000/
- Results page: http://localhost:3000/results

Notes for local testing:
- The results page currently uses mock data (see hello_world/templates/results.html). When backend endpoints are implemented/available, update the frontend to point to the real endpoint.
- If you need to invoke the function directly with a sample event, you can use:
  sam local invoke ProxyFunction -e events/get-root.json

Build & deploy

Build
```bash
sam build
# or, if you need a containerized build for native binaries:
sam build --use-container
```

Deploy (guided)
```bash
sam deploy --guided
```

During `sam deploy --guided`, you'll be prompted for a stack name, AWS region, and whether you want to save the configuration to samconfig.toml. The template requires IAM capabilities to create resources, so respond "y" when asked for CAPABILITY_IAM.

After deployment, outputs include:
- ApiGatewayUrl — base URL for the API
- SQSQueueUrl — URL of the created queue
- DynamoDBTable — table name used for participants/requests

Configuration & environment
The Lambda function expects the following environment variables, which are set in the SAM template on deployment:
- SQS_QUEUE_URL — URL of the SQS queue (set by the stack)
- DYNAMODB_TABLE — DynamoDB table name (set by the stack)

When testing locally, you can either:
- Use the resources created in an AWS account (requires valid AWS credentials), or
- Mock/patch environment variables and AWS clients in your tests.

If you invoke functions locally with `sam local` and you want to access real AWS services from your local environment, ensure your AWS credentials are configured (via the AWS CLI, environment variables, or another supported method).

Running tests

Install test dependencies:
- See the "Install runtime/test dependencies" section above.

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit
```

Run integration tests only:
```bash
pytest tests/integration
```

Notes about tests:
- Integration tests may require access to AWS resources. Set AWS credentials appropriately or run integration tests against a local mock if implemented.
- If integration tests target your locally-running API, start the API before running them:
  sam local start-api

Common troubleshooting & tips
- Permission errors on deploy: ensure you have sufficient IAM permissions and that CAPABILITY_IAM is accepted during deployment.
- Local build failures: try `sam build --use-container` to match the Lambda runtime environment.
- Port conflicts when running `sam local start-api`: the default port is 3000. Use `--port` to change it.
- Lambda runtime mismatch: this template is configured to use Python 3.12. Ensure your code is compatible with that version when deploying to AWS. Locally you can use a different Python version for development, but for binary/native dependencies you should build within a container matching the runtime.

Contributing
- Feel free to open issues or pull requests.
- Keep changes small and focus on clarity and test coverage.
- If adding new dependencies, update hello_world/requirements.txt and document the reason in the PR.

License & acknowledgements
- This repository is a lightweight demo for an event registration and display system. Adapt and reuse as needed.
- Built with AWS SAM and inspired by simple live polling/visualization patterns.

If you need any updates to the README (more deployment details, architecture diagram, or example events), tell me what you'd like added and I'll update this file.
