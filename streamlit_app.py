from __future__ import annotations

import json
from io import BytesIO

import streamlit as st
from PIL import Image

from agent.planner import FoodscapingPlanner
from agent.vision import analyze_photo

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
    col_a, col_b = st.columns(2)
    with col_a:
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

    with col_b:
        st.subheader("Depois (ilustração)")
        with st.spinner("Gerando ilustração de paisagismo..."):
            from agent.image_generator import generate_illustration
            illustration = generate_illustration(
                prompt=plan["image_prompt"],
                negative_prompt=plan["negative_prompt"]
            )
        
        if illustration:
            st.image(illustration, use_container_width=True)
            buf = BytesIO()
            illustration.save(buf, format="PNG")
            st.download_button(
                "Descarregar ilustração",
                data=buf.getvalue(),
                file_name="foodscaping_illustration.png",
                mime="image/png",
            )
        else:
            st.warning("Não foi possível gerar a ilustração. Verifique a conexão ou tente mais tarde.")

    st.divider()
    st.subheader("1. Análise do sítio")
    if plan["context"]["assumed_climate"]:
        st.warning(f"Clima assumido: **{plan['context']['climate']}**.")
    st.write(
        f"- Espaço: **{analysis.likely_space}** ({analysis.width}×{analysis.height}px)"
    )
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
    for zone, plants in plan["zones"].items():
        st.markdown(f"**{zone}**")
        for line in plants:
            st.write(f"- {line}")

    st.subheader("6. Manutenção")
    t1, t2 = st.tabs(["1.º ano", "Anos seguintes"])
    with t1:
        for line in plan["maintenance"]["ano_1"]:
            st.write(f"- {line}")
    with t2:
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
           zonas, manutenção e uma ilustração gerada.
        """
    )
