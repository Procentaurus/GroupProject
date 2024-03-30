CONFLICT_SIDES = (
    ("teacher", "teacher"),
    ("student", "student"),
)

MOVE_TYPES = (
    ("action", "action"),
    ("reaction", "reaction")
)

PLAYER_STATES = (
    ('in_hub', 'in_hub'),
    ('await_clash_start', 'await_clash_start'),
    ('in_clash', 'in_clash'),
    ('await_clash_end', 'await_clash_end'),
)

def increase_card_amount(had_card_earlier, card, amount):
    if had_card_earlier:
        card.amount += amount
        card.save()
    else:
        card.amount == amount
        card.save()

def decrease_card_amount(card, amount):
    if card.amount > amount:
        card.amount -= amount
        card.save()
    elif card.amount == amount:
        card.delete()
