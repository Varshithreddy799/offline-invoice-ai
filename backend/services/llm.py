import json
import logging
import multiprocessing
from pathlib import Path
from typing import Generator

from config import DEFAULT_MODEL_PATH, MODEL_CONTEXT, MODEL_THREADS, USE_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Extract invoice data from OCR text.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.
If a field is missing, return an empty string.
"""

JSON_TEMPLATE = """
{
    "vendor": "",
    "invoice_number": "",
    "invoice_date": "",
    "items": [
        {
            "name": "",
            "quantity": "",
            "unit_price": "",
            "total": ""
        }
    ],
    "subtotal": "",
    "tax": "",
    "grand_total": "",
    "payment_method": ""
}
"""


class LLMService:
    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        context_size: int = MODEL_CONTEXT,
        threads: int = MODEL_THREADS,
    ):
        self.model_path = Path(model_path)
        self.context_size = context_size
        self.threads = threads if threads > 0 else multiprocessing.cpu_count()
        self.model = None
        if USE_MODEL:
            self._load_model()
        else:
            logger.info("LLM model loading disabled via USE_MODEL=false")

    def _load_model(self):
        if not self.model_path.exists():
            logger.warning(f"Model not found at {self.model_path}")
            return

        try:
            from llama_cpp import Llama

            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=self.context_size,
                n_threads=self.threads,
                n_gpu_layers=0,
                verbose=False,
            )

            logger.info(f"Loaded model: {self.model_path}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    @property
    def is_loaded(self):
        return self.model is not None

    def _build_prompt(self, ocr_text: str) -> str:
        return f"""<|system|>
    You are an invoice extraction assistant.

    Extract the invoice into valid JSON.

    Return ONLY JSON.

    <|user|>

    OCR TEXT

    {ocr_text}

    Return this exact JSON structure:

    {{
        "vendor":"",
        "invoice_number":"",
        "invoice_date":"",
        "items":[
            {{
                "name":"",
                "quantity":"",
                "unit_price":"",
                "total":""
            }}
        ],
        "subtotal":"",
        "tax":"",
        "grand_total":"",
        "payment_method":""
    }}

    <|assistant|>
    """

    def _clean_json(self, text: str) -> str:
        text = text.strip()

        start = text.find("{")
        if start == -1:
            return text

        depth = 0

        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return text[start:]

    def _validate_structure(self, data: dict):
        required = [
            "vendor",
            "invoice_number",
            "invoice_date",
            "items",
            "subtotal",
            "tax",
            "grand_total",
            "payment_method",
        ]

        for key in required:
            if key not in data:
                data[key] = [] if key == "items" else ""

        if not isinstance(data["items"], list):
            data["items"] = []

        for item in data["items"]:
            for field in [
                "name",
                "quantity",
                "unit_price",
                "total",
            ]:
                if field not in item:
                    item[field] = ""

    def extract(self, ocr_text: str, max_retries: int = 3):

        if not self.is_loaded:
            return {
                "error": "Model not loaded. Place a GGUF model in the models/ directory or set USE_MODEL=false."
            }

        if not ocr_text or not ocr_text.strip():
            return {
                "error": "Empty OCR text provided"
            }

        prompt = self._build_prompt(ocr_text)

        logger.info("=" * 80)
        logger.info("PROMPT")
        logger.info(prompt)
        logger.info("=" * 80)

        for attempt in range(max_retries):

            try:

                output = self.model.create_completion(
                    prompt=prompt,
                    max_tokens=512,
                    temperature=0,
                    echo=False,
                )

                raw = output["choices"][0]["text"]

                logger.info("=" * 80)
                logger.info("RAW OUTPUT")
                logger.info(repr(raw))
                logger.info("=" * 80)

                cleaned = self._clean_json(raw)

                logger.info("=" * 80)
                logger.info("CLEANED OUTPUT")
                logger.info(repr(cleaned))
                logger.info("=" * 80)

                if cleaned.strip() == "":
                    raise ValueError("LLM returned an empty response.")

                result = json.loads(cleaned)

                self._validate_structure(result)

                return result

            except json.JSONDecodeError as e:

                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} - JSON decode failed: {e}"
                )

                if attempt == max_retries - 1:
                    return {
                        "error": "Could not parse model output.",
                        "raw": raw if "raw" in locals() else ""
                    }

            except Exception as e:

                logger.error(f"Attempt {attempt + 1}: {e}")

                if attempt == max_retries - 1:
                    return {
                        "error": str(e),
                        "raw": raw if "raw" in locals() else ""
                    }

        return {
            "error": "Unknown error."
    }

    def extract_stream(self, ocr_text: str) -> Generator[str, None, None]:

        if not self.is_loaded:
            yield json.dumps({"error": "Model not loaded"})
            return

        prompt = self._build_prompt(ocr_text)

        for output in self.model.create_completion(
            prompt=prompt,
            max_tokens=1024,
            temperature=0.1,
            stop=["###"],
            stream=True,
        ):

            token = output["choices"][0].get("text", "")

            if token:
                yield token
