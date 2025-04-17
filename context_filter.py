import json
from json import JSONDecodeError

# … inside your try: after
analysis_raw = invoke_custom_api(TKD_NAME, email_body, system_prompt)
logger.debug(f"Raw custom API response (first 200 chars): {analysis_raw[:200]}…")

# Attempt to parse it as JSON:
try:
    analysis_obj = json.loads(analysis_raw)
    # Remove the "context" key if present:
    filtered_analysis = {
        k: v for k, v in analysis_obj.items() if k != "context"
    }
except JSONDecodeError:
    # If it wasn’t JSON, just log the raw string
    filtered_analysis = analysis_raw

logger.debug(f"Filtered analysis (no context): {filtered_analysis}")

# Then when you assemble the result to return, you can still use the full analysis_obj
# or just re‑embed filtered_analysis, depending on whether you want to send context
# back to the client or not.
result = {
    "metadata": email_data.get("metadata", {}),
    "analysis": analysis_obj  # or filtered_analysis
}
logger.debug(f"Assembled result: {{'metadata': …, 'analysis': { {k:v for k,v in result['analysis'].items() if k!='context'} } }}")
