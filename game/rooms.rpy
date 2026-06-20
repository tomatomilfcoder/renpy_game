init python:
    import random

    class Room(object):
        def __init__(self, id, name, background, exits=None, interactions=None):
            self.id = id
            self.name = name
            self.background = background
            self.exits = exits or {}
            self.interactions = interactions or []

    class RoomInteraction(object):
        def __init__(self, id, name, label, xpos, ypos, xsize=220, ysize=110, image=None, zoom=1.0):
            self.id = id
            self.name = name
            self.label = label
            self.xpos = xpos
            self.ypos = ypos
            self.xsize = xsize
            self.ysize = ysize
            self.image = image
            self.zoom = zoom

    def set_current_room(room_id):
        global current_room_id

        if crash_occurred and room_id == "lounge":
            show_room_phrase(_("Дверь в комнату отдыха не открывается"))
            return

        if room_id in room_db:
            current_room_id = room_id
            renpy.restart_interaction()

    def get_current_room():
        return room_db[current_room_id]

    def room_background(room):
        return Image(room.background)

    def show_room_phrase(message):
        global room_phrase_message

        room_phrase_message = message
        renpy.restart_interaction()

    def hide_room_phrase():
        global room_phrase_message

        room_phrase_message = None
        renpy.restart_interaction()

    FUSE_ITEM_VALUES = {
        "fuse_3": 3,
        "fuse_5": 5,
        "fuse_6": 6,
        "fuse_8": 8,
        "fuse_9": 9,
        "fuse_11": 11,
    }
    FUSE_ITEM_IDS = ["fuse_3", "fuse_5", "fuse_6", "fuse_8", "fuse_9", "fuse_11"]

    def inventory_fuses():
        fuses = []

        for item_id in FUSE_ITEM_IDS:
            value = FUSE_ITEM_VALUES[item_id]
            for _i in range(player_inventory.count(item_id)):
                fuses.append((item_id, value))

        return fuses

    def remove_fuses_from_inventory(fuses):
        removed_by_id = {}

        for item_id, _value in fuses:
            removed_by_id[item_id] = removed_by_id.get(item_id, 0) + 1

        for item_id, amount in removed_by_id.items():
            player_inventory.remove(item_id, amount)

    def collect_storage_fuses_from_room():
        global storage_fuses_collected

        if storage_fuses_collected:
            show_room_phrase(_("Ящик пуст. Все подходящие предохранители уже у меня."))
            return

        player_inventory.add("fuse_3", 1)
        player_inventory.add("fuse_5", 1)
        player_inventory.add("fuse_6", 1)
        player_inventory.add("fuse_8", 1)
        player_inventory.add("fuse_9", 1)
        player_inventory.add("fuse_11", 1)
        storage_fuses_collected = True
        show_room_phrase(_("Я нашёл несколько предохранителей разного сопротивления. Этого должно хватить, если не сжечь нужные варианты."))

    room_db = {
        "cockpit": Room(
            "cockpit",
            _("Капитанская рубка"),
            "cockpit.jpg",
            exits={
                "right": "hall",
            },
            interactions=[]
        ),
        "lounge": Room(
            "lounge",
            _("Комната отдыха"),
            "lounge.png",
            exits={
                "left": "hall",
            },
            interactions=[
                RoomInteraction(
                    "jean",
                    _("Жан"),
                    "jean_dialogue",
                    xpos=900,
                    ypos=1100,
                    image="jean",
                    zoom=0.5,
                ),
            ]
        ),
        "storage": Room(
            "storage",
            _("Склад"),
            "lounge.png",
            exits={
                "up": "hall",
            },
            interactions=[
                RoomInteraction(
                    "fuse_box",
                    _("Ящик с предохранителями"),
                    "collect_storage_fuses",
                    xpos=730,
                    ypos=590,
                    xsize=360,
                    ysize=220,
                ),
                RoomInteraction(
                    "electrical_panel",
                    _("Электрощит"),
                    "electrical_panel",
                    xpos=1190,
                    ypos=440,
                    xsize=330,
                    ysize=260,
                ),
            ],
        ),
        "hall": Room(
            "hall",
            _("Главный коридор"),
            "Hall.png",
            exits={
                "left": "cockpit",
                "right": "lounge",
                "down": "storage",
            },
            interactions=[],
        ),
    }

    def selected_fuse_sum():
        fuses = inventory_fuses()
        return sum(fuses[i][1] for i in selected_fuse_indexes if i < len(fuses))

    def toggle_fuse(index):
        if index in selected_fuse_indexes:
            selected_fuse_indexes.remove(index)
        else:
            selected_fuse_indexes.append(index)

        renpy.restart_interaction()

    def generate_all_magic_squares():
        """
        Возвращает список всех 8 классических магических квадратов 3x3
        (числа 1..9, сумма по всем направлениям = 15).
        """
        base = [
            [2, 7, 6],
            [9, 5, 1],
            [4, 3, 8],
        ]

        def rotate(sq):
            """Поворот на 90 градусов по часовой."""
            return [list(row) for row in zip(*sq[::-1])]

        def reflect(sq):
            """Отражение по горизонтали."""
            return [row[::-1] for row in sq]

        squares = []
        current = base
        for _i in range(4):
            squares.append(current)
            squares.append(reflect(current))
            current = rotate(current)

        unique = []
        for sq in squares:
            if sq not in unique:
                unique.append(sq)
        return unique

    def generate_puzzle():
        """
        Генерирует случайный магический квадрат и его вариант-загадку,
        где центральная строка заменена на '?' (скрыта).
        Возвращает кортеж (полный_квадрат, загадка, центральная_строка_ответ).
        """
        all_squares = generate_all_magic_squares()
        full_square = random.choice(all_squares)

        puzzle = [row[:] for row in full_square]
        center_row_index = 1
        puzzle[center_row_index] = ["?", "?", "?"]

        answer = full_square[center_row_index]

        return full_square, puzzle, answer

    def check_solution(puzzle, user_answer, correct_answer):
        """
        Проверяет, совпадает ли ввод пользователя с правильным ответом.
        user_answer - список из трёх чисел.
        """
        return user_answer == correct_answer

    def start_magic_hash_puzzle():
        global magic_hash_full_square
        global magic_hash_puzzle
        global magic_hash_answer
        global magic_hash_selected
        global magic_hash_message
        global magic_hash_solved

        magic_hash_full_square, magic_hash_puzzle, magic_hash_answer = generate_puzzle()
        magic_hash_selected = []
        magic_hash_message = _("Восстановите скрытую центральную строку.")
        magic_hash_solved = False

    def toggle_magic_hash_number(number):
        if number in magic_hash_selected:
            magic_hash_selected.remove(number)
        elif len(magic_hash_selected) < 3:
            magic_hash_selected.append(number)

        renpy.restart_interaction()

    def submit_magic_hash_solution():
        global magic_hash_solved
        global magic_hash_message

        if len(magic_hash_selected) != 3:
            magic_hash_message = _("Нужно выбрать ровно три числа.")
            renpy.restart_interaction()
            return

        if check_solution(magic_hash_puzzle, magic_hash_selected, magic_hash_answer):
            magic_hash_solved = True
            magic_hash_message = _("Верно! Хеш записан на карту доступа.")
            renpy.restart_interaction()
            return

        magic_hash_message = _("Ошибка. Последовательность не совпала.")
        renpy.restart_interaction()

    def has_possible_fuse_combo(target):
        possible = set([0])

        for _item_id, value in inventory_fuses():
            possible.update([current + value for current in list(possible)])

        return target in possible

    def test_fuse_solution():
        global electrical_power_failed
        global fuse_status_message

        total = selected_fuse_sum()

        if not selected_fuse_indexes:
            fuse_status_message = _("Выберите хотя бы один предохранитель.")
            renpy.restart_interaction()
            return

        available_fuses = inventory_fuses()
        selected_fuses = [available_fuses[i] for i in selected_fuse_indexes if i < len(available_fuses)]

        if total == electrical_target_resistance:
            electrical_power_failed = False
            remove_fuses_from_inventory(selected_fuses)
            selected_fuse_indexes[:] = []
            fuse_status_message = _("Цепь стабилизирована. Электричество восстановлено.")
            renpy.restart_interaction()
            return

        burned_values = [value for _item_id, value in selected_fuses]
        remove_fuses_from_inventory(selected_fuses)

        burned_fuses.extend(burned_values)
        selected_fuse_indexes[:] = []

        if total > electrical_hidden_consumption_limit:
            fuse_status_message = _("Перегрузка. Предохранители сгорели, питание снова выбило.")
        else:
            fuse_status_message = _("Сопротивление не совпало. Предохранители сгорели при проверке.")

        if not has_possible_fuse_combo(electrical_target_resistance):
            fuse_status_message += _(" Подходящей комбинации среди оставшихся предохранителей больше нет.")

        renpy.restart_interaction()


