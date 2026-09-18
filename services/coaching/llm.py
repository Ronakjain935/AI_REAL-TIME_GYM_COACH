import os
import logging
from services.config.workout_config import PROMPT

try:
    from groq import (
        APIError,
        AuthenticationError,
        RateLimitError,
        NotFoundError,
        APIConnectionError,
    )
except ImportError:
    APIError = Exception
    AuthenticationError = Exception
    RateLimitError = Exception
    NotFoundError = Exception
    APIConnectionError = Exception

logger = logging.getLogger(__name__)

DEFAULT_CUES = {
    "workout_started": "Welcome to your workout! Stay focused, maintain form, and let's crush it!",
    "workout_completed": "Fantastic job! Workout complete. Great effort and dedication today!",
    "set_completed": "Set complete! Excellent work. Rest up and prepare for the next set.",
    "no_pose_detected": "Step back into the camera frame so I can track your form.",
    "ongoing_form_check": "Keep your core tight, maintain control, and breathe steadily."
}


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT
        self.model = os.environ.get(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )
        # Secondary fallback model if primary model is unavailable
        self.fallback_model = "llama-3.1-8b-instant"

    def _get_fallback_cue(self, event, issue):
        if issue:
            return f"Watch your form: {issue}. Stay controlled and keep going!"
        return DEFAULT_CUES.get(event, "Great work! Stay consistent and keep moving!")

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        # 1. Primary call with configured model
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
            )
            text = response.choices[0].message.content.strip()
            if text:
                self.history.append({"role": "assistant", "content": text})
                return text

        except NotFoundError as e:
            logger.warning(
                f"Groq model '{self.model}' not found or access denied: {e}. "
                f"Attempting fallback model '{self.fallback_model}'..."
            )
            # Try secondary model if primary model is not accessible
            if self.fallback_model and self.fallback_model != self.model:
                try:
                    response = self.client.chat.completions.create(
                        model=self.fallback_model,
                        messages=messages,
                        temperature=0.4,
                    )
                    text = response.choices[0].message.content.strip()
                    if text:
                        self.history.append({"role": "assistant", "content": text})
                        return text
                except Exception as fallback_err:
                    logger.error(f"Fallback model '{self.fallback_model}' failed: {fallback_err}")

        except AuthenticationError as e:
            logger.error(f"Groq Authentication failed. Verify your GROQ_API_KEY: {e}")

        except RateLimitError as e:
            logger.warning(f"Groq rate limit exceeded: {e}. Using fallback coaching cue.")

        except APIConnectionError as e:
            logger.warning(f"Network/Connection error communicating with Groq: {e}")

        except APIError as e:
            logger.error(f"Groq API error occurred: {e}")

        except Exception as e:
            logger.error(f"Unexpected error generating coach feedback: {e}")

        # 2. Resilient fallback cue ensuring workout session is uninterrupted
        fallback_text = self._get_fallback_cue(event, issue)
        self.history.append({"role": "assistant", "content": fallback_text})
        return fallback_text