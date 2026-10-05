---
title: Foodscaping Planner
emoji: 🖼️
colorFrom: yellow
colorTo: red
sdk: streamlit
app_file: app.py
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


# foodscaping_planner

Agente de **foodscaping**: recebe a foto de um exterior e devolve um
projecto de paisagismo comestível (visual + lista de plantas).

- ≥80% plantas comestíveis
- ≥80% perenes; anuais só em canteiros delimitados
- jardim desenhado (camadas, repetição, bordaduras, caminhos, guildas)
- hardscape e perspetiva da foto conservados

## Arranque

```bash
cd foodscaping_planner
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py