default current_room_id = "lounge"
default jean_dialogue_seen = False
default crash_occurred = False
default storage_fuses_collected = False
default selected_fuse_indexes = []
default burned_fuses = []
default electrical_power_failed = True
default electrical_repair_dialogue_seen = False
default electrical_target_resistance = 17
default electrical_hidden_consumption_limit = 21
default fuse_status_message = "Электричество выбило. Соберите предохранители с суммой сопротивления 17."
default magic_hash_full_square = []
default magic_hash_puzzle = []
default magic_hash_answer = []
default magic_hash_selected = []
default magic_hash_message = ""
default magic_hash_solved = False
default room_phrase_message = None


label room_navigation:
    call screen room_navigation
    jump room_navigation


label blocked_lounge_after_crash:
    Author "Дверь в комнату отдыха не открывается"
    jump room_navigation


label collect_storage_fuses:
    if storage_fuses_collected:
        jump storage_fuses_empty
    else:
        $ player_inventory.add("fuse_3", 1)
        $ player_inventory.add("fuse_5", 1)
        $ player_inventory.add("fuse_6", 1)
        $ player_inventory.add("fuse_8", 1)
        $ player_inventory.add("fuse_9", 1)
        $ player_inventory.add("fuse_11", 1)
        $ storage_fuses_collected = True
        jump storage_fuses_collected


