from sequence import Beat

STEPS = { 
    "game_start": [
        Beat("harry", "HARRY: Alright Barry we made it to the open space. I guess that old man wasn't crazy after all!", zoom = 3.0, key = "first_flight"),
        Beat("barry", "BARRY: Perhaps. But we'll see how long this thing holds up. He said it was more capable then modern ships if operated properly, but it seems underwhelming.", zoom = 3.0, key = "first_flight"),
        Beat("harry", "HARRY: I like it! It feels vintage and probably full of crazy stories. Lets see what we can do with it B!", zoom = 3.0, key = "first_flight"),
        Beat("barry", "BARRY: Alright the flight controls seem simple enough.", zoom = 3.0, key = "first_flight")
    ],
    "open_panel": [
        Beat("barry", "BARRY: Seems simple enough. Each button has a description of what it is and the lights indicate if we have the required materials. Auto probably means that the ship will do the work for us. I wonder if I turn it off...", zoom = 2.0, key = "open_panel"),
        Beat("harry", "HARRY: Woah this is totally retro!", zoom = 2.0, key = "open_panel"),
        Beat("harry", "HARRY: Yo Barry whats good with these panels again man.", zoom = 2.0, key = "open_panel"),
        Beat("barry", "BARRY: ...", zoom = 2.0, key = "open_panel"),
        Beat("barry", "BARRY: If you click blinky light ship get better.", zoom = 2.0, key = "open_panel"),
        Beat("harry", "HARRY: Oh word?!", zoom = 2.0, key = "open_panel"),
    ],
    "first_dash": [
        Beat("harry", "HARRY: DAMN B! Yo give me some warning before you move like that.", key = "first_dash"),
        Beat("barry", "BARRY: Sorry. I think I figured out what 'ABILITY' this ship has...", key = "first_dash"),
    ],
    "first_grav_preview": [
        Beat("barry", "BARRY: Harry do you see that.", zoom = 1.5, key = "first_grav_preveiew"),
        Beat("harry", "HARRY: Yea I thought I was tripping but I think it happens everytime I hit this pedal with my foot.", zoom = 1.5, key = "first_grav_preveiew"),
        Beat("barry", "BARRY: Interesting. It lights up the control for dash on my end. I wonder if we time it together...", zoom = 1.5, key = "first_grav_preveiew"),
    ],
    "first_scrap": [
        Beat("barry", "BARRY: Scrap ore. I believe we could use those materials to upgrade the ship.", zoom = 1.5, key = "first_scrap"),
        Beat("harry", "HARRY: Oh Hell Yea! Give it a try B!", zoom = 1.5, key = "first_scrap"),
        Beat("barry", "BARRY: I guess I'll start with whatever 'ABILITY' is.", zoom = 1.5, wait_for = "ability", key = "first_scrap"),       
    ],
    "first_salvage": [
        Beat("barry", "BARRY: Looks like some of the salvage from that cargo drone was collected by the ship.", zoom = 1.5, key = "first_salvage"),
        Beat("harry", "HARRY: Sweet! What do I do?", zoom = 1.5, key = "first_salvage"),
        Beat("barry", "BARRY: Just click the flashing light.", zoom = 1.5, wait_for = "LASER", key = "first_salvage"),
        Beat("harry", "HARRY: Wooorrrd.", zoom = 1.5, key = "first_salvage"),
    ],
    "first_hit": [
        Beat("harry", "HARRY: Barry, watch where you are flying man.", key = "first_hit"),
        Beat("barry", "BARRY: This ship is not as responsive as you would think.", key = "first_hit")
    ],
    "auto_buy": [
        Beat("barry", "BARRY: Just as I thought the ship will spend the resources we collect if we don't do it quick enough.", key = "auto_buy"),
        Beat("harry", "HARRY: That's kind of whack. Does the ship think we are stupid or something.", key = "auto_buy"),
        Beat("barry", "BARRY: I'm sure that's what that auto light indicates. It's probably a toggle.", key = "auto_buy"),
        Beat("harry", "HARRY: Oh tight!", key = "auto_buy"),
    ],
    "cannon_heat": [
        Beat("harry", "HARRY: Yo the cannon stopped working B!", key = "cannon_heat"),
        Beat("barry", "BARRY: It's probably overheated. I'm sure one of the tabs on your panel will show the temp.", key = "cannon_heat"),
        Beat("barry", "BARRY: If you keep your panel open you could probably control the temp better. But I guess it would be kind of hard to see.", key = "cannon_heat"),
        Beat("harry", "HARRY: Panel...tab..temp.", key = "cannon_heat"),
        Beat("harry", "HARRY: Man this ship is way more analog then i thought.", key = "cannon_heat"),
        Beat("harry", "HARRY: Rad.", key = "cannon_heat"),
    ],
    "laser": [
        Beat("harry", "HARRY: This laser is totally stripes yo!", key="laser"),
        Beat("harry", "HARRY: Now you can focus on dodgin and I can shoot wherever I want!", key="laser"),
        Beat("barry", "BARRY: Cool.", key="laser"),
    ]
}


def trigger(sequence, key, player):
    if key not in STEPS or sequence.active:
        return False
    if player.invulnerability_timer > 0:    # so we dont trigger a beats mid hit
        return False
    sequence.start(STEPS[key], player)
    return sequence.active