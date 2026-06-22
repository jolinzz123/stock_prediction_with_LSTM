import streamlit as st

from ..tokens import get_tokens, get_is_dark
from ._base import css_base
from ._nav import css_nav
from ._metrics import css_metrics
from ._inputs import css_inputs
from ._buttons import css_buttons
from ._dataframe import css_dataframe
from ._forecast import css_forecast
from ._news import css_news
from ._widgets import css_widgets


def inject_global_css() -> None:
    T = get_tokens()
    is_dark = get_is_dark()

    parts = [
        "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');",
        css_base(T),
        css_nav(T),
        css_metrics(T),
        css_inputs(T),
        css_buttons(T),
        css_dataframe(T),
        css_forecast(T, is_dark),
        css_news(T),
        css_widgets(T, is_dark),
    ]

    st.markdown(
        f"<style>\n{''.join(parts)}\n</style>",
        unsafe_allow_html=True,
    )
