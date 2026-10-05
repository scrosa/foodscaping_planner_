"""Leitura da fotografia. Sem API, usa heurística + notas do utilizador."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from PIL import Image


@dataclass
class SiteAnalysis:
    width: int
    height: int
    aspect: str
    likely_space: str
    notes: list[str] = field(default_factory=list)
    vision_description: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "aspect": self.aspect,
            "likely_space": self.likely_space,
            "notes": self.notes,
            "vision_description": self.vision_description,
        }


def classify_space(image: Image.Image, user_space: str | None = None) -> str:
    if user_space:
        return user_space
    w, h = image.size
    ratio = w / max(h, 1)
    if ratio > 1.6:
        return "fachada / vista ampla de jardim"
    if ratio < 0.85:
        return "pátio estreito / recanto / recorte vertical"
    return "jardim / pátio em perspetiva"


def analyze_photo(
    image: Image.Image,
    user_space: str | None = None,
    vision_description: str | None = None,
) -> SiteAnalysis:
    w, h = image.size
    space = classify_space(image, user_space)
    notes = [
        "Conservar casa, muros, pavimentos, portas e janelas.",
        "Manter perspetiva e ângulo de câmara da foto original.",
        "Não tapar entradas nem vãos de janela.",
        "Substituir relvado genérico e vazios por plantação comestível desenhada.",
    ]
    if w < 800 or h < 800:
        notes.append("Foto relativamente pequena: pedir versão mais nítida se a imagem final sair mole.")
    return SiteAnalysis(
        width=w,
        height=h,
        aspect=f"{w}:{h}",
        likely_space=space,
        notes=notes,
        vision_description=vision_description,
    )