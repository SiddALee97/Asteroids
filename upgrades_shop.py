


def buy(player, slot):
    if slot.kind == "mode":
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
        if s.kind == "mode":
            continue
        if player.levels[s.key] >= len(s.costs):
            continue
        if getattr(player, s.currency) >= s.costs[player.levels[s.key]]:
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