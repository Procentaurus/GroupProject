# cards.py

class Card:
    def __init__(self, name, description, price, player_type):
        self.name = name
        self.description = description
        self.price = price
        self.player_type = player_type

class ActionCard(Card):
    def __init__(self, name, description, price, player_type, pressure):
        super().__init__(name, description, price, player_type)
        self.pressure = pressure

    def calculate_damage(self):
        # Simple example assuming damage is specified as 'Deal X damage'
        damage_amount = int(self.description.split()[1])
        return damage_amount

class ReactionCard(Card):
    def __init__(self, name, description, values, price, player_type, card_type):
        self.name = name
        self.description = description
        self.values = self.parse_values(values)
        self.price = price
        self.player_type = player_type
        self.card_type = card_type

    def parse_values(self, values):
        return dict(item.split('=') for item in values.split(';'))

    def apply_reaction(self, action_damage):
        blocked_damage = 0
        redirected_damage = 0
        condition_satisfied = self.check_conditions(blocked_damage, redirected_damage)
        percentage_value = self.values.get('percentage_value', None)

        blocked_damage = self.apply_block_effect(blocked_damage, condition_satisfied)
        redirected_damage = self.apply_redirect_effect(redirected_damage, condition_satisfied)
        blocked_damage, redirected_damage = self.apply_percentage_modifications(
            action_damage, blocked_damage, redirected_damage, percentage_value
        )

        return action_damage - blocked_damage, redirected_damage

    def check_conditions(self, blocked_damage, redirected_damage):
        condition_satisfied = True
        if 'conditional_value' in self.values:
            conditional_value = self.values['conditional_value']
            threshold = int(self.values.get('conditional_threshold', 0))

            if conditional_value == 'blocked' and blocked_damage <= threshold:
                condition_satisfied = False
            elif conditional_value == 'redirected' and redirected_damage <= threshold:
                condition_satisfied = False
        return condition_satisfied

    def apply_block_effect(self, blocked_damage, condition_satisfied):
        if 'block' in self.values and condition_satisfied:
            blocked_damage += int(self.values['block'])
        return blocked_damage

    def apply_redirect_effect(self, redirected_damage, condition_satisfied):
        if 'redirect' in self.values and condition_satisfied:
            redirected_damage += int(self.values['redirect'])
        return redirected_damage

    def apply_percentage_modifications(self, action_damage, blocked_damage, redirected_damage, percentage_value):
        if percentage_value == 'blocked':
            blocked_damage += action_damage * 0.01 * int(self.values.get('percentage', 0))
        elif percentage_value == 'redirected':
            redirected_damage += action_damage * 0.01 * int(self.values.get('percentage', 0))
        return blocked_damage, redirected_damage


class CardFactory:
    @staticmethod
    def create_card(card_data):
        card_type = card_data["model"].split(".")[-1]
        fields = card_data["fields"]

        if card_type == "actioncard":
            return ActionCard(
                name=fields["name"],
                description=fields["description"],
                price=int(fields["price"]),
                player_type=fields["playerType"],
                pressure=int(fields["pressure"]),
            )
        elif card_type == "reactioncard":
            return ReactionCard(
                name=fields["name"],
                description=fields["description"],
                values=fields["values"],
                price=int(fields["price"]),
                player_type=fields["playerType"],
                card_type=fields["type"],
            )
        else:
            raise ValueError("Unknown card type")
