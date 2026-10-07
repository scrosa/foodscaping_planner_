from __future__ import annotations

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image


def _load_pipe():
    """Carrega o modelo localmente e usa GPU quando disponível."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = AutoPipelineForText2Image.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
    )
    pipe = pipe.to(device)

    if device == "cuda":
        pipe.enable_attention_slicing()

    return pipe


def generate_illustration(prompt: str, negative_prompt: str = "") -> Image.Image | None:
    """Gera uma ilustração de paisagismo a partir do prompt do plano."""
    try:
        pipe = _load_pipe()

        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=25,
            guidance_scale=7.5,
            width=1024,
            height=768,
        )

        return result.images[0]
    except Exception as exc:
        print(f"Erro ao gerar ilustração local: {exc}")
        return None
