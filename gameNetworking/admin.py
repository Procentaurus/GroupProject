from django.contrib import admin

from .models.game_user.game_user import GameUser
from .models.game.game import Game
from .models.game_archive.game_archive import GameArchive
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
    list_display = ('id', 'teacher_player', 'student_player')
    readonly_fields = ('id',)
    add_fieldsets = (
        ("Main section", {"fields": (
            "teacher_player",'student_player',
            "next_move_player", "next_move_type")
        }),
    )


@admin.register(GameArchive)
class GameArchiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'teacher_player', 'student_player')
    readonly_fields = ('id',)
    ordering = ('-start_date', "-start_time")
    add_fieldsets = ((
        "Players", {"fields": (
            "teacher_player",'student_player'
            )},
        "Game info", {"fields":('start_date', 'start_time',
            'lenght_in_sec', 'winner')}
        ),
    )

@admin.register(GameUser)
class GameUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'conflict_side')
    readonly_fields = ('id', 'user')
    add_fieldsets = (
        ("Main", {"fields": ("id", "user")}),
        ("Game Data", {"fields": (
            "state", "morale", "money", "conflict_side")}),
        ("Cards", {"fields":(
            "owned_action_cards", "action_cards_in_shop"
        )})
    )


@admin.register(GameAuthenticationToken)
class GameAuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issued')
    readonly_fields = ('id','issued')
    ordering = ("-issued",)
    add_fieldsets = (
        ("Main section", {"fields": ("user",)}),
    )


@admin.register(OwnedReactionCard)
class OwnedReactionCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'reaction_card', 'game_user', 'amount')


@admin.register(ReactionCardInShop)
class ReactionCardInShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'reaction_card', 'game_user', 'amount')
