from dataclasses import dataclass

@dataclass(frozen=True)
class Slot:
    key: str
    label: str
    kind: str = "upgrade"
    currency: str = "scrap"
    costs: tuple = ()
    requires: str | None = None   # key of a weapon that must be unlocked first

HARRY_SLOTS = (
    Slot("MULTISHOT", "CANNON", currency="salvage", costs=(5, 10, 16, 24)),
    Slot("LASER", "LASER", currency="salvage", costs=(7, 10, 16, 24, 36)),
    Slot("SHOCKWAVE", "SHOCKWAVE", currency="salvage", costs=(6, 10, 16, 24, 36)),
    Slot("maintenance", "MAINT", kind="mode", currency="salvage"),
)

BARRY_SLOTS = (
    Slot("speed", "SPEED", costs=(5, 8, 13, 20)),
    Slot("max_hull", "HULL", costs=(8, 14, 22)),
    Slot("ability", "ABILITY", costs=(8, 14, 22)),
    Slot("repair", "REPAIR", kind="mode"),
)
