from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');
        :root { --ink:#16323f; --teal:#0e7490; --coral:#f97316; --sand:#fffaf3; }
        .stApp { background:var(--sand); color:var(--ink); }
        [data-testid="stSidebar"] { background:#e9f5f5; }
        h1,h2,h3 { font-family:'Playfair Display',serif !important; color:var(--ink); }
        p, label, .stMarkdown { font-family:'DM Sans',sans-serif; }
        .hero { padding:2.5rem 1rem 2rem; background:linear-gradient(120deg,#dff4ef,#fff4e6); border-radius:24px; margin-bottom:1.5rem; }
        .hero h1 { font-size:clamp(2.4rem,5vw,4.7rem); line-height:1.05; margin:.4rem 0 1rem; }
        .hero h1 span { color:var(--coral); }
        .eyebrow { color:var(--teal); font-weight:700; letter-spacing:.12em; font-size:.75rem; }
        .destination-card { min-height:205px; padding:1.2rem; border:1px solid #d5e6e2; border-radius:18px; background:white; box-shadow:0 6px 24px #164e6310; }
        .destination-card h3 { margin:.1rem 0; }
        .tag { display:inline-block; background:#e0f2f1; color:#155e75; border-radius:999px; padding:.25rem .55rem; margin:.2rem .2rem 0 0; font-size:.75rem; }
        .cost { color:var(--teal); font-weight:700; }
        button[kind="primary"] { background:var(--coral) !important; border-color:var(--coral) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
