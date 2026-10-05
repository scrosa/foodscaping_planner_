"""Prompt de transformação visual (img2img / inpainting)."""

from __future__ import annotations


def build_image_prompt(plan: dict) -> str:
    climate = plan["context"]["climate"]
    space = plan["analysis"]["likely_space"]
    anchors = ", ".join(plan["anchor_species"])
    perennial = ", ".join(p["common_pt"] for p in plan["plants"] if p["life"] == "perennial")
    annuals = ", ".join(p["common_pt"] for p in plan["plants"] if p["life"] == "annual") or "none"

    return f"""
Photorealistic landscape architecture renovation of the SAME outdoor scene.
Keep the original camera angle, perspective, building, walls, windows, doors,
paving, sky and hardscape EXACTLY. Do not invent a different house.

Space type: {space}. Climate: {climate}.
Style: designed edible garden / foodscaping, not a messy allotment.
Layered planting, clear gravel or stone paths, repetition, edible borders,
focal points, guilds around fruit trees. Real plants, real soil, real light.

Anchor plants repeated: {anchors}.
Perennial edible structure: {perennial}.
Annuals ONLY inside clearly edged geometric beds: {annuals}.

Include: rosemary and thyme borders, strawberry groundcover replacing lawn
patches, 1-3 fruit trees of correct scale, berry shrubs as hedges, a vine
on existing pergola or wall IF support exists. Keep access to doors clear.
Evergreen winter structure plus seasonal fruit. No tropical jungle, no CGI
gloss, no extra buildings, no text, no watermark.
""".strip()


def build_negative_prompt() -> str:
    return (
        "different house, changed windows, blocked door, overgrown jungle, "
        "messy vegetable patch, plastic look, extra buildings, people, text, "
        "watermark, deformed plants, tropical rainforest, fake CGI garden"
    )