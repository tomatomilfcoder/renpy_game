image jerma menacing = "jerma menacing.png"
image jerma happy = "jerma happy.png"
image bg men:
    "men.jpg"
    xysize(1920, 1080)

define jerma = Character("Jerma")

label start:
    $ player_inventory.add("antidote", 1, False)
    $ player_inventory.add("bandage", 2, False)
    $ player_inventory.add("lube", 1, False)
    jump start_scene

label start_scene:
    scene bg men

    show jerma happy at right
    with dissolve

    jerma "Съел бутерброд, умираю, помоги."

    if player_inventory.has("antidote"):
        menu:
            "Дать антидот":
                $ player_inventory.remove("antidote")
                jerma "Спасибо."

            "Ничего не делать":
                show jerma menacing at right
                jerma "Ты заплатишь."
    else:
        jerma "Предатель Родины"
    return