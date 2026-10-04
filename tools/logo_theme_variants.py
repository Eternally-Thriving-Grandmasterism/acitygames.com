#!/usr/bin/env python3
# LOGO-3D-1 generator. Usage: python3 tools/logo_theme_variants.py site/images/logo-1024.png dark out.png
# Then save as lossless WebP (exact=True). Needs numpy, scipy, Pillow.
"""Recolour and re-shade the crest inside its original alpha mask.
The alpha channel is copied byte-for-byte, so the silhouette is pixel-identical."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def hex2rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float) / 255

def ramp(stops, v):
    v = np.clip(v, 0, 1)
    xs = np.array([s[0] for s in stops]); cs = np.array([hex2rgb(s[1]) for s in stops])
    return np.stack([np.interp(v, xs, cs[:, i]) for i in range(3)], -1)

THEMES = {
    # dark: brighter, glowing warm gold
    "dark": dict(
        body=[(0.0, '#b85a0e'), (0.30, '#e88a1c'), (0.52, '#f6b23a'), (0.74, '#ffd25e'), (0.90, '#ffe9a6'), (1.0, '#fff8e2')],
        rim=[(0.0, '#a8480c'), (0.35, '#e0701a'), (0.65, '#fd9a3c'), (0.88, '#ffc773'), (1.0, '#fff0cf')],
        gloss=[(0.0, '#ffd98a'), (0.6, '#fff1c8'), (1.0, '#fffdf4')],
        lift=0.06, spec=0.55),
    # light: richer, slightly deeper gold-orange, crisp
    "light": dict(
        body=[(0.0, '#a8480c'), (0.28, '#d9781a'), (0.55, '#f2a93a'), (0.80, '#ffd36e'), (1.0, '#fff3d1')],
        rim=[(0.0, '#8f3f0c'), (0.35, '#c4560e'), (0.65, '#ec7a22'), (0.88, '#ffad5a'), (1.0, '#ffe2b8')],
        gloss=[(0.0, '#ffd27a'), (0.6, '#ffeec2'), (1.0, '#fffbf0')],
        lift=0.0, spec=0.5),
}

def render(src, theme):
    im = np.array(Image.open(src).convert('RGBA')).astype(float)
    H, W = im.shape[:2]; s = W / 1024.0
    a = im[..., 3]; g = im[..., 1]
    solid = a > 127
    # region weights from the green channel (rim ~136, body ~181, gloss ~210)
    w_rim = np.clip((181 - g) / 45, 0, 1)
    w_gloss = np.clip((g - 181) / 29, 0, 1)
    w_body = 1 - w_rim - w_gloss
    inner = solid & (g > 158)              # body + gloss panels (inside the rim)
    # heights: rim as a rounded tube, panels as a soft pillow set slightly below the rim
    d_in = ndi.distance_transform_edt(inner)
    # heights from blurred masks: no medial-axis creases, smooth rounded bevels
    rim_h = ndi.gaussian_filter(solid.astype(float), 5.0 * s)
    panel_h = 0.6 * ndi.gaussian_filter(inner.astype(float), 12.0 * s) + 0.9 * ndi.gaussian_filter(inner.astype(float), 38.0 * s)
    Hm = 1.0 * rim_h + 1.5 * panel_h - 0.45 * ndi.gaussian_filter(inner.astype(float), 1.2 * s)
    Hm = ndi.gaussian_filter(Hm, 1.2 * s)
    gy, gx = np.gradient(Hm * 9.0 * s)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array([-0.45, -0.65, 0.62]); L /= np.linalg.norm(L)
    V = np.array([0, 0, 1.0]); Hv = (L + V); Hv /= np.linalg.norm(Hv)
    diff = np.clip(n @ L, 0, 1)
    spec = np.clip(n @ Hv, 0, 1) ** 40
    # environment band for a polished-metal read (sky above, warm floor below)
    env = 0.5 + 0.5 * (-n[..., 1])
    yy = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    xx = np.linspace(0, 1, W)[None, :] * np.ones((H, 1))
    diag = 0.55 * xx + 0.75 * yy
    sheen = np.exp(-((diag - 0.42) / 0.11) ** 2)   # soft polished band, upper left
    v = 0.08 + 0.50 * diff + 0.20 * env + 0.16 * (1 - diag / 1.3) + 0.10 * sheen
    T = THEMES[theme]
    v = v + T['lift']
    col = (w_body[..., None] * ramp(T['body'], v)
           + w_rim[..., None] * ramp(T['rim'], v * 0.95)
           + w_gloss[..., None] * ramp(T['gloss'], v))
    col = col + T['spec'] * spec[..., None] * np.array([1.0, 0.97, 0.88])
    # soft inner shading along the panel edge where it meets the rim
    occl = np.exp(-d_in / (4.5 * s)) * inner
    col = col * (1 - 0.18 * occl[..., None])
    out = np.zeros_like(im)
    out[..., :3] = np.clip(col, 0, 1) * 255
    out[..., 3] = a
    out = np.round(out).astype(np.uint8)
    out[..., 3] = im[..., 3].astype(np.uint8)  # exact original alpha
    return out

if __name__ == '__main__':
    src, theme, dst = sys.argv[1:4]
    Image.fromarray(render(src, theme), 'RGBA').save(dst, optimize=True)
