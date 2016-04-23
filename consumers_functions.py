from django.db.models import Count
from models import Room, Game, Turn, Role, Player, Vote
from collections import Counter

import logging
log = logging.getLogger(__name__)
import random, string



def getPlayers(game):
    players = []
    for player in game.players.all():
        players.append(player.as_dict())
    return players

def killPlayer(pkill_id, players):
    killed_player = Player.objects.get(pk = pkill_id)
    return players.exclude(pk=killed_player.pk)

def nextTurn(game, turn, survivors):
    next_turn, created = Turn.objects.get_or_create(game = game, counter=(turn.counter + 1))
    for survivor in survivors:
        survivor.turn.add(next_turn)
    return next_turn

#Bug: The first vote always tries to write two...
def setVote(turn, voter, target, category):
    try:
        vote, created = Vote.objects.get_or_create(turn=turn, voter=voter, category=category)
        vote.target = target
        vote.save()
        vote, created = Vote.objects.get_or_create(turn=turn, voter=voter, category=category)
    except Vote.MultipleObjectsReturned:
        Vote.objects.filter(turn=turn, voter=voter, category=category).delete()

def tallyVotes(votes):
    result = votes.values('target').annotate(count=Count('target')).order_by('-count')
    try:
        if result[0]['count'] == result[1]['count']:
            log.debug("It's a TIE")
            votes.delete()
        else:
            return result[0]['target']
    except IndexError:
        return result[0]['target']

def dealCards(num_players):
    villager = Role.objects.get_or_create(label="villager", name="Villager")
    werewolf = Role.objects.get_or_create(label="werewolf", name="Werewolf")
    seer = Role.objects.get_or_create(label="seer", name="Seer")
    deck = [werewolf, werewolf, seer]
    if num_players <= 3:
        deck = [werewolf, villager, villager]
    for i in range(num_players - len(deck)):
        deck.append(villager)
    random.shuffle(deck)
    return deck

def processRoles(game_id):
    try:
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        log.error("Game DNE")
        return
    if game.assigned is False:
        deck = dealCards(game.players.count())
        for player in game.players.all():
            role, created = deck.pop()
            player.role = role
            player.save()
        game.assigned = True
        game.save()
        return True
    return False

def createNewGame(room, old_game):
    new_game, created = room.games.get_or_create(counter=(old_game.counter + 1))
    new_turn, created = new_game.turns.get_or_create(counter=1)
    return new_game.as_dict()
