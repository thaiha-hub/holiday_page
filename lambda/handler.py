import datetime
import json
import urllib.request
import urllib.error


DAGSMART_BASE_URL = "https://api.dagsmart.se"


def fetch_dagsmart(endpoint: str, year: int):
    url = f"{DAGSMART_BASE_URL}/{endpoint}?year={year}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.URLError as error:
        print(f"Error calling Dagsmart API: {error}")
        return []


def normalize_items(data):
    """
    This helper makes the Lambda more tolerant if the API response shape changes.
    It tries to return a list of dictionaries.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["data", "items", "holidays", "halfDays", "bridgeDays"]:
            if key in data and isinstance(data[key], list):
                return data[key]

    return []


def find_items_for_date(items, today_iso):
    matches = []

    for item in items:
        if not isinstance(item, dict):
            continue

        item_date = item.get("date") or item.get("datum")

        if item_date == today_iso:
            name = (
                item.get("name")
                or item.get("title")
                or item.get("namn")
                or item.get("description")
                or json.dumps(item, ensure_ascii=False)
            )
            matches.append(name)

    return matches


def lambda_handler(event, context):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    today_iso = today.isoformat()
    year = today.year

    holidays_data = normalize_items(fetch_dagsmart("holidays", year))
    half_days_data = normalize_items(fetch_dagsmart("half-days", year))
    bridge_days_data = normalize_items(fetch_dagsmart("bridge-days", year))

    result = {
        "date": today_iso,
        "holidays": find_items_for_date(holidays_data, today_iso),
        "halfDays": find_items_for_date(half_days_data, today_iso),
        "bridgeDays": find_items_for_date(bridge_days_data, today_iso),
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://d1bkeswoec9ca5.cloudfront.net",
        },
        "body": json.dumps(result, ensure_ascii=False),
    }