from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .image_prompt import build_image_prompt, build_negative_prompt
from .system_prompt import SYSTEM_PROMPT
from .vision import SiteAnalysis

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "plants.json"

LAYER_ORDER = ["canopy", "shrub", "herbaceous", "herb", "climber", "groundcover", "annual_bed"]

ZONE_BY_LAYER = {
    "canopy": "fundo / ponto focal (1–3 árvores no máximo)",
    "shrub": "sebes laterais e guildas sob as árvores",
    "herbaceous": "canteiros permanentes de volume (alcachofra, espargo)",
    "herb": "bordadura junto a caminhos e à casa",
    "climber": "pérgola, muro ou vedação existente",
    "groundcover": "substituição de relvado e juntas de pavimento",
    "annual_bed": "canteiros geométricos delimitados, perto de água/cozinha",
}


class FoodscapingPlanner:
    def __init__(self, catalog_path: Path | None = None) -> None:
        path = catalog_path or DATA_PATH
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.meta = raw["meta"]
        self.plants = raw["plants"]

    def filter_plants(
        self,
        climate: str,
        sun: str,
        has_irrigation: bool,
        space_type: str,
        avoid_acid_lovers: bool = False,
    ) -> list[dict[str, Any]]:
        sun_map = {
            "dia todo": "full",
            "manhã": "full_or_part",
            "tarde": "full",
            "sombra parcial": "part",
        }
        sun_key = sun_map.get(sun, "full")
        terrace = space_type in {"terraço", "varanda", "pátio pequeno"}

        selected: list[dict[str, Any]] = []
        for plant in self.plants:
            if climate not in plant["climates"] and climate != "any":
                continue
            if avoid_acid_lovers and plant["id"] == "mirtilo":
                continue
            if plant["sun"] == "full" and sun_key == "part":
                continue
            if plant["water"] == "high" and not has_irrigation:
                continue
            if terrace and plant["layer"] == "canopy" and plant["id"] not in {
                "citrinos_anao",
                "macieira_ana",
                "romazeira",
            }:
                continue
            selected.append(plant)
        return selected

    def pick_palette(self, candidates: list[dict[str, Any]], space_type: str) -> list[dict[str, Any]]:
        """3–5 âncoras + camadas. Máximo ~12 espécies. 80% perene."""
        by_layer: dict[str, list[dict[str, Any]]] = {k: [] for k in LAYER_ORDER}
        for p in candidates:
            by_layer.setdefault(p["layer"], []).append(p)

        max_trees = 1 if space_type in {"terraço", "varanda", "pátio pequeno"} else 3
        picks: list[dict[str, Any]] = []

        def take(layer: str, n: int) -> None:
            for plant in by_layer.get(layer, [])[:n]:
                if plant not in picks:
                    picks.append(plant)

        take("canopy", max_trees)
        take("shrub", 2)
        take("herb", 3)
        take("herbaceous", 2)
        take("groundcover", 2)
        take("climber", 1)
        take("annual_bed", 3)

        perennials = [p for p in picks if p["life"] == "perennial"]
        annuals = [p for p in picks if p["life"] == "annual"]
        if len(picks) and len(annuals) / len(picks) > 0.2:
            annuals = annuals[: max(1, int(len(perennials) * 0.25))]
            picks = perennials + annuals
        return picks[:12]

    def guilds(self, palette: list[dict[str, Any]]) -> list[str]:
        tree = next((p["common_pt"] for p in palette if p["layer"] == "canopy"), None)
        shrub = next((p["common_pt"] for p in palette if p["layer"] == "shrub"), None)
        cover = next((p["common_pt"] for p in palette if p["layer"] == "groundcover"), None)
        herb = next((p["common_pt"] for p in palette if p["layer"] == "herb"), None)
        if not all([tree, shrub, cover, herb]):
            return ["Repetir bordadura aromática + cobertura de solo em todas as zonas abertas."]
        return [
            f"Guilda principal: {tree} + {shrub} + {cover} + {herb}.",
            "Repetir esta guilda 2–3 vezes em vez de espalhar espécies únicas.",
        ]

    def zones(self, palette: list[dict[str, Any]]) -> dict[str, list[str]]:
        zones: dict[str, list[str]] = {}
        for plant in palette:
            zone = ZONE_BY_LAYER.get(plant["layer"], "outras zonas")
            zones.setdefault(zone, []).append(
                f"{plant['common_pt']} ({plant['scientific']}) — {plant['life']}"
            )
        return zones

    def maintenance(self, has_irrigation: bool) -> dict[str, list[str]]:
        year1 = [
            "Jan–Fev: plantar árvores/arbustos de raiz nua se o clima permitir; mulch 7–10 cm.",
            "Mar: instalar bordaduras (alecrim, tomilho) e cobertura de morango.",
            "Abr–Mai: sementeira/plantação dos canteiros anuais; tutores.",
            "Jun–Ago: rega profunda e pouco frequente nas perenes;"
            + (" irrigação regular nos anuais." if has_irrigation else " priorizar perenes de sequeiro se não houver irrigação."),
            "Set: colheita de bagas/figos/uvas conforme espécie; não cortar alcachofras até ao fim.",
            "Out–Nov: plantar alhos e couves nos canteiros anuais; podas ligeiras de formação.",
            "Dez: proteger citrinos se houver geada; rever mulch.",
        ]
        later = [
            "Perenes pedem cada vez menos: poda de inverno, mulch, colheita.",
            "Anuais: renovar só os canteiros delimitados (máx. ~20% da área plantada).",
            "Morangueiros: renovar plantas a cada 3 anos.",
            "Hortelã: nunca libertar da barreira.",
            "Manter caminhos livres — jardim desenhado, não selva.",
        ]
        return {"ano_1": year1, "anos_seguintes": later}

    def concept(self, climate: str, space_type: str, goal: str, anchors: list[str]) -> str:
        look = (
            "jardim bonito que também se come"
            if goal == "jardim bonito que também se come"
            else "jardim produtivo com leitura de paisagismo"
        )
        return (
            f"Transformar o {space_type} num {look}, clima {climate}. "
            f"Estrutura permanente com {', '.join(anchors[:5])}. "
            "O hardscape permanece; o relvado e os vazios passam a camadas comestíveis. "
            "Repetição de 3–5 âncoras, caminhos claros, bordadura aromática e "
            "canteiros anuais geométricos como minoria. "
            "Deve ler-se como jardim desenhado o ano inteiro, com evergreen no inverno."
        )

    def plan(
        self,
        analysis: SiteAnalysis,
        climate: str,
        sun: str,
        has_irrigation: bool,
        space_type: str,
        goal: str,
        maintenance_level: str,
        country: str,
        kids_or_pets: bool,
        assumed_climate: bool = False,
    ) -> dict[str, Any]:
        avoid_acid = country.lower() in {"portugal", "espanha", "spain", "pt", "es"}
        candidates = self.filter_plants(
            climate=climate,
            sun=sun,
            has_irrigation=has_irrigation,
            space_type=space_type,
            avoid_acid_lovers=avoid_acid,
        )
        palette = self.pick_palette(candidates, space_type)

        if maintenance_level == "baixa":
            palette = [p for p in palette if p["water"] != "high" and p["life"] == "perennial"] + [
                p for p in palette if p["life"] == "annual"
            ][:2]

        if kids_or_pets:
            palette = [p for p in palette if p["id"] != "ruibarbo"]

        edible = [p for p in palette if p["edible"]]
        perennials = [p for p in palette if p["life"] == "perennial"]
        anchors = [
            p["common_pt"]
            for p in palette
            if "repeat" in p["role"] or "anchor" in p["role"] or "border" in p["role"]
        ][:5]
        if len(anchors) < 3:
            anchors = [p["common_pt"] for p in perennials[:5]]

        context = {
            "climate": climate,
            "assumed_climate": assumed_climate,
            "sun": sun,
            "irrigation": has_irrigation,
            "space_type": space_type,
            "goal": goal,
            "maintenance_level": maintenance_level,
            "country": country,
            "kids_or_pets": kids_or_pets,
        }

        draft = {
            "project": "foodscaping_planner",
            "system": SYSTEM_PROMPT,
            "context": context,
            "analysis": analysis.as_dict(),
            "anchor_species": anchors,
            "plants": palette,
        }
        image_prompt = build_image_prompt(draft)

        n = max(len(palette), 1)
        return {
            **draft,
            "concept": self.concept(climate, space_type, goal, anchors),
            "guilds": self.guilds(palette),
            "zones": self.zones(palette),
            "maintenance": self.maintenance(has_irrigation),
            "ratios": {
                "edible": round(len(edible) / n, 2),
                "perennial": round(len(perennials) / n, 2),
                "annual": round(1 - len(perennials) / n, 2),
                "count": n,
            },
            "image_prompt": image_prompt,
            "negative_prompt": build_negative_prompt(),
            "landscape_rules": [
                "Conservar hardscape e perspetiva da foto.",
                "80% comestível, 80% perene, anuais só em canteiros delimitados.",
                "3–5 espécies-âncora repetidas.",
                "Bordadura comestível, caminhos acessíveis, guildas, evergreen + sazonal.",
                "Escala correcta: árvores anãs junto a casas pequenas.",
            ],
        }