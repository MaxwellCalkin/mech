"""Utility helpers for gameplay logic."""

from typing import Any

try:
    import pygame
except Exception:  # pragma: no cover - pygame may not be installed
    pygame = None


def rects_collide(rect_a: Any, rect_b: Any) -> bool:
    """Return ``True`` if the two rectangles overlap."""
    if pygame is None or not hasattr(rect_a, "colliderect"):
        ax, ay, aw, ah = rect_a
        bx, by, bw, bh = rect_b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
    return rect_a.colliderect(rect_b)
