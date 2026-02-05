import urllib.request
import json

def get_latest_filename():
    try:
        url = "https://terraria.org/api/get/dedicated-servers-names"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8')

        parsed_data = json.loads(data)

        if isinstance(parsed_data, list) and parsed_data:
            return parsed_data[0]
        else:
            raise ValueError("Unexpected data format")
        
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"Error fetching latest filename: {e}")
        return None

if __name__ == "__main__":
    print(get_latest_filename())