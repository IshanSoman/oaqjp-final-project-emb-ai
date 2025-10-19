"""Emotion detection wrapper around the Watson NLP EmotionPredict endpoint."""

from typing import Dict, Optional
import json
import requests
def emotion_detector(text_to_analyze: str) -> Dict[str, Optional[float]]:
    """
    Send text to the Watson EmotionPredict endpoint and return a dict with
    the 5 scores and the dominant emotion.

    If the server returns HTTP 400 (bad request), return a dictionary where
    all numeric values and dominant_emotion are None.
    """
    url = (
        "https://sn-watson-emotion.labs.skills.network"
        "/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
    )

    headers = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}
    payload = {"raw_document": {"text": text_to_analyze}}

    try:
        response = requests.post(url, headers=headers, json=payload)
    except requests.RequestException:
        # Network or DNS error — return None values
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    # If the service responded with 400 -> invalid/blank input per instructions
    if response.status_code == 400:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    # If any other non-200 status, try to handle gracefully
    if response.status_code != 200:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    # Parse JSON
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    # Navigate to expected structure. If keys don't exist, return None-values.
    try:
        # The API returns a list under 'emotionPredictions'; adjust if structure differs.
        emotions_block = data["emotionPredictions"][0]["emotion"]
        anger_score = float(emotions_block.get("anger", 0.0))
        disgust_score = float(emotions_block.get("disgust", 0.0))
        fear_score = float(emotions_block.get("fear", 0.0))
        joy_score = float(emotions_block.get("joy", 0.0))
        sadness_score = float(emotions_block.get("sadness", 0.0))
    except (KeyError, IndexError, TypeError, ValueError):
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    emotion_scores = {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score,
    }

    # Determine dominant emotion (the key with highest score)
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)

    result = {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score,
        "dominant_emotion": dominant_emotion,
    }

    return result
