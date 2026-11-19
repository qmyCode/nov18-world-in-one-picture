"""Entrypoint for the news-image-20261118 entry.

Renders entry.png (1024x1024) — 'The World on Wednesday', a one-image
front page summing up the news of Wednesday 18 November 2026 — into the
same directory as this file. Requires Pillow.
"""

import os

import draw


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    draw.render(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
