#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "pillow",
# ]
# ///
"""
Generate images using Google's Gemini image models (Nano Banana family).

Usage:
    uv run generate_image.py --prompt "A colorful abstract pattern" --output "./hero.png"
    uv run generate_image.py --prompt "Minimalist icon" --output "./icon.png" --aspect landscape
    uv run generate_image.py --prompt "Similar style image" --output "./new.png" --reference "./existing.png"
    uv run generate_image.py --prompt "Blend these styles" --output "./new.png" --reference "./a.png" --reference "./b.png"
    uv run generate_image.py --prompt "High quality art" --output "./art.png" --model pro --size 2K
    uv run generate_image.py --prompt "Fast high-res" --output "./fast.png" --model 2 --size 2K --aspect 4:3

Batch mode — uses the Gemini Batch API (async, 50% cost, up to 24h turnaround):
    uv run generate_image.py --batch-input jobs.jsonl

Each line in the JSONL file must be a JSON object with keys:
    prompt     (required)  - image description
    output     (required)  - output file path
    aspect     (optional)  - aspect ratio, default "square"
    model      (optional)  - model name, default "2"
    size       (optional)  - image size, default "1K"
    references (optional)  - list of reference image paths
"""

import argparse
import base64
import json
import os
import sys
import tempfile
import time

from google import genai
from google.genai import types
from PIL import Image

MODEL_IDS = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
    "2": "gemini-3.1-flash-image-preview",
}

# Named shortcuts for common aspect ratios
ASPECT_ALIASES = {
    "square": "1:1",
    "landscape": "16:9",
    "portrait": "9:16",
}

# All valid aspect ratios (Nano Banana 2 superset)
ALL_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
    "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

# Aspect ratios supported per model
MODEL_ASPECT_RATIOS = {
    "flash": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
    "pro": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
    "2": ALL_ASPECT_RATIOS,
}


def resolve_aspect(aspect: str) -> str:
    """Resolve a named alias or direct ratio string to a ratio string."""
    return ASPECT_ALIASES.get(aspect, aspect)


def get_aspect_instruction(aspect_ratio: str) -> str:
    """Return aspect ratio instruction for the prompt."""
    descriptions = {
        "1:1": "Generate a square image (1:1 aspect ratio).",
        "1:4": "Generate a tall narrow image (1:4 aspect ratio).",
        "1:8": "Generate a very tall narrow image (1:8 aspect ratio).",
        "2:3": "Generate a tall image (2:3 aspect ratio).",
        "3:2": "Generate a wide image (3:2 aspect ratio).",
        "3:4": "Generate a tall image (3:4 aspect ratio).",
        "4:1": "Generate a wide panoramic image (4:1 aspect ratio).",
        "4:3": "Generate a landscape image (4:3 aspect ratio).",
        "4:5": "Generate a slightly tall image (4:5 aspect ratio).",
        "5:4": "Generate a slightly wide image (5:4 aspect ratio).",
        "8:1": "Generate a very wide panoramic image (8:1 aspect ratio).",
        "9:16": "Generate a portrait/tall image (9:16 aspect ratio).",
        "16:9": "Generate a landscape/wide image (16:9 aspect ratio).",
        "21:9": "Generate an ultrawide image (21:9 aspect ratio).",
    }
    return descriptions.get(aspect_ratio, f"Generate an image with {aspect_ratio} aspect ratio.")


