import json
import sys
import time
import requests
from datetime import datetime, timedelta
import urllib3

def agents_ip(role):
    with open("/workspace/agents.json") as f:
        data = json.load(f)
    return [item for item in data if role in item.get("roles")]

prometheus = agents_ip("prometheus")[0].get("host")

PROMETHEUS_URL = f"https://{prometheus}:9091"
PROMETHEUS_AUTH = ("admin", "admin")
TIMEOUT = 3 * 60  # Timeout after 3 minutes (in seconds)

# Suppress InsecureRequestWarning if verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check(job, status, count):
    start_time = datetime.now()
    timeout_time = start_time + timedelta(seconds=TIMEOUT)

    while datetime.now() < timeout_time:
        try:
            # Fetch targets from Prometheus
            response = requests.get(f"{PROMETHEUS_URL}/api/v1/targets", verify=False, auth=PROMETHEUS_AUTH)
            response.raise_for_status()  # Raise an exception for bad responses
            targets = response.json()["data"]["activeTargets"]

            # Filter targets matching the job and status
            matching_targets = [{"job": target["labels"].get("job"), "health": target["health"]}  for target in targets if target["labels"].get("job") == job and target["health"] == status]

            print(f"All {count} targets with job '{job}' have the expected status '{status}', found {len(matching_targets)}")

            if len(matching_targets) == count:
                print(f"All {count} targets with job '{job}' have the expected status '{status}'.")
                return True
        except requests.RequestException as e:
            print(f"Request error: {e}")
        except KeyError as e:
            print(f"Unexpected response format: {e}")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1)  # Wait 1 second before retrying

    raise TimeoutError(f"Timeout: Job '{job}' did not reach status '{status}' for {count} target(s) within {TIMEOUT//60} minutes.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <job> <status> <count>")
        sys.exit(1)

    job = sys.argv[1]
    status = sys.argv[2]
    try:
        count = int(sys.argv[3])
    except ValueError:
        print("Error: count must be an integer.")
        sys.exit(1)

    try:
        check(job, status, count)
    except TimeoutError as e:
        print(e)
        sys.exit(1)
