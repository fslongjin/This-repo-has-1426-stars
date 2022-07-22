import os
import re
import json
import hmac
import hashlib
import requests

from dotenv import load_dotenv
from flask import Flask, request

from .logging import init_logging

load_dotenv()

app = Flask(__name__)
log = init_logging("DEBUG")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", None)
REPO_URL = os.getenv("REPO_URL", None)

REPO_INFO = re.search(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)",
    REPO_URL,
)

if not GITHUB_TOKEN and not WEBHOOK_SECRET and not REPO_URL and REPO_INFO is None:
    raise ValueError("GITHUB_WEBHOOK_SECRET is not set")

API_REPO_URL = (
    "https://api.github.com/repos/{owner}/{repo}".format_map(  # noqa: E501,F523,F524
        REPO_INFO.groupdict()
    )
)


def edit_repo(stargazers_count: int) -> None:
    log.info(f"Edit repo: {stargazers_count}")
    requests.patch(
        API_REPO_URL,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}",
        },
        data=json.dumps(
            dict(
                name=f"This-repo-has-{stargazers_count}-stars",
                description=f"这个仓库有{stargazers_count}个star，不信你试试",
            )
        ),
    )


@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        headers = request.headers
        data = request.get_json()

        if not headers.get("User-Agent", "").startswith("GitHub-Hookshot/"):
            return "not is github hook", 400

        event_name = headers.get("x-github-event", None)
        signature = headers.get("x-hub-signature-256", None)

        generate_signature = hmac.new(
            bytes(WEBHOOK_SECRET, "utf-8"),
            bytes(json.dumps(data, separators=(",", ":"), ensure_ascii=False), "utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if f"sha256={generate_signature}" != signature:
            log.error(
                "signature mismatch"
                f" signature={signature!r}"
                f" generate_signature={generate_signature!r}"
            )
            return "signature not match", 403

        log.debug(f"webhook_event: {event_name}")

        if event_name == "star":
            edit_repo(data["repository"]["stargazers_count"])

        return "ok", 200
    return "ok", 200


if __name__ == "__main__":
    log.debug(API_REPO_URL)

    data = requests.get(API_REPO_URL)
    edit_repo(data.json()["stargazers_count"])

    app.run()