def generate_image(
    prompt: str,
    output_path: str,
    aspect: str = "square",
    references: list[str] | None = None,
    model: str = "2",
    size: str = "1K",
    client: "genai.Client | None" = None,
) -> None:
    """Generate an image using Gemini and save to output_path."""
    if client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
            sys.exit(1)
        client = genai.Client(api_key=api_key)

    aspect_ratio = resolve_aspect(aspect)

    # Validate aspect ratio for selected model
    valid_ratios = MODEL_ASPECT_RATIOS[model]
    if aspect_ratio not in valid_ratios:
        print(f"Error: Aspect ratio '{aspect_ratio}' not supported for model '{model}'. Valid ratios: {', '.join(valid_ratios)}", file=sys.stderr)
        sys.exit(1)

    aspect_instruction = get_aspect_instruction(aspect_ratio)
    full_prompt = f"{aspect_instruction} {prompt}"

    # Build contents with optional reference images
    contents: list = []
    if references:
        for ref_path in references:
            if not os.path.exists(ref_path):
                print(f"Error: Reference image not found: {ref_path}", file=sys.stderr)
                sys.exit(1)
            contents.append(Image.open(ref_path))
        if len(references) == 1:
            full_prompt = f"{full_prompt} Use the provided image as a reference for style, composition, or content."
        else:
            full_prompt = f"{full_prompt} Use the provided {len(references)} images as references for style, composition, or content."
    contents.append(full_prompt)

    model_id = MODEL_IDS[model]

    # Pro and Nano Banana 2 models support image_config for resolution and aspect ratio
    if model in ("pro", "2"):
        valid_sizes = ["512", "1K", "2K", "4K"] if model == "2" else ["1K", "2K", "4K"]
        if size not in valid_sizes:
            print(f"Error: Size '{size}' not supported for model '{model}'. Valid sizes: {', '.join(valid_sizes)}", file=sys.stderr)
            sys.exit(1)
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=size,
            ),
        )
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config,
        )
    else:
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
        )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Extract image from response
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"Image saved to: {output_path}")
            return

    print("Error: No image data in response", file=sys.stderr)
    sys.exit(1)


