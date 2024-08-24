from django.contrib import admin

from .models.game_user.game_user import GameUser
from .models.game.game import Game
from .models.owned_reaction_card.owned_reaction_card import OwnedReactionCard
from .models.game_authentication_token.game_authentication_token \
    import GameAuthenticationToken
from .models.reaction_card_in_shop.reaction_card_in_shop \
    import ReactionCardInShop


#
# Each class adds one entity class and its elements to django admin,
# with specified values for display and search
#

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher_player', 'student_player', "stage")
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main section", {"fields": (
            "teacher_player",'student_player', "stage"
            "next_move_player", "next_move_type", "delayed_tasks")
        }),
    )

@admin.register(GameUser)
class GameUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'conflict_side')
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main", {"fields": ("id", "user_id")}),
        ("Game Data", {"fields": (
            "morale", "money", "conflict_side", "action_moves_left",
            "reaction_moves_left", "opp_played_action_card_id")
        }),
        ("Cards", {"fields":(
            "owned_action_cards", "action_cards_in_shop"
        )})
    )


@admin.register(GameAuthenticationToken)
class GameAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'issued')
    readonly_fields = ('id', 'issued')
    ordering = ("-issued",)
    fields = ('user_id', 'issued')

@admin.register(OwnedReactionCard)
class OwnedReactionCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'reaction_card', 'game_user', 'amount')


@admin.register(ReactionCardInShop)
class ReactionCardInShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'reaction_card', 'game_user', 'amount')
