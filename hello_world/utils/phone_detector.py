"""Phone model detection from User-Agent strings."""
import re

_ANDROID_MODEL_RE = re.compile(r"Android [^;\)]*;\s*([^;\)]+)")


def parse_phone_model(user_agent: str | None) -> str:
    """
    Extract phone model information from User-Agent string.
    
    Args:
        user_agent: The User-Agent header value
        
    Returns:
        Detected phone model or generic type (iPhone/iPad/Mobile/Unknown)
    """
    if not user_agent:
        return "Unknown"
    
    ua = user_agent
    
    # iOS devices
    if "iPhone" in ua:
        return "iPhone"
    if "iPad" in ua:
        return "iPad"
    
    # Android - extract model from standard format
    m = _ANDROID_MODEL_RE.search(ua)
    if m:
        model = m.group(1).strip().split(" Build")[0].strip()
        return model
    
    # Common Android brands - fallback detection
    for brand in ["Pixel", "Nexus", "Huawei", "HUAWEI", "OnePlus", "SM-", "M200", "Redmi", "Mi "]:
        if brand in ua:
            idx = ua.find(brand)
            snippet = ua[idx: idx + 32]
            return snippet.split(";")[0].split(")")[0]
    
    return "Mobile"
