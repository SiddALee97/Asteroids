from sequence import Beat

BASICS = {
    "first_scrap": [
        Beat("barry", "BARRY: Scrap ore.I believe we could use those materials to upgrade the ship.", open_panel = True, key = "first_scrap"),
        Beat("harry", "HARRY: I think you can use the panel to spend the scrap on upgrades.", open_panel = True, key = "first_scrap")        
    ],
    "first_hit": [
        Beat("harry", "HARRY: Barry, watch where you are flying man.", key = "first_hit"),
        Beat("barry", "BARRY: This ship is not as responsive as you would think.", key = "first_hit")
    ],
}


def trigger(sequence, key, player):
    if key not in BASICS or sequence.active:
        print("trigger", key, key in BASICS, sequence.active, player.invulnerability_timer)
        return False
    if player.invulnerability_timer > 0:    # so we dont trigger a beats mid hit
        print("trigger", key, key in BASICS, sequence.active, player.invulnerability_timer)
        return False
    sequence.start(BASICS[key])
    print("trigger", key, key in BASICS, sequence.active, player.invulnerability_timer)
    return sequence.active