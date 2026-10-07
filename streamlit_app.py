from __future__ import annotations

import json
from io import BytesIO

import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

from agent.planner import FoodscapingPlanner
from agent.vision import analyze_photo


def generate_zone_diagram(plan: dict) -> plt.Figure:
    """Generate a simple schematic of the planting layout."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(5, 9.5, "Esquema do jardim", ha="center", va="center", fontsize=16, weight="bold")

    # Base ground
    ax.add_patch(plt.Rectangle((0.5, 0.8), 9, 7.8, facecolor="#e8f5e9", edgecolor="none"))

    # Anchor trees (circles)
    anchor_species = plan.get("anchor_species", [])
    tree_positions = [(1.8, 6.8), (4.5, 7.2), (7.2, 6.8), (8.2, 4.8)]
    for i, (x, y) in enumerate(tree_positions[: len(anchor_species) or 3]):
        ax.add_patch(plt.Circle((x, y), 0.55, color="#8d6e63", alpha=0.85, ec="black", lw=0.5))
        ax.text(x, y, anchor_species[i] if i < len(anchor_species) else "Árvore", ha="center", va="center", fontsize=8)

    # Hedge / shrub strips (rectangles)
    ax.add_patch(plt.Rectangle((1.0, 3.4), 2.5, 1.0, facecolor="#66bb6a", edgecolor="black", lw=1))
    ax.add_patch(plt.Rectangle((5.8, 3.4), 2.8, 1.0, facecolor="#66bb6a", edgecolor="black", lw=1))
    ax.text(2.25, 3.9, "Framboeseira + Feijoa", ha="center", va="center", fontsize=8)
    ax.text(7.2, 3.9, "Framboeseira + Feijoa", ha="center", va="center", fontsize=8)

    # Border line of aromatic plants (small circles)
    border_x = [1.2, 2.3, 3.4, 4.5, 5.6, 6.7, 7.8, 8.8]
    for x in border_x:
        ax.add_patch(plt.Circle((x, 1.6), 0.18, color="#7cb342", ec="black", lw=0.5))
    ax.text(5.0, 1.2, "Bordadura: Alecrim / Tomilho", ha="center", va="center", fontsize=9)

    # Striped area = strawberry replacing lawn
    ax.add_patch(plt.Rectangle((1.0, 5.0), 7.2, 1.1, facecolor="#d9f2d9", edgecolor="black", lw=1))
    for xx in range(1, 8):
        for yy in [5.05, 5.45, 5.85, 6.05]:
            ax.plot([xx, xx + 0.4], [yy, yy + 0.3], color="#7ecb73", lw=3)
    ax.text(4.6, 5.55, "Morangueiro substitui relvado", ha="center", va="center", fontsize=8)

    # Annual bed in red / geometric patch
    ax.add_patch(plt.Rectangle((3.1, 7.2), 3.4, 1.1, facecolor="#f4cccc", edgecolor="black", lw=1.2))
    ax.text(4.8, 7.7, "Piri-piri / canteiro anual 20%", ha="center", va="center", fontsize=8, color="#7a1f1f")

    # Legend
    ax.text(0.7, 0.4, "Legenda:", fontsize=10, weight="bold")
    ax.add_patch(plt.Circle((1.8, 0.4), 0.18, color="#8d6e63", alpha=0.85))
    ax.text(2.2, 0.4, "árvore âncora", fontsize=8)
    ax.add_patch(plt.Rectangle((4.2, 0.25), 0.6, 0.35, facecolor="#66bb6a", edgecolor="black"))
    ax.text(5.2, 0.4, "sebe", fontsize=8)
    ax.add_patch(plt.Rectangle((6.6, 0.25), 0.6, 0.35, facecolor="#d9f2d9", edgecolor="black"))
    ax.text(7.6, 0.4, "morangueiro", fontsize=8)
    ax.add_patch(plt.Rectangle((8.8, 0.25), 0.6, 0.35, facecolor="#f4cccc", edgecolor="black"))
    ax.text(9.8, 0.4, "anual", fontsize=8)

    return fig


st.set_page_config(page_title="foodscaping_planner", layout="wide")
st.title("foodscaping_planner")
st.caption(
    "Fotografia de um exterior → jardim desenhado, maioritariamente comestível e perene."
)

planner = FoodscapingPlanner()

with st.sidebar:
    st.header("Contexto do sítio")
    country = st.text_input("País / cidade", "Portugal")
    climate = st.selectbox(
        "Clima",
        ["mediterranean", "mild", "temperate", "atlantic"],
        index=0,
        help="Se não souberes, deixa mediterrânico (assunção declarada).",
    )
    assumed = st.checkbox("Clima é uma assunção", value=False)
    space_type = st.selectbox(
        "Tipo de espaço",
        ["jardim", "pátio", "pátio pequeno", "terraço", "varanda", "fachada"],
    )
    sun = st.selectbox("Sol", ["dia todo", "manhã", "tarde", "sombra parcial"])
    irrigation = st.toggle("Há irrigação", value=True)
    goal = st.radio(
        "Objectivo",
        ["jardim bonito que também se come", "produção de comida"],
    )
    maintenance_level = st.select_slider(
        "Manutenção", options=["baixa", "média", "alta"], value="média"
    )
    kids_or_pets = st.checkbox("Crianças ou animais")

photo = st.file_uploader(
    "Fotografia do exterior (perspetiva ao nível do olhar, de dia, nítida)",
    type=["jpg", "jpeg", "png", "webp"],
)

if photo:
    image = Image.open(photo).convert("RGB")
    st.subheader("Antes")
    st.image(image, use_container_width=True)

    analysis = analyze_photo(image, user_space=space_type)
    plan = planner.plan(
        analysis=analysis,
        climate=climate,
        sun=sun,
        has_irrigation=irrigation,
        space_type=space_type,
        goal=goal,
        maintenance_level=maintenance_level,
        country=country,
        kids_or_pets=kids_or_pets,
        assumed_climate=assumed or climate == "mediterranean",
    )

    st.divider()
    st.subheader("1. Análise do sítio")
    if plan["context"]["assumed_climate"]:
        st.warning(f"Clima assumido: **{plan['context']['climate']}**.")
    st.write(f"- Espaço: **{analysis.likely_space}** ({analysis.width}×{analysis.height}px)")
    for note in analysis.notes:
        st.write(f"- {note}")

    st.subheader("2. Conceito")
    st.write(plan["concept"])
    st.write("**Regras de paisagismo**")
    for rule in plan["landscape_rules"]:
        st.write(f"- {rule}")
    st.write("**Guildas**")
    for g in plan["guilds"]:
        st.write(f"- {g}")

    st.subheader("3. Rácios")
    r = plan["ratios"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Espécies", r["count"])
    c2.metric("Comestível", f"{int(r['edible']*100)}%")
    c3.metric("Perene", f"{int(r['perennial']*100)}%")
    c4.metric("Anual", f"{int(r['annual']*100)}%")
    st.write("**Âncoras:** " + ", ".join(plan["anchor_species"]))

    st.subheader("4. Lista de plantas")
    rows = [
        {
            "Comum": p["common_pt"],
            "Científico": p["scientific"],
            "Camada": p["layer"],
            "Ciclo": p["life"],
            "Sol": p["sun"],
            "Água": p["water"],
            "Função": ", ".join(p["role"]),
            "Notas": p["notes"],
        }
        for p in plan["plants"]
    ]
    st.dataframe(rows, use_container_width=True)

    st.subheader("5. Esquema por zonas")
    st.pyplot(generate_zone_diagram(plan))

    st.subheader("6. Manutenção")
    tab1, tab2 = st.tabs(["1.º ano", "Anos seguintes"])
    with tab1:
        for line in plan["maintenance"]["ano_1"]:
            st.write(f"- {line}")
    with tab2:
        for line in plan["maintenance"]["anos_seguintes"]:
            st.write(f"- {line}")

    payload = json.dumps(plan, ensure_ascii=False, indent=2)
    st.download_button(
        "Descarregar projecto JSON",
        data=payload.encode("utf-8"),
        file_name="foodscaping_plan.json",
        mime="application/json",
    )

    buf = BytesIO()
    image.save(buf, format="JPEG", quality=92)
    st.download_button(
        "Descarregar foto original",
        data=buf.getvalue(),
        file_name="site_before.jpg",
        mime="image/jpeg",
    )
else:
    st.markdown(
        """
        **Como usar**
        1. Carrega uma foto nítida, de dia, em perspetiva.
        2. Preenche clima, sol, irrigação e restrições na barra lateral.
        3. O agente devolve análise, conceito, paleta 80% perene/comestível,
           zonas e manutenção com esquema visual.
        """
    )
