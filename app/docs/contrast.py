"""
WCAG 2.1 contrast checker for the Proofolio palette.

    python3 docs/contrast.py

Add a row to PAIRS whenever you add a colour. Body text needs 4.5:1,
large text (24px, or 18.66px bold) needs 3:1, borders and icons need 3:1.
"""


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    r, g, b = linear
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


PAIRS = [
    # label,                              foreground, background, minimum
    ("light  --ink on --surface",         "#0b1a2e", "#ffffff", 4.5),
    ("light  --ink-2 on --surface",       "#44566e", "#ffffff", 4.5),
    ("light  --ink-3 on --surface",       "#566780", "#ffffff", 4.5),
    ("light  --ink-3 on --surface-2",     "#566780", "#f7faff", 4.5),
    ("light  --ink-3 on --ground",        "#566780", "#f3f7fd", 4.5),
    ("light  --brand on --surface",       "#0b63d6", "#ffffff", 4.5),
    ("light  --brand on --ground",        "#0b63d6", "#f3f7fd", 4.5),
    ("light  Met chip",                   "#0b63d6", "#e2edfe", 4.5),
    ("light  Partly chip",                "#8f6708", "#fbf1d8", 4.5),
    ("light  Not met chip",               "#a1293c", "#fae7ea", 4.5),
    ("light  info note",                  "#1f5e8c", "#e5eff6", 4.5),
    ("light  primary button",             "#ffffff", "#0b63d6", 4.5),
    ("light  Partly selected",            "#ffffff", "#8f6708", 4.5),
    ("light  Not met selected",           "#ffffff", "#a1293c", 4.5),
    ("dark   --ink on --surface",         "#e9f1fb", "#0e1620", 4.5),
    ("dark   --ink-2 on --surface",       "#a7b6c9", "#0e1620", 4.5),
    ("dark   --ink-3 on --surface",       "#8d9db2", "#0e1620", 4.5),
    ("dark   --ink-3 on --ground",        "#8d9db2", "#070b12", 4.5),
    ("dark   Met chip",                   "#6aaaf5", "#11233a", 4.5),
    ("dark   Partly chip",                "#efc463", "#2b2311", 4.5),
    ("dark   Not met chip",               "#f07a86", "#2e161b", 4.5),
    ("dark   info note",                  "#7fb6e0", "#14212b", 4.5),
    ("dark   primary button",             "#04131f", "#6aaaf5", 4.5),
]

if __name__ == "__main__":
    failures = 0
    for label, fg, bg, minimum in PAIRS:
        r = ratio(fg, bg)
        ok = r >= minimum
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {r:5.2f}:1  (needs {minimum})  {label}")
    print()
    print("All pairs pass." if not failures else f"{failures} pair(s) below the minimum.")