def process_batch(jsonl_path: str) -> None:  # noqa: C901
    """Submit image generation jobs to the Gemini Batch API, poll until done, save results."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # --- 1. Read jobs ---
    jobs = []
    with open(jsonl_path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                job = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON on line {i}: {e}", file=sys.stderr)
                sys.exit(1)
            if "prompt" not in job or "output" not in job:
                print(f"Error: Line {i} missing required 'prompt' or 'output' field", file=sys.stderr)
                sys.exit(1)
            jobs.append(job)

    if not jobs:
        print("No jobs found in JSONL file.")
        return

    total = len(jobs)
    print(f"Preparing {total} image(s) for Gemini Batch API...", flush=True)

    client = genai.Client(api_key=api_key)

    # --- 2. Build Gemini batch JSONL ---
    # Each line: {"key": "<index>", "request": {GenerateContentRequest}}
    batch_lines = []
    for i, job in enumerate(jobs):
        model = job.get("model", "2")
        aspect_ratio = resolve_aspect(job.get("aspect", "square"))
        size = job.get("size", "1K")
        references = job.get("references")

        aspect_instruction = get_aspect_instruction(aspect_ratio)
        full_prompt = f"{aspect_instruction} {job['prompt']}"

        parts = []
        if references:
            for ref_path in references:
                if not os.path.exists(ref_path):
                    print(f"Error: Reference image not found: {ref_path}", file=sys.stderr)
                    sys.exit(1)
                with open(ref_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                parts.append({"inline_data": {"mime_type": "image/png", "data": img_b64}})
            suffix = "Use the provided image as a reference for style, composition, or content." \
                if len(references) == 1 else \
                f"Use the provided {len(references)} images as references for style, composition, or content."
            full_prompt += f" {suffix}"
        parts.append({"text": full_prompt})

        generation_config: dict = {"response_modalities": ["TEXT", "IMAGE"]}
        if model in ("pro", "2"):
            generation_config["image_config"] = {"aspect_ratio": aspect_ratio, "image_size": size}

        batch_lines.append(json.dumps({
            "key": str(i),
            "request": {
                "contents": [{"parts": parts}],
                "generation_config": generation_config,
            },
        }))

    # --- 3. Upload the batch JSONL via File API ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
        tmp.write("\n".join(batch_lines))
        tmp_path = tmp.name

    try:
        print("Uploading batch request file...", flush=True)
        uploaded_file = client.files.upload(
            file=tmp_path,
            config=types.UploadFileConfig(display_name="batch-images", mime_type="application/jsonl"),
        )

        # --- 4. Create batch job ---
        model_key = jobs[0].get("model", "2")
        model_id = MODEL_IDS[model_key]
        print(f"Creating batch job (model: {model_id})...", flush=True)
        batch_job = client.batches.create(
            model=model_id,
            src=uploaded_file.name,
            config={"display_name": "generate-images"},
        )
        print(f"Batch job created: {batch_job.name}", flush=True)

        # --- 5. Poll until terminal state ---
        terminal = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
        while batch_job.state.name not in terminal:
            print(f"  Status: {batch_job.state.name} — polling in 30s...", flush=True)
            time.sleep(30)
            batch_job = client.batches.get(name=batch_job.name)

        if batch_job.state.name != "JOB_STATE_SUCCEEDED":
            print(f"Error: Batch job ended with state {batch_job.state.name}", file=sys.stderr)
            sys.exit(1)

        print("Batch job succeeded. Downloading results...", flush=True)

        # --- 6. Download and save results ---
        content = client.files.download(file=batch_job.dest.file_name).decode("utf-8")
        errors = []
        saved = 0

        for line in content.splitlines():
            if not line.strip():
                continue
            result = json.loads(line)
            key = result.get("key")
            if key is None:
                continue
            job = jobs[int(key)]
            output_path = job["output"]

            if "error" in result:
                errors.append((output_path, result["error"]))
                print(f"  Error for {output_path}: {result['error']}", file=sys.stderr)
                continue

            for candidate in result.get("response", {}).get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline:
                        img_bytes = base64.b64decode(inline["data"])
                        output_dir = os.path.dirname(output_path)
                        if output_dir:
                            os.makedirs(output_dir, exist_ok=True)
                        with open(output_path, "wb") as out:
                            out.write(img_bytes)
                        saved += 1
                        print(f"[{saved}/{total}] Saved: {output_path}")
                        break

        if errors:
            print(f"\n{len(errors)} image(s) failed:", file=sys.stderr)
            for path, err in errors:
                print(f"  {path}: {err}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\nAll {total} image(s) saved successfully.")

    finally:
        os.unlink(tmp_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana (Gemini Flash, Pro, or 2)"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--prompt",
        help="Description of the image to generate (single-image mode)",
    )
    mode.add_argument(
        "--batch-input",
        metavar="JSONL_FILE",
        help="Path to a JSONL file for batch mode (one job per line)",
    )

    parser.add_argument(
        "--output",
        help="Output file path (PNG format) — required in single-image mode",
    )
    parser.add_argument(
        "--aspect",
        choices=list(ASPECT_ALIASES.keys()) + ALL_ASPECT_RATIOS,
        default="square",
        help="Aspect ratio: named shortcut (square, landscape, portrait) or direct ratio (e.g. 4:3, 21:9). Default: square",
    )
    parser.add_argument(
        "--reference",
        action="append",
        dest="references",
        help="Path to a reference image (can be specified multiple times for multiple references)",
    )
    parser.add_argument(
        "--model",
        choices=["flash", "pro", "2"],
        default="2",
        help="Model: flash (Nano Banana, fast, 1024px), pro (Nano Banana Pro, up to 4K), 2 (Nano Banana 2, fast + up to 4K) (default: 2)",
    )
    parser.add_argument(
        "--size",
        choices=["512", "1K", "2K", "4K"],
        default="1K",
        help="Image resolution for pro/2 models: 512 (2 only), 1K (default), 2K, 4K. Ignored for flash.",
    )
    args = parser.parse_args()

    if args.batch_input:
        if not os.path.exists(args.batch_input):
            print(f"Error: JSONL file not found: {args.batch_input}", file=sys.stderr)
            sys.exit(1)
        process_batch(args.batch_input)
    else:
        if not args.output:
            parser.error("--output is required in single-image mode")
        generate_image(args.prompt, args.output, args.aspect, args.references, args.model, args.size)


if __name__ == "__main__":
    main()
