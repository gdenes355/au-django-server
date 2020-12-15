from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

import json
import random 

from sandbox.models.au import AUGame, AUPlayer


def fetch_full_game_as_dict(code):
    game = AUGame.objects.filter(code=code).prefetch_related('players').first()
    res = dict()
    res["state"] = game.state
    res["target"] = game.target
    res["players"] = list()
    players = AUPlayer.objects.filter(game__id=game.id).all()
    for player in players:
        res["players"].append(dict(
            xs=player.xs,
            ys=player.ys,
            vx=player.vx,
            vy=player.vy,
            seq=player.seq,
            col=player.col,
            id=player.e_id,
            mask=player.mask,
            name=player.name
        ))
    return res

def meet_to_vote(gameid, player):
    game = AUGame.objects.filter(code=gameid).prefetch_related('players').first()
    game.state = "Voting"
    game.save()
    for aplayer in game.players.all():
        aplayer.mask = aplayer.mask & ~8
        aplayer.save(update_fields=["mask"])

    if player is not None:
        player.mask = player.mask | 8
        player.save(update_fields=["mask"])

def start_game(gameid):
    game = get_object_or_404(AUGame, code=gameid)
    game.state =  "Game"
    players = list(AUPlayer.objects.filter(game__id=game.id).all())
    game.target = (len(players) - 2) * 5
        
    impostors = random.sample(players, 2)
    for imp in impostors:
        imp.mask = 2
        imp.save(update_fields=['mask'])

    game.save()

def create_game(gameid):
    prevgame = AUGame.objects.filter(code=gameid)
    if prevgame is not None:
        prevgame.delete()
    game = AUGame(code=gameid)
    game.save()
    return JsonResponse({})


class ListView(View):
    def get(self, request):
        codes = AUGame.objects.values_list('code', flat=True)
        return JsonResponse({'data': list(codes)}) 


class JoinView(View):

    def get(self, request):
        name = request.GET.get('name')
        if len(name) > 16:
            name = name[0:16]

        id = int(request.GET.get('id'))
        gameid = int(request.GET.get('gameid'))

        game = AUGame.objects.filter(code=gameid).prefetch_related('players').first()
 
        player = AUPlayer(name=name, e_id=id)
        player.col = game.find_col()
        player.game = game
        player.save()

        return JsonResponse({'data': fetch_full_game_as_dict(gameid)})


class UpdateView(View):

    def get(self, request):
        id = int(request.GET.get('id'))
        gameid = int(request.GET.get('gameid'))
        return JsonResponse({'data': fetch_full_game_as_dict(gameid)})

    def post(self, request):
        update = json.loads(request.body.decode('utf-8'))
        id = int(request.GET.get('id'))
        gameid = int(request.GET.get('gameid'))

        player = AUPlayer.objects.filter(e_id=id, game__code=gameid).first()
        if player is None:
            return JsonResponse({}, status=404)

        player.xs = update["xs"]
        player.ys = update["ys"]
        player.vx = update["vx"]
        player.vy = update["vy"]
        player.seq = update["seq"]
        player.save(update_fields=["xs", "ys", "vx", "vy", "seq"])
        return JsonResponse({'data': fetch_full_game_as_dict(gameid)})


class KillView(View):
    def get(self, request):
        who = int(request.GET.get('who'))
        whom = int(request.GET.get('whom'))
        gameid = int(request.GET.get('gameid'))
        player_who = AUPlayer.objects.filter(e_id=who, game__code=gameid).first()
        player_whom = AUPlayer.objects.filter(e_id=whom, game__code=gameid).first()
        if player_who is not None and player_whom is not None:
            player_whom.mask = player_whom.mask | 1
            player_whom.save(update_fields=["mask"])
        return JsonResponse({})


class ReportView(View):
    def get(self, request):
        who = int(request.GET.get('who'))
        whom = int(request.GET.get('whom'))
        gameid = int(request.GET.get('gameid'))
        player_who = AUPlayer.objects.filter(e_id=who, game__code=gameid).first()
        player_whom = AUPlayer.objects.filter(e_id=whom, game__code=gameid).first()
        if player_who is not None and player_whom is not None:
            meet_to_vote(gameid, player_who)
        return JsonResponse({})


class PointView(View):
    def get(self, request):
        gameid = int(request.GET.get('gameid'))
        amount = int(request.GET.get('amount'))
        game = AUGame.objects.filter(code=gameid).first()
        game.target = game.target + amount
        game.save(update_fields=["target"])
        return JsonResponse({})


class DahsboardView(View):
    ''' UI for managing the game '''

    @method_decorator(login_required)
    def get(self, request):
        gameid = request.GET.get('gameid')
        game = AUGame.objects.filter(code=gameid).prefetch_related('players').first()
        players = game.players.all() if game is not None else []
        imp_count = 0
        crew_count = 0
        for player in players:
            player.impostor = (player.mask & 2) == 2
            
            if (player.mask & 1) == 1:
                player.state = "Christmas treed"
            elif (player.mask & 4) == 4:
                player.state = "Voted out"
            else:
                if (player.mask & 8) == 8:
                    player.state = "Called vote"
                else:
                    player.state = "Playing"
                if (player.mask & 2) == 2:
                    imp_count += 1
                else:
                    crew_count += 1
        outcome = ''
        if game is not None and (game.target < 1 or imp_count == 0):
            outcome = 'Class wins'
        elif imp_count >= crew_count:
            outcome = 'Santas win!'

        args = dict(
            game=game,
            players=players,
            outcome=outcome
        )
        return render(request, 'sandbox/index.html', args)

    @method_decorator(login_required)
    def post(self, request):
        gameid = request.GET.get('gameid')
        cmd = request.POST.get('cmd')
        if cmd == 'vo':
            id = request.POST.get('id')
            player = AUPlayer.objects.filter(id=id).first()
            player.mask = player.mask | 4
            player.save(update_fields=["mask"])
        elif cmd == 'rm':
            id = request.POST.get('id')
            AUPlayer.objects.filter(id=id).delete()
        elif cmd == 'vote':
            meet_to_vote(gameid, None)
        elif cmd == 'resume':
            game = AUGame.objects.filter(code=gameid).first()
            game.state = "Game"
            game.save()
        elif cmd == 'start':
            start_game(gameid)
        elif cmd == 'create':
            create_game(gameid)

        return HttpResponseRedirect(request.path_info + '?gameid=' + gameid)