label storage_fuses_empty:
    Author "Ящик пуст. Все подходящие предохранители уже у меня."
    jump room_navigation


label storage_fuses_collected:
    Author "Я нашёл несколько предохранителей разного сопротивления. Этого должно хватить, если не сжечь нужные варианты."
    jump room_navigation


label electrical_panel:
    call screen electricity_minigame
    if not electrical_power_failed and not electrical_repair_dialogue_seen:
        jump after_electrical_repair
    jump room_navigation


label magic_hash_minigame:
    $ start_magic_hash_puzzle()
    while not magic_hash_solved:
        call screen magic_hash_minigame
    return


screen room_navigation():
    modal True

    $ room = get_current_room()

    add room_background(room):
        xysize (1920, 1080)

    frame:
        style "room_title_panel"
        xalign 0.5
        yalign 0.02

        text "[room.name!t]":
            style "room_title_text"

    for interaction in room.interactions:
        if interaction.image:
            imagebutton:
                idle Transform(interaction.image, zoom=interaction.zoom)
                hover Transform(interaction.image, zoom=interaction.zoom, matrixcolor=BrightnessMatrix(0.18))
                action Jump(interaction.label)
                xpos interaction.xpos
                ypos interaction.ypos
                xanchor 0.5
                yanchor 1.0
                alt interaction.name
        else:
            textbutton "[interaction.name!t]":
                style "room_interaction_button"
                if interaction.id == "fuse_box":
                    action Function(collect_storage_fuses_from_room)
                else:
                    action Jump(interaction.label)
                xpos interaction.xpos
                ypos interaction.ypos
                xsize interaction.xsize
                ysize interaction.ysize

    $ exits_unlocked = jean_dialogue_seen or room.id != "lounge"

    if exits_unlocked:
        if "left" in room.exits:
            textbutton "←":
                style "room_arrow_button"
                action Function(set_current_room, room.exits["left"])
                xalign 0.02
                yalign 0.5

        if "right" in room.exits:
            textbutton "→":
                style "room_arrow_button"
                action Function(set_current_room, room.exits["right"])
                xalign 0.98
                yalign 0.5

        if "up" in room.exits:
            textbutton "↑":
                style "room_arrow_button"
                action Function(set_current_room, room.exits["up"])
                xalign 0.5
                yalign 0.04

        if "down" in room.exits:
            textbutton "↓":
                style "room_arrow_button"
                action Function(set_current_room, room.exits["down"])
                xalign 0.5
                yalign 0.94

    if room_phrase_message:
        button:
            style "room_phrase_button"
            action Function(hide_room_phrase)
            xalign 0.5
            yalign 0.98

            text "[room_phrase_message!t]":
                style "room_phrase_text"


