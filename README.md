# Conference Participant Registration & Display System

A serverless web application originally built for a live conference ([Fii IT-ist](https://fii-itist.asii.ro/)). The app provides a simple registration form for attendees and a visually engaging "wall of fame" that displays registered participant names. The implementation is serverless (AWS Lambda + API Gateway) and uses SQS for event queuing and DynamoDB for persistent storage.

This repository contains the application code, HTML templates, and SAM infrastructure configuration.

## Key Features

- User registration form (mobile-friendly)
- Animated "wall of fame" results display
- Client-side polling (results page polls every 5 seconds)
- Collects participant name, detected phone model (from User-Agent), and client IP
- Serverless architecture using AWS Lambda, API Gateway, SQS, and DynamoDB
- SAM (Serverless Application Model) template for deployment

## Architecture

![Architecture Diagram](docs/architecture-diagram.png)

Main components:
- AWS Lambda (Python 3.12) – request routing + business logic
- API Gateway – exposes REST endpoints
- Amazon SQS – queue for processing form submissions and other events
- Amazon DynamoDB – persistent storage
- AWS SAM – infrastructure as code (template.yaml)

## Runtime / Dependencies

- Python runtime: 3.12
- Application dependencies are small and listed in `hello_world/requirements.txt` (boto3).
- Tests dependencies are in `tests/requirements.txt` (pytest, boto3, requests).

## API Endpoints

The Lambda function routes requests based on method and path:

- GET `/`  
  Returns the HTML form page (template: hello_world/templates/form.html)

- POST `/form`  
  Processes form submission, performs basic validation, extracts metadata (User-Agent -> phone model, client IP), and sends a message to SQS. The handler is implemented in `hello_world/handlers/form.py`. The Lambda expects the environment variable `SQS_QUEUE_URL` to be set (in SAM this is wired to the queue resource).

- GET `/results`  
  Returns the animated results page (template: hello_world/templates/results.html). Note: the results page currently uses client-side mock data by default (see `USE_MOCK_DATA` flag in the template). A real participants API endpoint (e.g. `/participants`) is not implemented in this codebase — results page is ready to be wired to a backend endpoint later.

- All other requests  
  A catch-all handler (`hello_world/handlers/default.py`) records request info to SQS and stores a record in DynamoDB. This is used for generic telemetry/demo purposes.

Important: There is also `hello_world/handlers/formular.py` which implements the same logic as `form.py` but uses a different import pattern; it is not referenced by the main router (app.lambda_handler). The router only calls `/form`.

## Local Development

You can run and test the API locally using SAM CLI.

1. Install requirements and SAM CLI (see AWS docs for SAM installation).
2. Build:

   ```bash
   sam build --use-container
   ```

3. Run locally:

   ```bash
   sam local start-api
   ```

   By default SAM serves the API at http://localhost:3000. Example:

   - Form page: http://localhost:3000/
   - Submit form (example using curl):
     curl -X POST http://localhost:3000/form -H "Content-Type: application/json" -d '{"name":"Alice"}'

Notes for local invocation:
- `hello_world/events/` contains example API Gateway event samples you can use with `sam local invoke`.
- The results page (`/results`) uses mock data client-side — change the `USE_MOCK_DATA` flag inside `hello_world/templates/results.html` when wiring a real endpoint.

## Deployment

The SAM template is `template.yaml`. Key resources defined:

- ProxyFunction (Lambda) — handler: `hello_world/app.lambda_handler`, runtime python3.12
- TaskQueue (SQS)
- ParticipantsTable (DynamoDB)

Typical deploy workflow:

```bash
# Build
sam build --use-container

# Deploy interactively (creates/updates stack, sets env vars)
sam deploy --guided
```

The SAM template wires environment variables:
- `SQS_QUEUE_URL` → reference to TaskQueue
- `DYNAMODB_TABLE` → reference to ParticipantsTable

After deployment the stack outputs include the ApiGatewayUrl, SQSQueueUrl, and DynamoDB table name.

## Configuration & Environment Variables

Lambda expects the following environment variables (set by SAM template):

- SQS_QUEUE_URL — URL of the SQS queue used to enqueue submissions
- DYNAMODB_TABLE — DynamoDB table name for persistence (used by default handler)

If testing locally, you can override these environment variables via SAM config or your local environment.

## Testing

Unit / integration test helpers are not provided in the repo, but `pytest` can be used to run tests. Install test requirements:

```bash
pip install -r tests/requirements.txt
pytest
```

(There are no tests included by default in this repository; add tests under `tests/unit/` or `tests/integration/` as needed.)

## Implementation Notes & Developer Hints

- Entry point: `hello_world/app.py` — routes requests to handlers:
  - `handlers/home.py` → GET `/` (serves `form.html`)
  - `handlers/form.py` → POST `/form` (sends message to SQS)
  - `handlers/results.py` → GET `/results` (serves `results.html`)
  - `handlers/default.py` → catch-all for other requests (records to SQS and DynamoDB)

- Shared AWS clients are defined in `hello_world/aws_clients.py` (boto3 clients/resources). There is also `hello_world/services.py` which duplicates `aws_clients.py` pattern; `formular.py` imports `services.py` while other handlers import `aws_clients.py`.

- Request helpers:
  - `hello_world/utils/request_helpers.py` contains `lower_headers`, `extract_ip`, and `read_body` used by handlers to normalize headers and read request bodies (handles base64 encoded bodies).

- Phone model detection:
  - `hello_world/utils/phone_detector.py` contains `parse_phone_model(user_agent)` which extracts simple device information (e.g., iPhone, iPad, Android model snippets) from the User-Agent header.

- Results page:
  - `hello_world/templates/results.html` currently uses a client-side mock data generator (USE_MOCK_DATA = true). To connect to a real endpoint, change `API_ENDPOINT` and set `USE_MOCK_DATA = false`. A backend endpoint that returns JSON like `{ "participants": ["Name1", "Name2"] }` is expected.

## Security & Privacy

- The app captures IP addresses and User-Agent strings to extract a simple phone model. If used in production, ensure this data collection complies with event privacy policies and local laws.
- Ensure IAM policies for the Lambda are least-privilege. The SAM template currently grants the Lambda permission to send messages to the SQS queue and write to the DynamoDB table (these are scoped to resources created by the template).

## Files of Interest

- Application code: `hello_world/app.py`, `hello_world/handlers/*.py`, `hello_world/utils/*.py`
- Templates: `hello_world/templates/form.html`, `hello_world/templates/results.html`
- Infrastructure: `template.yaml`, `samconfig.toml`
- Example events: `events/event.json`, `events/get-root.json`

## Contributing

Feel free to open issues or send pull requests. Suggested improvements:
- Implement a real participants HTTP endpoint returning participant lists (to replace mock data in results page)
- Add server-side storage and read APIs for results page with pagination
- Add tests and CI for unit and integration testing
- Add proper input sanitation and rate-limiting for production usage

---

If you need help wiring the results page to a real backend endpoint or adjusting the SAM template/env variables, tell me what you want to change and I can provide specific code or template updates.
