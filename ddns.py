import subprocess
import yaml
import requests
import time


def get_secrets():
    try:
        result = subprocess.run(
            ["sops", "-d", "secrets.enc.yaml"], capture_output=True, text=True, check=True)
        secrets = yaml.safe_load(result.stdout)
        return (secrets["cloudflare_api_key"], secrets["domain"], secrets["zone_id"])
    except subprocess.CalledProcessError as e:
        print(f"Error decrypting secrets: {e}")
        return None


API_KEY, RECORD_NAME, ZONE_ID = get_secrets()
CF_API_BASE = "https://api.cloudflare.com/client/v4"
IP_CHECK_URL = "https://api.ipify.org"


def get_current_ip():
    return requests.get(IP_CHECK_URL).text


def update_dns_record(ip):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "type": "A",
        "name": RECORD_NAME,
        "content": ip,
        "ttl": 1,
        "proxied": False,
    }

    response = requests.get(
        f"{CF_API_BASE}/zones/{ZONE_ID}/dns_records", headers=headers)
    records = response.json()["result"]

    record_id = None
    for record in records:
        if record["name"] == RECORD_NAME:
            record_id = record["id"]
            break

    if record_id:
        response = requests.put(
            f"{CF_API_BASE}/zones/{ZONE_ID}/dns_records/{record_id}", headers=headers, json=data)
    else:
        response = requests.post(
            f"{CF_API_BASE}/zones/{ZONE_ID}/dns_records", headers=headers, json=data)

    return response.status_code == 200


def main():
    last_ip = None
    while True:
        current_ip = get_current_ip()
        if current_ip != last_ip:
            if update_dns_record(current_ip):
                last_ip = current_ip
        time.sleep(300)


if __name__ == "__main__":
    main()
