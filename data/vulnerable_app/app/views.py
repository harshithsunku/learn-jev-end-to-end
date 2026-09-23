"""HTML views."""
import html


def render_greeting(name):
    return f"<h1>Hello {name}!</h1>"


def render_greeting_safe(name):
    return f"<h1>Hello {html.escape(name)}!</h1>"


def health():
    return {"status": "ok"}
