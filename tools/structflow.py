import json
import time
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities import I18nObject, ParameterOption
from dify_plugin.entities.tool import ToolInvokeMessage


class StructFlowTool(Tool):
    POLL_INTERVAL = 5
    MAX_POLL_COUNT = 120

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message("API key is not configured.")
            return

        base_url = self.runtime.credentials.get("base_url", "https://gw.ldxhub.io").rstrip("/")

        headers = {"Authorization": f"Bearer {api_key}"}

        file_obj = tool_parameters.get("file")
        if file_obj is None:
            yield self.create_text_message("File is required.")
            return

        model = tool_parameters.get("model", "google/gemini-3-flash-preview")

        system_prompt = (tool_parameters.get("system_prompt") or "").strip()
        if not system_prompt:
            yield self.create_text_message("system_prompt is required.")
            return

        example_output_str = (tool_parameters.get("example_output") or "").strip()
        if not example_output_str:
            yield self.create_text_message("example_output is required.")
            return
        try:
            example_output = json.loads(example_output_str)
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"example_output is not valid JSON: {e}")
            return

        webhook_url = (tool_parameters.get("webhook_url") or "").strip()
        webhook_secret = (tool_parameters.get("webhook_secret") or "").strip()

        try:
            file_bytes = file_obj.blob
            filename = getattr(file_obj, "filename", "input.jsonl")
        except Exception as e:
            yield self.create_text_message(f"Failed to read input file: {e}")
            return

        # ---- Upload file ----
        yield self.create_text_message("Uploading file to LDX hub...")

        try:
            upload_response = requests.post(
                f"{base_url}/files",
                headers=headers,
                files={"file": (filename, file_bytes)},
                timeout=60,
            )
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            file_id = upload_data.get("file_id")
            if not file_id:
                yield self.create_text_message(f"Upload failed: no file_id returned. Response: {upload_data}")
                return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Failed to upload file: {e}")
            return

        yield self.create_text_message(f"File uploaded (file_id: {file_id}). Starting StructFlow job...")

        # ---- Build job body ----
        job_body = {
            "model": model,
            "system_prompt": system_prompt,
            "example_output": example_output,
            "file_id": file_id,
        }
        if webhook_url:
            job_body["webhook_url"] = webhook_url
            if webhook_secret:
                job_body["webhook_secret"] = webhook_secret

        # ---- Submit job ----
        try:
            job_response = requests.post(
                f"{base_url}/structflow/jobs",
                headers={**headers, "Content-Type": "application/json"},
                json=job_body,
                timeout=60,
            )
            job_response.raise_for_status()
            job_data = job_response.json()
            job_id = job_data.get("job_id")
            if not job_id:
                yield self.create_text_message(f"Job creation failed: {job_data}")
                return
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Failed to create job: {e}")
            return

        # ---- Async mode: return immediately ----
        if webhook_url:
            yield self.create_text_message(
                f"Job submitted in async mode (job_id: {job_id}). "
                f"Completion will be delivered via webhook to: {webhook_url}"
            )
            yield self.create_json_message({
                "job_id": job_id,
                "mode": "async",
                "status": "queued",
                "webhook_url": webhook_url,
            })
            return

        # ---- Sync mode: poll until completion ----
        yield self.create_text_message(f"Job created (job_id: {job_id}). Waiting for completion...")

        output_file_id = None
        for attempt in range(self.MAX_POLL_COUNT):
            time.sleep(self.POLL_INTERVAL)
            try:
                status_response = requests.get(
                    f"{base_url}/structflow/jobs/{job_id}",
                    headers=headers,
                    timeout=30,
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                status = status_data.get("status")

                if status == "completed":
                    output_file_id = status_data.get("output_file_id")
                    yield self.create_text_message("Job completed. Downloading result...")
                    break
                elif status == "failed":
                    error = status_data.get("error") or {}
                    error_msg = error.get("message") or "Job failed without error message"
                    raise Exception(f"Job failed: {error_msg}")
                elif status in ("queued", "processing"):
                    continue
                else:
                    raise Exception(f"Unknown status: {status}")

            except requests.exceptions.RequestException as e:
                yield self.create_text_message(f"Polling error (attempt {attempt + 1}): {e}")
                continue
        else:
            yield self.create_text_message(
                f"Timeout: job did not complete within {self.POLL_INTERVAL * self.MAX_POLL_COUNT} seconds. "
                f"You can check status manually with job_id: {job_id}"
            )
            return

        if not output_file_id:
            yield self.create_text_message("Job completed but no output_file_id returned.")
            return

        # ---- Download result ----
        try:
            download_response = requests.get(
                f"{base_url}/files/{output_file_id}/content",
                headers=headers,
                timeout=60,
            )
            download_response.raise_for_status()
            result_bytes = download_response.content
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Failed to download result: {e}")
            return

        # ---- Build output filename ----
        if filename.endswith(".jsonl"):
            base = filename[: -len(".jsonl")]
            output_filename = f"{base}.structured.jsonl"
        else:
            output_filename = f"{filename}.structured.jsonl"

        yield self.create_blob_message(
            blob=result_bytes,
            meta={
                "mime_type": "application/x-ndjson",
                "filename": output_filename,
            },
        )

        yield self.create_json_message({
            "job_id": job_id,
            "output_file_id": output_file_id,
            "mode": "sync",
            "status": "completed",
        })

    def _fetch_parameter_options(self, parameter: str) -> list[ParameterOption]:
        # Dynamically populate the model dropdown from the LDX hub models API.
        if parameter != "model":
            return []

        # Static fallback, used only when the models API cannot be reached.
        fallback = [
            ("google/gemini-3-flash-preview", "Google Gemini 3 Flash Preview"),
            ("openai/gpt-5.5", "OpenAI GPT-5.5"),
            ("anthropic/claude-opus-4-8", "Claude Opus 4.8"),
            ("google/gemini-3.5-flash", "Google Gemini 3.5 Flash"),
        ]

        api_key = self.runtime.credentials.get("api_key")
        base_url = self.runtime.credentials.get("base_url", "https://gw.ldxhub.io").rstrip("/")

        if api_key:
            try:
                response = requests.get(
                    f"{base_url}/structflow/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )
                response.raise_for_status()
                options = [
                    ParameterOption(
                        value=item["id"],
                        label=I18nObject(en_US=item.get("display_name") or item["id"]),
                    )
                    for item in response.json().get("data", [])
                    if item.get("id")
                ]
                if options:
                    return options
            except Exception:
                pass

        return [
            ParameterOption(value=value, label=I18nObject(en_US=label))
            for value, label in fallback
        ]