screen electricity_minigame():
    modal True

    $ available_fuses = inventory_fuses()

    add "#05070bcc"

    frame:
        style "fuse_game_frame"
        xalign 0.5
        yalign 0.5

        vbox:
            spacing 18

            text _("Аварийный электрощит"):
                style "fuse_game_title"

            text _("Потребитель: автопилот обхода кислотного слоя. Его потребление скрыто. Превышение порога снова выбьет питание."):
                style "fuse_game_text"

            text _("Нужная сумма сопротивления: [electrical_target_resistance]"):
                style "fuse_game_target"

            grid 6 2:
                spacing 10

                for i in range(12):
                    if i < len(available_fuses):
                        textbutton "[available_fuses[i][1]] Ω":
                            style "fuse_button"
                            selected (i in selected_fuse_indexes)
                            action Function(toggle_fuse, i)
                    else:
                        null width 110 height 62

            if not available_fuses:
                text _("В инвентаре нет предохранителей. Их стоит поискать на складе."):
                    style "fuse_game_message"

            hbox:
                spacing 12

                textbutton _("Проверить цепь"):
                    style "fuse_action_button"
                    action Function(test_fuse_solution)

                textbutton _("Вернуться"):
                    style "fuse_action_button"
                    action Return()

            text "[fuse_status_message!t]":
                style "fuse_game_message"

            if burned_fuses:
                text _("Сгоревшие предохранители: [', '.join([str(value) for value in burned_fuses])]"):
                    style "fuse_game_burned"


screen magic_hash_minigame():
    modal True

    add "#05070bcc"

    frame:
        style "magic_hash_frame"
        xalign 0.5
        yalign 0.5

        vbox:
            spacing 18

            text _("Магический хеш"):
                style "magic_hash_title"

            text _("Программатор показывает магический квадрат. Центральная строка скрыта. Восстановите её, чтобы записать хеш на карту доступа."):
                style "magic_hash_text"

            grid 3 3:
                spacing 8
                xalign 0.5

                for row in magic_hash_puzzle:
                    for cell in row:
                        frame:
                            style "magic_hash_cell"

                            text "[cell]":
                                style "magic_hash_cell_text"
                                xalign 0.5
                                yalign 0.5

            text _("Выбрано: [', '.join([str(value) for value in magic_hash_selected]) or '—']"):
                style "magic_hash_text"

            grid 3 3:
                spacing 8
                xalign 0.5

                for number in range(1, 10):
                    textbutton "[number]":
                        style "magic_hash_number_button"
                        selected (number in magic_hash_selected)
                        action Function(toggle_magic_hash_number, number)

            hbox:
                spacing 12
                xalign 0.5

                textbutton _("Проверить"):
                    style "fuse_action_button"
                    action Function(submit_magic_hash_solution)

                textbutton _("Вернуться"):
                    style "fuse_action_button"
                    action Return()

            text "[magic_hash_message!t]":
                style "magic_hash_message"

            if magic_hash_solved:
                textbutton _("Продолжить"):
                    style "fuse_action_button"
                    xalign 0.5
                    action Return()


