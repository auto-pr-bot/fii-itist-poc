"""Helper functions for processing API Gateway requests."""
import base64


def lower_headers(headers: dict | None) -> dict:
    """Convert all header keys to lowercase for case-insensitive lookup."""
    if not headers:
        return {}
    return {str(k).lower(): v for k, v in headers.items()}


def extract_ip(event: dict) -> str | None:
    """Extract the client IP address from the API Gateway event."""
    headers = lower_headers(event.get('headers'))
    xff = headers.get('x-forwarded-for')
    if xff:
        ip = xff.split(',')[0].strip()
        if ip:
            return ip
    try:
        return event.get("requestContext", {}).get("identity", {}).get("sourceIp")
    except Exception:
        return None


def read_body(event: dict) -> str:
    """Read and decode the request body, handling base64 encoding if present."""
    body = event.get('body', '')
    if event.get('isBase64Encoded') and body:
        try:
            return base64.b64decode(body).decode('utf-8', errors='replace')
        except Exception:
            return ''
    return body or ''
