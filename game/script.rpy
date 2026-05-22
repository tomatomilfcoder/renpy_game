image jermamenacing = "jerma menacing.png"
image jermahappy = "jerma happy.png"
image bg men:
    "men.jpg"
    xysize(1920, 1080)

define g1 = Character("Gay 1")
define g2 = Character("Gay 2")

label start:
    $ player_inventory.add("antidote", 1, False)
    $ player_inventory.add("bandage", 2, False)
    $ player_inventory.add("lube", 1, False)
    jump sex

label sex:
    scene bg men

    show jermamenacing at left
    with dissolve

    g1 "Бля меня змея укусила в хуй"

    show jermahappy at right
    with dissolve

    if player_inventory.has("antidote"):
        menu:
            "Дать антидот":
                $ player_inventory.remove("antidote")
                g2 "Держи, выпей — должно помочь."
                g1 "Ага, уже не так страшно."
            "Открыть инвентарь":
                call open_inventory
                jump sex_after_bite
            "Ничего не делать":
                g2 "Ну тогда сам как-нибудь..."
    else:
        g2 "Блин, антидота нет. Может, в инвентаре что-то есть?"

    label sex_after_bite:
    g2 "Пиздец дай пососу"

    return