import random
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests import RequestException


USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
]


def build_headers(extra_headers=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if extra_headers:
        headers.update(extra_headers)
    return headers


def is_allowed_by_robots(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)

    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        raise ValueError(f"robots.txt 확인 실패: {robots_url} / {e}")


def get_with_retry(
    url: str,
    headers=None,
    retries: int = 3,
    min_delay: float = 1.0,
    max_delay: float = 3.0,
    timeout: int = 10,
):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            time.sleep(random.uniform(min_delay, max_delay))

            response = requests.get(
                url,
                headers=build_headers(headers),
                timeout=timeout,
            )
            response.raise_for_status()
            return response

        except RequestException as e:
            last_error = e
            if attempt < retries:
                time.sleep(2 * attempt)
            else:
                raise last_error


def fetch_page(url: str, timeout: int = 15) -> requests.Response:
    if not is_allowed_by_robots(url):
        raise ValueError(f"robots.txt 정책상 수집 불가 URL입니다: {url}")

    return get_with_retry(
        url=url,
        timeout=timeout,
        retries=3,
        min_delay=1.0,
        max_delay=3.0,
    )
