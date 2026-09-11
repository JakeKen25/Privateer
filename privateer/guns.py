"""Naval gun quality is independent of research-area unlocks."""
GUN_CALIBERS = tuple(range(2, 21))
GUN_QUALITIES = (-3, -2, -1, 0, 1, 2, 9)


def gun_quality(fields, caliber):
    raw = fields.get(f'Guns{caliber}')
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    return value if value in GUN_QUALITIES else None
