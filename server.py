"""Flask web server exposing the emotionDetector route."""

from typing import Dict
from flask import Flask, render_template, request
from markupsafe import Markup
from EmotionDetection import emotion_detector

APP = Flask(__name__)


def _format_response_text(result: Dict[str, float]) -> str:
    """
    Convert the result dictionary into the required sentence format.

    Example:
    For the given statement, the system response is 'anger': 0.006..., 'disgust': ...
    The dominant emotion is joy.
    """
    # If dominant is None, return the invalid message upstream
    if result.get("dominant_emotion") is None:
        return "Invalid text! Please try again!"

    # Build the 5-score snippet
    snippet = (
        f"'anger': {result['anger']}, "
        f"'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, "
        f"'joy': {result['joy']} and "
        f"'sadness': {result['sadness']}."
    )

    return (
        f"For the given statement, the system response is {snippet} "
        f"The dominant emotion is {result['dominant_emotion']}."
    )


@APP.route("/emotionDetector", methods=["GET", "POST"])
def emotion_detector_route() -> str:
    """
    Handle web requests for emotion detection.

    The frontend (index.html) posts the field 'text' (or query param 'text'),
    we run emotion_detector(), then format and return the human-friendly sentence.
    """
    text_to_analyze = ""
    if request.method == "POST":
        # try form first, then JSON payload, then args
        text_to_analyze = request.form.get("text", "").strip()
        if not text_to_analyze:
            # Try JSON
            try:
                json_payload = request.get_json(silent=True) or {}
                text_to_analyze = (json_payload.get("text") or "").strip()
            except Exception:
                text_to_analyze = ""
    else:
        text_to_analyze = request.args.get("text", "").strip()

    # Call the emotion detector
    result = emotion_detector(text_to_analyze)

    # Build the response string
    response_text = _format_response_text(result)

    # If you have an index.html expecting insertion, render it; otherwise return plain text.
    # We'll return a simple HTML page with the response embedded.
    return render_template("index.html", result=Markup(response_text))


if __name__ == "__main__":
    # host 0.0.0.0 for container, port 5000 as required
    APP.run(host="0.0.0.0", port=5000, debug=False)
