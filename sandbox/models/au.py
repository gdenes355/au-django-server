import secrets
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from django.utils.translation import gettext_lazy as _

import random

__all__ = ['AUGame', 'AUPlayer']


class AUGame(models.Model):

    state = models.CharField(_('state'), max_length=16, default="Lobby")

    code = models.CharField(_('code'), max_length=6, default="CODE", unique=True)

    target = models.IntegerField(default=0)
    
    def find_col(self):
        cols = set(['c51111', '132ed1', '117f2d', 'ed54ba', 'efd0d', 'f5f557', '3f474e', 'd6e0f0', '6b2fbb', '71491e', '38fedc', '50ef39'])
        for player in self.players.all():
            cols.remove(player.col)
        return random.sample(cols, 1)[0]

class AUPlayer(models.Model):
    
    game = models.ForeignKey(AUGame, on_delete=models.CASCADE, verbose_name=_('token'), related_name='players')
    name = models.CharField(max_length=16, default="")

    vx = models.FloatField(default=0)
    vy = models.FloatField(default=0)
    xs = models.TextField(default="")
    ys = models.TextField(default="")
    seq = models.IntegerField(default=0)  # sequence numbers

    col = models.CharField(_('code'), max_length=6, default="ff0000")

    mask = models.IntegerField(default=0)            #  1:DEAD, 2:IMPOSTOR, 4:VOTED_OUT, 8:CALLED_VOTE
    e_id =  models.IntegerField(default=0)   # external id
    timestamp = models.DateTimeField(auto_now_add=True)
