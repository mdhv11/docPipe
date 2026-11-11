import json
import subprocess
from pathlib import Path


class LlamaCppClient:
    def __init__(self, binary_path: str, model_path: str, n_predict: int = 1024, temp: float = 0.2):
        self.binary_path = binary_path
        self.model_path = model_path
        self.n_predict = n_predict
        self.temp = temp

    def run(self, prompt: str) -> str:
        if not Path(self.binary_path).exists():
            raise FileNotFoundError(f"llama.cpp binary not found at {self.binary_path}")
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"llama.cpp model not found at {self.model_path}")

        command = [
            self.binary_path,
            "-m",
            self.model_path,
            "--temp",
            str(self.temp),
            "-n",
            str(self.n_predict),
            "--repeat-penalty",
            "1.1",
            "-no-cnv",
            "--prompt",
            prompt,
        ]

        result = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
        return result.strip()

    def build_document_prompt(self, ocr_text: str, filename: str) -> str:
        return (
            "You are a document reconstruction assistant. "
            "Given raw OCR text from a scanned document, produce only valid JSON with the following schema:\n"
            "{\n"
            "  \"title\": string,\n"
            "  \"sections\": [\n"
            "    {\n"
            "      \"heading\": string,\n"
            "      \"content\": [\n"
            "        {\"type\": \"paragraph\", \"text\": string},\n"
            "        {\"type\": \"bullet_list\", \"items\": [string]},\n"
            "        {\"type\": \"table\", \"rows\": [[string]]}\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "Use the filename as context. Do not include any markdown or explanation. "
            "If the text contains no clear title, use an empty string for title. "
            "Keep table rows as arrays of strings. "
            "Return exactly one JSON object.\n\n"
            f"Filename: {filename}\n"
            "OCR_TEXT:\n"
            f"{ocr_text}\n"
        )
