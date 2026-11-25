from sequence import Beat

STEPS = { 
    "game_start": [
        Beat("harry", "HARRY: Alright Barry we made it to the open space. I guess that old man wasn't crazy after all!", open_panel = True, zoom = 3.0, key = "first_flight"),
        Beat("barry", "BARRY: Perhaps. But we'll see how long this thing holds up. He said it was more capable then modern ships if operated properly, but it seems underwhelming.", open_panel = True, zoom = 3.0, key = "first_flight"),
        Beat("harry", "HARRY: I like it! It feels vintage and probably full of crazy stories. Lets see what we can do with it B!", open_panel = True, zoom = 3.0, key = "first_flight"),
        Beat("barry", "BARRY: Alright the flight controls seem simple enough.", open_panel = True, zoom = 3.0, key = "first_flight")
    ],
    "barry_panel": [
        Beat("barry", "BARRY: Looks simple enough. Each button has a description of what it is and the lights indicate if we have the required materials. Auto probably means that the ship will do the work for us. I wonder if I turn it off...", open_panel = True, zoom = 2.0, key = "barry_panel")
    ],
    "harry_panel": [
        Beat("harry", "HARRY: Woah this is totally retro!", open_panel = True, zoom = 2.0, key = "harry_panel"),
        Beat("harry", "HARRY: Yo Barry whats good with these panels man.", open_panel = True, zoom = 2.0, key = "harry_panel"),
        Beat("barry", "BARRY: They seem to be used to tune and tweak the ships performance. We need to collect materials first though.", open_panel = True, zoom = 2.0, key = "harry_panel"),
        Beat("harry", "HARRY: Oh word?!", open_panel = True, zoom = 2.0, key = "harry_panel"),
    ],
    "first_dash": [
        Beat("harry", "HARRY: DAMN B! Yo give me some warning before you move like that.", open_panel = True, key = "first_dash"),
        Beat("barry", "BARRY: Sorry. I think theres more to this ship than I initially though", open_panel = True, key = "first_dash"),
    ],
    "first_grav_preview": [
        Beat("barry", "BARRY: Harry do you see that.", open_panel = True, zoom = 1.5, key = "first_grav_preveiew"),
        Beat("harry", "HARRY: Yea I thought I was tripping but I think it happens everytime I hit the SHIFT on my control panel.", open_panel = True, zoom = 1.5, key = "first_grav_preveiew"),
        Beat("barry", "BARRY: Interesting. It lights up the control for dash on my end. I wonder if we time it together...", open_panel = True, zoom = 1.5, key = "first_grav_preveiew"),
    ],
    "first_scrap": [
        Beat("barry", "BARRY: Scrap ore.I believe we could use those materials to upgrade the ship.", open_panel = True, zoom = 1.5, key = "first_scrap"),
        Beat("harry", "HARRY: I think you can use the panel to spend the scrap on upgrades.", open_panel = True, zoom = 1.5, key = "first_scrap"),
        Beat("barry", "BARRY: It looks like we don't have enough yet. I think these lights might signal if we have enough.", zoom = 1.5, open_panel = True, key = "first_scrap")        
    ],
    "first_hit": [
        Beat("harry", "HARRY: Barry, watch where you are flying man.", key = "first_hit"),
        Beat("barry", "BARRY: This ship is not as responsive as you would think.", key = "first_hit")
    ],
}


def trigger(sequence, key, player):
    if key not in STEPS or sequence.active:
        print("trigger", key, key in STEPS, sequence.active, player.invulnerability_timer)
        return False
    if player.invulnerability_timer > 0:    # so we dont trigger a beats mid hit
        print("trigger", key, key in STEPS, sequence.active, player.invulnerability_timer)
        return False
    sequence.start(STEPS[key], player)
    print("trigger", key, key in STEPS, sequence.active, player.invulnerability_timer)
    return sequence.active