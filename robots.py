import requests
from urllib.parse import urlparse

def can_fetch(url, user_agent="*"):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            return True  # Si no se encuentra robots.txt, permitimos el rastreo
        robots_txt = response.text
        return check_robots_txt(robots_txt, parsed_url.path, user_agent)
    except requests.RequestException:
        return True  # Si hay un problema al obtener robots.txt, permitimos el rastreo

def check_robots_txt(robots_txt, path, user_agent):
    lines = robots_txt.splitlines()
    user_agent_line = False
    for line in lines:
        line = line.strip()
        if line.startswith("User-agent:"):
            user_agent_line = line.split(":")[1].strip() == user_agent or line.split(":")[1].strip() == "*"
        elif user_agent_line and line.startswith("Disallow:"):
            disallow_path = line.split(":")[1].strip()
            if path.startswith(disallow_path):
                return False
    return True
