"""Gera um SVG com estilo de projeto de paisagismo a partir do plano."""

from __future__ import annotations

import random
from typing import Any


def generate_landscape_svg(plan: dict[str, Any], width: int = 1024, height: int = 768) -> str:
    """
    Gera um SVG estilo projeto de paisagismo com:
    - Zones de plantação
    - Símbolos simplificados das plantas
    - Legenda e anotações
    """
    plants = plan.get("plants", [])
    zones_dict = plan.get("zones", {})
    anchor_species = plan.get("anchor_species", [])
    space_type = plan.get("context", {}).get("space_type", "jardim")

    # Organizar plantas por camada para visualização
    by_layer = {}
    for p in plants:
        layer = p.get("layer", "other")
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(p)

    # Cores por camada
    layer_colors = {
        "canopy": "#2d5016",       # verde escuro
        "shrub": "#4a7c1d",        # verde médio
        "herb": "#8bc34a",         # verde claro
        "herbaceous": "#a4d65e",   # verde muito claro
        "groundcover": "#b8d968",  # amarelo-verde
        "climber": "#5b8c5a",      # verde azulado
        "annual_bed": "#ff9800",   # laranja
    }

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs>',
        '<style>',
        'text { font-family: "Arial", sans-serif; }',
        '.title { font-size: 28px; font-weight: bold; fill: #2d5016; }',
        '.zone-label { font-size: 14px; font-weight: bold; fill: #2d5016; }',
        '.plant-label { font-size: 11px; fill: #333; }',
        '.legend-label { font-size: 12px; fill: #333; }',
        '</style>',
        '</defs>',
        # Fundo
        '<rect width="{}" height="{}" fill="#f5f5f0"/>'.format(width, height),
        # Título
        '<text class="title" x="20" y="40">Projeto Foodscaping</text>',
    ]

    # Fundo com zonas (áreas de cores diferentes)
    margin = 60
    plot_width = width - 2 * margin
    plot_height = height - 100

    # Desenhar zonas por camada
    zone_height = plot_height / len(by_layer) if by_layer else plot_height
    y_offset = 60

    for idx, (layer, layer_plants) in enumerate(sorted(by_layer.items())):
        color = layer_colors.get(layer, "#cccccc")
        y = y_offset + idx * zone_height

        # Retângulo para a zona
        svg_parts.append(
            f'<rect x="{margin}" y="{y}" width="{plot_width}" height="{zone_height}" '
            f'fill="{color}" opacity="0.15" stroke="{color}" stroke-width="2"/>'
        )

        # Label da zona
        zone_name = {
            "canopy": "Árvores",
            "shrub": "Arbustos",
            "herbaceous": "Permanentes",
            "herb": "Bordadura",
            "climber": "Trepadeiras",
            "groundcover": "Cobertura",
            "annual_bed": "Anuais",
        }.get(layer, layer.replace("_", " ").title())

        svg_parts.append(
            f'<text class="zone-label" x="{margin + 10}" y="{y + 25}">{zone_name}</text>'
        )

        # Símbolos das plantas nesta zona
        x_offset = margin + 30
        for pidx, plant in enumerate(layer_plants):
            x = x_offset + (pidx % 5) * (plot_width // 5)
            py = y + 40 + (pidx // 5) * 30

            # Cor da planta (um pouco mais saturada que a zona)
            plant_color = color.replace("cc", "aa")

            # Círculo para a planta (simplificado)
            svg_parts.append(
                f'<circle cx="{x}" cy="{py}" r="12" fill="{plant_color}" '
                f'stroke="{color}" stroke-width="1.5" opacity="0.8"/>'
            )

            # Iniciais do nome
            initials = "".join([w[0].upper() for w in plant["common_pt"].split()[:2]])
            svg_parts.append(
                f'<text class="plant-label" x="{x}" y="{py + 4}" '
                f'text-anchor="middle" font-weight="bold">{initials}</text>'
            )

    # Legenda no rodapé
    legend_y = height - 35
    svg_parts.append(f'<text class="zone-label" x="{margin}" y="{legend_y}">Legenda:</text>')

    legend_x = margin + 100
    for layer, color in list(layer_colors.items())[:4]:
        svg_parts.append(
            f'<rect x="{legend_x}" y="{legend_y - 15}" width="15" height="15" '
            f'fill="{color}" opacity="0.5"/>'
        )
        layer_name = {
            "canopy": "Árvores",
            "shrub": "Arbustos",
            "herb": "Bordadura",
            "groundcover": "Cobertura",
        }.get(layer, layer.replace("_", " "))
        svg_parts.append(
            f'<text class="legend-label" x="{legend_x + 20}" y="{legend_y}">{layer_name}</text>'
        )
        legend_x += 150

    # Rodapé com info
    svg_parts.append(
        f'<text class="legend-label" x="{width - margin - 200}" y="{legend_y}" '
        f'text-anchor="end">{len(plants)} espécies • {space_type}</text>'
    )

    svg_parts.append("</svg>")

    return "\n".join(svg_parts)
