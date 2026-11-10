from enum import Enum, auto





class SlotState(Enum):
    PURCHASEABLE = auto()
    UNAFFORDABLE = auto()
    MAXED = auto()
    MODE = auto()

LIGHT_COLORS = {
    SlotState.PURCHASEABLE: (133, 250, 250),
    SlotState.UNAFFORDABLE: (79, 49, 105),
    SlotState.MAXED: (232, 255, 191),
    SlotState.MODE: (79, 49, 105)
}
    
def slot_state(player, slot):
    if slot.kind == "mode":
        return SlotState.MODE
    level = player.levels[slot.key]
    if level >= len(slot.costs):
        return SlotState.MAXED
    if getattr(player, slot.currency) >= slot.costs[level]:
        return SlotState.PURCHASEABLE
    return SlotState.UNAFFORDABLE

def buy(player, slot):
    if slot_state(player, slot) is not SlotState.PURCHASEABLE:
        return False
    level = player.levels[slot.key]
    if level >= len(slot.costs):
        return False
    cost = slot.costs[level]
    wallet = getattr(player, slot.currency)
    if wallet < cost:
        return False
    setattr(player, slot.currency, wallet - cost) # pay and update wallet
    player.levels[slot.key] += 1                  # level up
    return True

def affordable_slots(player, slots):
    order = []
    
    for s in slots:
        if slot_state(player, s) is SlotState.PURCHASEABLE:
            order.append(s)
        
        sorted_order = sorted(order, key = lambda s: s.costs[player.levels[s.key]])
    return sorted_order

def auto_buy(player, slots):
    options = affordable_slots(player, slots)
    if not options:
        return None
    slot = options[0]
    buy(player, slot)
    if slot.key == "max_hull":
        player.hull += 1
    return slot