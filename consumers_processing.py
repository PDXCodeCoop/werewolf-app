from models import Room, Game, Turn, Role, Player, Vote

from consumers_functions import *


def process_vote(data):
    output = {}
    try:
        game = Game.objects.get(pk=data['game'])
        target = Player.objects.get(pk=data['target'])
        turn = Turn.objects.get(pk=data['turn'])
        voter = Player.objects.get(pk=data['voter'])
        category = data['category']
        current_turn = turn
    except Game.DoesNotExist:
        log.error("Game DNE")
        return
    except Player.DoesNotExist:
        log.error("Player DNE")
        return

    setVote(current_turn, voter, target, category)
    playerVotes = Vote.objects.filter(turn=current_turn, category="player")
    wwVotes = Vote.objects.filter(turn=current_turn, category="werewolf")
    werewolves = current_turn.players.filter(role=Role.objects.get(label="werewolf"))
    #Check that the number of votes = num of players AND that werewolves agreed on a kill
    try:
        if (playerVotes.count() == current_turn.players.count()
            and wwVotes.values('target').annotate(count=Count('target')).order_by('-count')[0]['count'] == werewolves.count()
            and Vote.objects.filter(turn=current_turn, category="seer").count() == current_turn.players.filter(role=Role.objects.get(label="seer")).count()
            ):
            players = current_turn.players.all()
            playerTarget = tallyVotes(playerVotes)
            survivors = killPlayer(playerTarget, players)
            wwTarget = tallyVotes(wwVotes)
            survivors = killPlayer(wwTarget, survivors)
            current_turn = nextTurn(game, turn, survivors)
            werewolf_count = current_turn.players.filter(role=Role.objects.get(label="werewolf")).count()
            human_count = current_turn.players.exclude(role=Role.objects.get(label="werewolf")).count()
            if werewolf_count <= 0:
                game.winner = "humans"
                game.save()
                output['finished'] = True
            elif werewolf_count >= human_count:
                game.winner = "werewolves"
                game.save()
                output['finished'] = True
            else:
                pass
    except IndexError:
        pass
    output['turn'] = current_turn.as_dict()
    return output
