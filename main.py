import requests
import time
import sys
import json

def check_vanity_url(vanity_url, proxy):
    url = f"https://discord.com/api/v9/invites/{vanity_url}"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 404:
            return "Available"
        elif response.status_code == 200:
            return "Taken"
        elif response.status_code == 403:
            return "Banned"
        else:
            return "Failed"
    except requests.exceptions.RequestException:
        return "Failed"

def update_progress(progress, sent_count):
    bar_length = 40
    filled_length = int(bar_length * progress // 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\rProgress: |{0}| {1}% | Sent: {2}'.format(bar, progress, sent_count))
    sys.stdout.flush()

def load_proxies(file_directory):
    proxies = []
    with open(file_directory, "r") as file:
        lines = file.readlines()
        for line in lines:
            proxy = line.strip()
            proxies.append({'http': proxy, 'https': proxy})
    return proxies

def send_to_webhook(webhook_url, message):
    headers = {"Content-Type": "application/json"}
    payload = {
        "embeds": [
            {
                "title": "Available Vanity's",
                "description": message,
                "color": 65280
            }
        ]
    }
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def main():
    print("╔══════════════════════════════════╗")
    print("║      Discord Vanity Checker      ║")
    print("╚══════════════════════════════════╝")
    print("[+] Made by srry")
    print("[+] Srryx on Github")
    print("------------------------------------")

    proxy_file_directory = input("Enter proxy file directory (no proxy, leave blank): ")
    proxies = []
    if proxy_file_directory:
        proxies = load_proxies(proxy_file_directory)

    webhook_url = input("Enter Discord webhook URL (no webhook, leave blank): ")

    file_directory = input("Enter vanity directory: ")
    print("Checking vanity URLs...")

    with open(file_directory, "r") as file:
        links = file.readlines()

    total_urls = len(links)
    checked_urls = 0
    failed_urls = []
    taken_urls = []
    available_urls = []
    sent_count = 0

    for link in links:
        word = link.strip().split("/")[-1]
        result = "Failed"
        for proxy in proxies:
            result = check_vanity_url(word, proxy)
            if result != "Failed":
                break

        if result == "Failed":
            failed_urls.append(link.strip())
        elif result == "Taken":
            taken_urls.append(link.strip())
        elif result == "Available":
            available_urls.append(link.strip())
            if webhook_url:
                message = f"The vanity **{link.strip()}** is available!"
                if send_to_webhook(webhook_url, message):
                    sent_count += 1

        checked_urls += 1
        progress = int((checked_urls / total_urls) * 100)
        update_progress(progress, sent_count)
        time.sleep(0.1)

    with open("results.txt", "w") as file:
        file.write("--- Failed Vanity's ---\n\n")
        file.write("\n".join(failed_urls))
        file.write("\n\n--- Taken Vanity's ---\n\n")
        file.write("\n".join(taken_urls))
        file.write("\n\n--- Available Vanity's ---\n\n")
        file.write("\n".join(available_urls))

    print("\nResults saved to 'results.txt'.")
    input("Press Enter to exit.")

if __name__ == "__main__":
    main()
