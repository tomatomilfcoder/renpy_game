init python:

    INVENTORY_COLS = 7
    INVENTORY_ROWS = 3
    INVENTORY_TOTAL_SLOTS = INVENTORY_COLS * INVENTORY_ROWS

    class Item(object):
        def __init__(self, id, name, description, icon=None, usable=False, max_stack=99, use_label=None):
            self.id = id
            self.name = name
            self.description = description
            self.icon = icon
            self.usable = usable
            self.max_stack = max_stack
            self.use_label = use_label

    class Inventory(object):
        def __init__(self):
            self.slots = {}

        @property
        def capacity(self):
            return inventory_unlocked

        def count(self, item_id):
            return self.slots.get(item_id, 0)

        def has(self, item_id, amount=1):
            return self.count(item_id) >= amount

        def add(self, item_id, amount=1, notify_player=True):
            item = item_db.get(item_id)
            if item is None:
                return False

            current = self.count(item_id)
            gained = min(amount, item.max_stack - current)

            if gained <= 0:
                return False

            if current == 0 and len(self.slots) >= self.capacity:
                renpy.notify(_("Инвентарь полон."))
                return False

            self.slots[item_id] = current + gained

            if notify_player:
                renpy.notify(_("Получено: [name] x[count]").format(name=item.name, count=gained))

            return True

        def remove(self, item_id, amount=1):
            if not self.has(item_id, amount):
                return False

            self.slots[item_id] -= amount
            if self.slots[item_id] <= 0:
                del self.slots[item_id]
            return True

        def entries(self):
            result = []
            for item_id in sorted(self.slots.keys()):
                item = item_db.get(item_id)
                if item is not None:
                    result.append((item, self.slots[item_id]))
            return result

        def grid_slots(self):
            entries = self.entries()
            slots = []

            for i in range(INVENTORY_TOTAL_SLOTS):
                if i >= inventory_unlocked:
                    slots.append({"state": "locked"})
                elif i < len(entries):
                    item, count = entries[i]
                    slots.append({"state": "filled", "item": item, "count": count})
                else:
                    slots.append({"state": "empty"})

            return slots

    item_db = {}

    def register_item(item):
        item_db[item.id] = item
        return item

    def get_item(item_id):
        return item_db.get(item_id)

    def use_inventory_item(item_id):
        item = get_item(item_id)
        if item is None or not player_inventory.has(item_id):
            return

        if not item.usable:
            renpy.notify(_("Этот предмет нельзя использовать."))
            return

        if item.use_label:
            renpy.call_in_new_context(item.use_label)
        else:
            player_inventory.remove(item_id)
            renpy.notify(_("Использовано: [name]").format(name=item.name))


define item_antidote = register_item(Item(
    "antidote",
    _("Антидот"),
    _("Снимает действие яда."),
    icon="#2d8a4e",
    usable=True,
    max_stack=5,
    use_label="use_antidote",
))

define item_bandage = register_item(Item(
    "bandage",
    _("Бинт"),
    _("Обычный бинт."),
    icon="#c9a86c",
    usable=True,
    max_stack=10,
))

define item_lube = register_item(Item(
    "lube",
    _("Смазка"),
    _("На всякий случай."),
    icon="#66c1e0",
    usable=False,
    max_stack=3,
))

default player_inventory = Inventory()
default inventory_unlocked = 7


label give_item(item_id, amount=1):
    $ player_inventory.add(item_id, amount, notify_player=True)
    return

label remove_item(item_id, amount=1):
    $ player_inventory.remove(item_id, amount)
    return

label open_inventory:
    call screen inventory
    return

label use_antidote:
    if not player_inventory.has("antidote"):
        return

    $ player_inventory.remove("antidote")
    return


