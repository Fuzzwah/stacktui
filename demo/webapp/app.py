"""Minimal Flask web app for the StackTUI demo."""

import logging
import time

from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [webapp] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


@app.route("/")
def index() -> str:
    log.info("GET /")
    return (
        "<h1>StackTUI Demo</h1>"
        "<p>This is a minimal web app used to demonstrate "
        "<a href='https://github.com/fuzzwah/stacktui'>StackTUI</a>.</p>"
        "<p>Try tailing this service's logs in the dashboard.</p>"
    )


@app.route("/health")
def health():
    return jsonify(status="ok", time=time.time())
