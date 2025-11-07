"""Handler for GET / - returns the HTML form page."""
import os


def handle_home(event: dict, context) -> dict:
    """
    Handle GET / requests.
    
    Returns the HTML form page for user input.
    """
    # Read the HTML template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'form.html')
    with open(template_path, 'r') as f:
        html_content = f.read()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        },
        'body': html_content
    }
