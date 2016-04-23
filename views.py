from django.shortcuts import render, redirect
from django.http import HttpResponse
import logging
log = logging.getLogger(__name__)

import random, string

from models import *

def dealCards(num_players):
    villager = Role.objects.get_or_create(label="villager", name="Villager")
    werewolf = Role.objects.get_or_create(label="werewolf", name="Werewolf")
    seer = Role.objects.get_or_create(label="seer", name="Seer")
    deck = [werewolf, werewolf, seer]
    if num_players <= 5:
        deck = [werewolf, villager, villager, villager, seer]
    for i in range(num_players - len(deck)):
        deck.append(villager)
    random.shuffle(deck)
    return deck

def getGame(request):
    if 'game' in request.session:
        game = request.session['game']
        game, created = Game.objects.get_or_create(pk=game)
        return game
    else:
        return None

def register(request):
    if request.method == "POST":
        room, created = Room.objects.get_or_create(name=request.POST['label'].lower(), label=request.POST['label'].lower())
        try:
            game, created = room.games.get_or_create(room=room)
        except Game.MultipleObjectsReturned:
            if room.testing is True:
                game = room.games.filter(room=room).latest('counter')
            else:
                return HttpResponse("Room is already in use. Please make another with a different name")
        if 'username' in request.POST:
            if game.assigned is False or room.testing is True:
                game_turn, created = game.turns.get_or_create(counter=1)
                player, created = game.players.get_or_create(name=request.POST['username'])
                player.turn.add(game_turn)
                request.session['username'] = request.POST['username']
                request.session['room'] = room.label
                request.session['game'] = game.pk
                request.session['player'] = player.as_dict()
                request.session['turn'] = 1
                return redirect("/werewolf/roster/" + request.POST['label'].lower())
            else:
                return HttpResponse("Game has been created. You can't join. Sorry.")
    return render(request, "werewolf/register.html", {
    })

# Create your views here.
def roster(request, label):
    room, created = Room.objects.get_or_create(label=label)
    game = room.games.latest('counter')
    if room is not None:
        return render(request, "werewolf/roster.html", {
            'room': room,
            'game': game,
        })
    else:
        return HttpResponse("Invalid Room")

def remote(request, label):
    game = getGame(request)
    if 'player' in request.session:
        return render(request, "werewolf/remote.html", {'game': game})
    return HttpResponse("Invalid Page")

def result(request, label):
    game = getGame(request)
    return render(request, "werewolf/result.html", {'game': game})

def newGame(request, label):
    room, created = Room.objects.get_or_create(label=label)
    game = room.games.latest('counter')
    game_turn, created = game.turns.get_or_create(counter=1)
    player, created = game.players.get_or_create(name=request.session['username'])
    player.turn.add(game_turn)
    request.session['game'] = game.pk
    request.session['player'] = player.as_dict()
    request.session['turn'] = 1
    return redirect("/werewolf/roster/" + label)
