


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
    if slot.key == "max_hull":
        player.hull += 1
    return True