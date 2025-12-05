# Conference Participant Registration & Display System

A serverless web application built for a live conference ([Fii IT-ist](https://fii-itist.asii.ro/)), enabling real-time participant registration with an engaging visual display. The system collects participant information through a web form and displays registered names on a dynamic "wall of fame" that updates in real-time during the event.

## Key Features

- **User Registration Form**: Clean, mobile-responsive interface for attendees to submit their names
- **Dynamic Results Display**: Kahoot-style animated wall of fame with real-time updates
- **Real-time Polling**: Results page auto-refreshes every 5 seconds to show new participants
- **Data Collection**: Captures participant name, phone model (via User-Agent parsing), and IP address
- **Serverless Architecture**: Fully scalable AWS infrastructure with zero server management
- **Dual Storage**: SQS queue for event processing + DynamoDB for persistent storage

## Architecture

Built using AWS Serverless technologies:

- **AWS Lambda** (Python 3.12): Request routing and business logic
- **API Gateway**: RESTful API endpoints
- **Amazon SQS**: Message queue for asynchronous event processing
- **Amazon DynamoDB**: NoSQL database for participant data storage
- **AWS SAM**: Infrastructure as Code for deployment

## API Endpoints

| Method | Endpoint   | Description                                    |
| ------ | ---------- | ---------------------------------------------- |
| `GET`  | `/`        | Displays participant registration form         |
| `POST` | `/form`    | Processes form submission, queues data to SQS  |
| `GET`  | `/results` | Shows animated wall of registered participants |

## Deployment

### Build and Deploy

```bash
# Build the application
sam build --use-container

# Deploy with guided configuration
sam deploy --guided
```

### Local Development

Run the API locally for testing:

```bash
# Start local API server
sam local start-api

# Access endpoints
curl http://localhost:3000/
```

## Running tests

This project uses pytest for tests. The test dependencies are listed in tests/requirements.txt.

Prerequisites:
- Python 3.8+ (the project uses Python 3.12 for Lambda, but tests run with any supported Python 3)
- pip
- (Optional) virtualenv or venv to isolate dependencies
- AWS credentials/config if running integration tests that interact with AWS services

Install test dependencies (recommended inside a virtual environment)

Unix / macOS:

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r tests/requirements.txt
```

Windows (PowerShell):

```powershell
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1

pip install -r tests/requirements.txt
```

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

Notes:
- Integration tests may require AWS credentials (for example via environment variables, AWS CLI configuration, or an AWS profile). If they interact with a locally running API, start the local API before running integration tests:

```bash
sam local start-api
```

- To run a single test function:

```bash
pytest path/to/test_file.py::test_function_name
```

- You can pass standard pytest options as needed (e.g., -q for quiet, -k to filter by substring, -x to stop after first failure).

If you encounter dependency or environment issues, ensure the virtual environment is activated and the test dependencies from tests/requirements.txt are installed.