screen inventory():

    modal True
    zorder 200

    default selected_item = False

    add "#000000cc"

    frame:
        style "inventory_frame"
        xalign 0.5
        yalign 0.5

        vbox:
            spacing 16

            ## Header
            fixed:
                xsize 980
                ysize 50

                text _("Инвентарь"):
                    style "inventory_title"
                    yalign 0.5

                textbutton "✕":
                    style "inventory_close_button"
                    xalign 1.0
                    yalign 0.5
                    action Hide("inventory")

            ## Slot grid (7 x 3)
            grid INVENTORY_COLS INVENTORY_ROWS:
                style_prefix "inventory"
                xalign 0.5
                spacing 10

                for slot in player_inventory.grid_slots():

                    if slot["state"] == "locked":
                        frame:
                            style "inventory_slot_locked"

                            text "🔒":
                                style "inventory_lock_icon"
                                xalign 0.5
                                yalign 0.5

                    elif slot["state"] == "empty":
                        frame:
                            style "inventory_slot_empty"

                    else:
                        $ item = slot["item"]
                        $ count = slot["count"]

                        button:
                            style "inventory_slot_button"
                            action SetScreenVariable("selected_item", item)
                            selected (selected_item == item)

                            fixed:
                                xysize (128, 128)

                                text "[item.name!t]":
                                    style "inventory_slot_name"
                                    xalign 0.5
                                    ypos 6

                                add Solid(item.icon):
                                    xalign 0.5
                                    yalign 0.5
                                    xysize (72, 72)

                                text "x[count]":
                                    style "inventory_slot_qty"
                                    xalign 1.0
                                    yalign 1.0
                                    xoffset -8
                                    yoffset -6

            ## Description (below grid, scrollable)
            if selected_item and player_inventory.has(selected_item.id):
                frame:
                    style "inventory_desc_panel"

                    vbox:
                        spacing 10

                        text "[selected_item.name!t]":
                            style "inventory_item_name"

                        viewport:
                            style "inventory_desc_viewport"
                            scrollbars "vertical"
                            mousewheel True
                            draggable True

                            text "[selected_item.description!t]":
                                style "inventory_item_description"

                        if selected_item.usable:
                            textbutton _("Использовать"):
                                style "inventory_use_button"
                                xalign 0.5
                                action Function(use_inventory_item, selected_item.id)

            else:
                frame:
                    style "inventory_desc_panel"

                    text _("Нажмите на предмет, чтобы прочитать описание."):
                        style "inventory_hint_text"
                        xalign 0.5
                        yalign 0.5

    key "game_menu" action Hide("inventory")
    key "K_ESCAPE" action Hide("inventory")


screen inventory_button():

    zorder 99

    if quick_menu:
        textbutton _("Инвентарь"):
            style "inventory_hud_button"
            xalign 1.0
            yalign 0.0
            xoffset -30
            yoffset 30
            action Show("inventory")


init python:
    config.overlay_screens.append("inventory_button")


style inventory_frame is empty
style inventory_title is gui_text
style inventory_close_button is button
style inventory_slot_button is button
style inventory_slot_empty is empty
style inventory_slot_locked is empty
style inventory_slot_name is gui_text
style inventory_slot_qty is gui_text
style inventory_lock_icon is gui_text
style inventory_desc_panel is empty
style inventory_desc_viewport is gui_viewport
style inventory_item_name is gui_text
style inventory_item_description is gui_text
style inventory_hint_text is gui_text
style inventory_use_button is button
style inventory_hud_button is quick_button

style inventory_frame:
    background Solid("#111111ee")
    padding (28, 24)
    xsize 1040

style inventory_title:
    size 40
    color "#ffffff"
    bold True

style inventory_close_button is default:
    background None
    padding (12, 8)
    xsize 48
    ysize 48

style inventory_close_button_text:
    size 36
    color "#e74c3c"
    hover_color "#ff6b6b"
    selected_color "#e74c3c"
    insensitive_color "#e74c3c"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style inventory_slot_button is default:
    background Solid("#252525")
    hover_background Solid("#353535")
    selected_background Solid("#3d4a5c")
    padding (0, 0)
    xsize 128
    ysize 128

style inventory_slot_empty:
    background Solid("#1a1a1a")
    xsize 128
    ysize 128

style inventory_slot_locked:
    background Solid("#1a1a1a")
    xsize 128
    ysize 128

style inventory_slot_name:
    size 16
    color "#cccccc"
    text_align 0.5
    xmaximum 120

style inventory_slot_qty:
    size 18
    color "#ffffff"
    bold True
    outlines [(2, "#000000", 0, 0)]

style inventory_lock_icon:
    size 36
    color "#666666"

style inventory_desc_panel:
    background Solid("#1a1a1a")
    padding (16, 14)
    xsize 980
    ysize 160

style inventory_desc_viewport:
    xsize 948
    ysize 90

style inventory_item_name:
    size 28
    color gui.accent_color
    bold True

style inventory_item_description:
    size 22
    color "#dddddd"
    xsize 920
    line_spacing 5

style inventory_hint_text:
    size 22
    color "#888888"
    xalign 0.5
    textalign 0.5

style inventory_use_button is default:
    background Solid("#2d5a3d")
    hover_background Solid("#3d7a52")
    padding (24, 10)
    xsize 200

style inventory_use_button_text:
    size 22
    color "#ffffff"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style inventory_hud_button:
    properties gui.button_properties("quick_button")