screen game_timer():
    timer 1800.0 action Jump("bad_ending_timeout")


style room_title_panel is empty
style room_title_text is gui_text
style room_interaction_button is button
style room_arrow_button is button
style room_phrase_button is button
style room_phrase_text is gui_text
style fuse_game_frame is empty
style fuse_game_title is gui_text
style fuse_game_text is gui_text
style fuse_game_target is gui_text
style fuse_game_message is gui_text
style fuse_game_burned is gui_text
style fuse_button is button
style fuse_action_button is button
style magic_hash_frame is empty
style magic_hash_title is gui_text
style magic_hash_text is gui_text
style magic_hash_cell is empty
style magic_hash_cell_text is gui_text
style magic_hash_number_button is button
style magic_hash_message is gui_text

style room_title_panel:
    background Solid("#00000099")
    padding (22, 12)

style room_title_text:
    size 30
    color "#ffffff"
    bold True

style room_interaction_button is default:
    background Solid("#ffffff18")
    hover_background Solid("#ffffff44")
    padding (12, 8)

style room_interaction_button_text:
    size 24
    color "#ffffffcc"
    hover_color "#ffffff"
    outlines [(2, "#000000", 0, 0)]
    xalign 0.5
    yalign 0.5

style room_arrow_button is default:
    background Solid("#00000088")
    hover_background Solid("#ffffff33")
    padding (22, 14)
    xsize 88
    ysize 88

style room_arrow_button_text:
    size 54
    color "#ffffff"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style room_phrase_button is default:
    background Solid("#000000cc")
    hover_background Solid("#111111dd")
    padding (28, 22)
    xsize 1400
    ysize 140

style room_phrase_text:
    size 30
    color "#ffffff"
    xalign 0.5
    yalign 0.5
    text_align 0.5

style fuse_game_frame:
    background Solid("#111722f2")
    padding (32, 28)
    xsize 980

style fuse_game_title:
    size 42
    color "#ffffff"
    bold True

style fuse_game_text:
    size 22
    color "#d7dee9"
    xsize 900

style fuse_game_target:
    size 28
    color "#ffe08a"
    bold True

style fuse_game_message:
    size 24
    color "#ffffff"
    xsize 900

style fuse_game_burned:
    size 20
    color "#ff9f9f"
    xsize 900

style fuse_button is default:
    background Solid("#273142")
    hover_background Solid("#3a4b66")
    selected_background Solid("#5f7eb5")
    padding (16, 10)
    xsize 110
    ysize 62

style fuse_button_text:
    size 24
    color "#ffffff"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style fuse_action_button is default:
    background Solid("#2d5a3d")
    hover_background Solid("#3d7a52")
    padding (20, 10)
    xsize 260

style fuse_action_button_text:
    size 22
    color "#ffffff"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style magic_hash_frame:
    background Solid("#111722f2")
    padding (32, 28)
    xsize 900

style magic_hash_title:
    size 42
    color "#ffffff"
    bold True

style magic_hash_text:
    size 22
    color "#d7dee9"
    xsize 820

style magic_hash_cell:
    background Solid("#202a38")
    xsize 96
    ysize 96

style magic_hash_cell_text:
    size 38
    color "#ffffff"
    bold True

style magic_hash_number_button is default:
    background Solid("#273142")
    hover_background Solid("#3a4b66")
    selected_background Solid("#5f7eb5")
    padding (12, 8)
    xsize 82
    ysize 58

style magic_hash_number_button_text:
    size 26
    color "#ffffff"
    text_align 0.5
    xalign 0.5
    yalign 0.5

style magic_hash_message:
    size 24
    color "#ffffff"
    xsize 820
