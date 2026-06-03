DOMAIN_COLORS: dict[str, str] = {
    "Social-Emotional":     "#FFCCE1",
    "Language":             "#CCE5FF",
    "Mathematics":          "#CCFFCC",
    "Science":              "#FFFFCC",
    "Physical":             "#FFCC99",
    "Arts":                 "#E0CCFF",
    "Approaches to Learning": "#D4EDE1",
}

DOMAIN_BORDER: dict[str, str] = {
    "Social-Emotional":     "#E8709A",
    "Language":             "#5A9FD4",
    "Mathematics":          "#5AAD5A",
    "Science":              "#C8B830",
    "Physical":             "#D4842A",
    "Arts":                 "#8A5CD4",
    "Approaches to Learning": "#3A9A6A",
}


def bg_for_domain(domain: str) -> str:
    return DOMAIN_COLORS.get(domain, "#EEEEEE")


def border_for_domain(domain: str) -> str:
    return DOMAIN_BORDER.get(domain, "#999999")
