# game/levels/level_chase.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import pyxel
from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.core.timeline import Timeline, TimelineManager
from game.objects.base import LevelObject, Which, Action
from game.objects.pickable import Key
from game.objects.key_wall import KeyWall
from game.objects.flag import Flag

# ---- key ids (reuse 1 as dark yellow / gold) ----
KEY_GOLD = 1  # matches the yellow/gold in your other levels (color 9)


class LevelChase(LevelBase):
    """
    A seed ghost (ghost id 0) runs along a recorded path while *carrying* a golden key.
    The player must steal the key and open the golden wall to reach the flag.
    """

    name: str = "Chase"
    difficulty: int = 2
    start_room: str = "A"
    max_cursors: int = 1
    loop_seconds: int = (
        15  # adjust if you want a longer/shorter loop; ghost is truncated to loop length
    )

    # ──────────────────────────────────────────────────────────────────────────
    # Paste the raw printed coordinates here. Keep the exact "pyxel.mouse_x=..pyxel.mouse_y=.." format.
    _RAW_TRACE: str = r"""
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=86pyxel.mouse_y=96
pyxel.mouse_x=84pyxel.mouse_y=97
pyxel.mouse_x=65pyxel.mouse_y=99
pyxel.mouse_x=52pyxel.mouse_y=99
pyxel.mouse_x=44pyxel.mouse_y=100
pyxel.mouse_x=41pyxel.mouse_y=101
pyxel.mouse_x=42pyxel.mouse_y=100
pyxel.mouse_x=73pyxel.mouse_y=92
pyxel.mouse_x=93pyxel.mouse_y=94
pyxel.mouse_x=98pyxel.mouse_y=99
pyxel.mouse_x=97pyxel.mouse_y=106
pyxel.mouse_x=89pyxel.mouse_y=113
pyxel.mouse_x=63pyxel.mouse_y=119
pyxel.mouse_x=46pyxel.mouse_y=116
pyxel.mouse_x=39pyxel.mouse_y=110
pyxel.mouse_x=40pyxel.mouse_y=104
pyxel.mouse_x=49pyxel.mouse_y=100
pyxel.mouse_x=56pyxel.mouse_y=100
pyxel.mouse_x=66pyxel.mouse_y=108
pyxel.mouse_x=74pyxel.mouse_y=123
pyxel.mouse_x=77pyxel.mouse_y=133
pyxel.mouse_x=77pyxel.mouse_y=140
pyxel.mouse_x=75pyxel.mouse_y=145
pyxel.mouse_x=73pyxel.mouse_y=149
pyxel.mouse_x=67pyxel.mouse_y=153
pyxel.mouse_x=60pyxel.mouse_y=153
pyxel.mouse_x=51pyxel.mouse_y=150
pyxel.mouse_x=38pyxel.mouse_y=136
pyxel.mouse_x=32pyxel.mouse_y=116
pyxel.mouse_x=32pyxel.mouse_y=105
pyxel.mouse_x=37pyxel.mouse_y=92
pyxel.mouse_x=43pyxel.mouse_y=76
pyxel.mouse_x=49pyxel.mouse_y=65
pyxel.mouse_x=50pyxel.mouse_y=61
pyxel.mouse_x=52pyxel.mouse_y=57
pyxel.mouse_x=55pyxel.mouse_y=51
pyxel.mouse_x=57pyxel.mouse_y=48
pyxel.mouse_x=61pyxel.mouse_y=46
pyxel.mouse_x=81pyxel.mouse_y=45
pyxel.mouse_x=92pyxel.mouse_y=48
pyxel.mouse_x=96pyxel.mouse_y=56
pyxel.mouse_x=95pyxel.mouse_y=66
pyxel.mouse_x=92pyxel.mouse_y=78
pyxel.mouse_x=90pyxel.mouse_y=90
pyxel.mouse_x=90pyxel.mouse_y=101
pyxel.mouse_x=94pyxel.mouse_y=112
pyxel.mouse_x=100pyxel.mouse_y=118
pyxel.mouse_x=114pyxel.mouse_y=125
pyxel.mouse_x=129pyxel.mouse_y=129
pyxel.mouse_x=138pyxel.mouse_y=129
pyxel.mouse_x=146pyxel.mouse_y=129
pyxel.mouse_x=149pyxel.mouse_y=129
pyxel.mouse_x=150pyxel.mouse_y=129
pyxel.mouse_x=144pyxel.mouse_y=123
pyxel.mouse_x=128pyxel.mouse_y=104
pyxel.mouse_x=116pyxel.mouse_y=91
pyxel.mouse_x=105pyxel.mouse_y=83
pyxel.mouse_x=95pyxel.mouse_y=79
pyxel.mouse_x=88pyxel.mouse_y=76
pyxel.mouse_x=84pyxel.mouse_y=75
pyxel.mouse_x=82pyxel.mouse_y=75
pyxel.mouse_x=75pyxel.mouse_y=77
pyxel.mouse_x=64pyxel.mouse_y=93
pyxel.mouse_x=59pyxel.mouse_y=107
pyxel.mouse_x=56pyxel.mouse_y=116
pyxel.mouse_x=55pyxel.mouse_y=125
pyxel.mouse_x=61pyxel.mouse_y=131
pyxel.mouse_x=79pyxel.mouse_y=135
pyxel.mouse_x=99pyxel.mouse_y=137
pyxel.mouse_x=115pyxel.mouse_y=137
pyxel.mouse_x=129pyxel.mouse_y=141
pyxel.mouse_x=134pyxel.mouse_y=144
pyxel.mouse_x=142pyxel.mouse_y=147
pyxel.mouse_x=149pyxel.mouse_y=149
pyxel.mouse_x=157pyxel.mouse_y=148
pyxel.mouse_x=168pyxel.mouse_y=145
pyxel.mouse_x=177pyxel.mouse_y=142
pyxel.mouse_x=182pyxel.mouse_y=140
pyxel.mouse_x=185pyxel.mouse_y=139
pyxel.mouse_x=185pyxel.mouse_y=139
pyxel.mouse_x=176pyxel.mouse_y=139
pyxel.mouse_x=146pyxel.mouse_y=137
pyxel.mouse_x=125pyxel.mouse_y=133
pyxel.mouse_x=113pyxel.mouse_y=129
pyxel.mouse_x=109pyxel.mouse_y=126
pyxel.mouse_x=111pyxel.mouse_y=115
pyxel.mouse_x=118pyxel.mouse_y=98
pyxel.mouse_x=128pyxel.mouse_y=76
pyxel.mouse_x=138pyxel.mouse_y=63
pyxel.mouse_x=146pyxel.mouse_y=54
pyxel.mouse_x=153pyxel.mouse_y=49
pyxel.mouse_x=158pyxel.mouse_y=47
pyxel.mouse_x=162pyxel.mouse_y=46
pyxel.mouse_x=163pyxel.mouse_y=45
pyxel.mouse_x=163pyxel.mouse_y=45
pyxel.mouse_x=161pyxel.mouse_y=46
pyxel.mouse_x=139pyxel.mouse_y=52
pyxel.mouse_x=117pyxel.mouse_y=56
pyxel.mouse_x=113pyxel.mouse_y=57
pyxel.mouse_x=113pyxel.mouse_y=57
pyxel.mouse_x=120pyxel.mouse_y=55
pyxel.mouse_x=151pyxel.mouse_y=48
pyxel.mouse_x=158pyxel.mouse_y=47
pyxel.mouse_x=168pyxel.mouse_y=47
pyxel.mouse_x=178pyxel.mouse_y=48
pyxel.mouse_x=182pyxel.mouse_y=49
pyxel.mouse_x=184pyxel.mouse_y=49
pyxel.mouse_x=183pyxel.mouse_y=49
pyxel.mouse_x=161pyxel.mouse_y=54
pyxel.mouse_x=138pyxel.mouse_y=55
pyxel.mouse_x=121pyxel.mouse_y=57
pyxel.mouse_x=110pyxel.mouse_y=59
pyxel.mouse_x=101pyxel.mouse_y=60
pyxel.mouse_x=89pyxel.mouse_y=62
pyxel.mouse_x=77pyxel.mouse_y=65
pyxel.mouse_x=69pyxel.mouse_y=68
pyxel.mouse_x=64pyxel.mouse_y=73
pyxel.mouse_x=60pyxel.mouse_y=80
pyxel.mouse_x=58pyxel.mouse_y=88
pyxel.mouse_x=57pyxel.mouse_y=92
pyxel.mouse_x=66pyxel.mouse_y=99
pyxel.mouse_x=87pyxel.mouse_y=108
pyxel.mouse_x=100pyxel.mouse_y=113
pyxel.mouse_x=108pyxel.mouse_y=118
pyxel.mouse_x=112pyxel.mouse_y=121
pyxel.mouse_x=112pyxel.mouse_y=129
pyxel.mouse_x=109pyxel.mouse_y=143
pyxel.mouse_x=102pyxel.mouse_y=154
pyxel.mouse_x=97pyxel.mouse_y=159
pyxel.mouse_x=95pyxel.mouse_y=162
pyxel.mouse_x=94pyxel.mouse_y=162
pyxel.mouse_x=97pyxel.mouse_y=162
pyxel.mouse_x=104pyxel.mouse_y=159
pyxel.mouse_x=109pyxel.mouse_y=154
pyxel.mouse_x=115pyxel.mouse_y=144
pyxel.mouse_x=115pyxel.mouse_y=137
pyxel.mouse_x=108pyxel.mouse_y=125
pyxel.mouse_x=86pyxel.mouse_y=104
pyxel.mouse_x=69pyxel.mouse_y=93
pyxel.mouse_x=64pyxel.mouse_y=90
pyxel.mouse_x=64pyxel.mouse_y=88
pyxel.mouse_x=69pyxel.mouse_y=82
pyxel.mouse_x=87pyxel.mouse_y=70
pyxel.mouse_x=105pyxel.mouse_y=61
pyxel.mouse_x=119pyxel.mouse_y=58
pyxel.mouse_x=136pyxel.mouse_y=56
pyxel.mouse_x=156pyxel.mouse_y=54
pyxel.mouse_x=170pyxel.mouse_y=54
pyxel.mouse_x=183pyxel.mouse_y=53
pyxel.mouse_x=191pyxel.mouse_y=51
pyxel.mouse_x=200pyxel.mouse_y=49
pyxel.mouse_x=206pyxel.mouse_y=47
pyxel.mouse_x=210pyxel.mouse_y=47
pyxel.mouse_x=216pyxel.mouse_y=47
pyxel.mouse_x=223pyxel.mouse_y=49
pyxel.mouse_x=226pyxel.mouse_y=53
pyxel.mouse_x=228pyxel.mouse_y=56
pyxel.mouse_x=228pyxel.mouse_y=60
pyxel.mouse_x=228pyxel.mouse_y=63
pyxel.mouse_x=228pyxel.mouse_y=68
pyxel.mouse_x=227pyxel.mouse_y=74
pyxel.mouse_x=227pyxel.mouse_y=77
pyxel.mouse_x=226pyxel.mouse_y=78
pyxel.mouse_x=226pyxel.mouse_y=78
pyxel.mouse_x=226pyxel.mouse_y=76
pyxel.mouse_x=217pyxel.mouse_y=60
pyxel.mouse_x=212pyxel.mouse_y=52
pyxel.mouse_x=209pyxel.mouse_y=48
pyxel.mouse_x=203pyxel.mouse_y=46
pyxel.mouse_x=195pyxel.mouse_y=45
pyxel.mouse_x=185pyxel.mouse_y=46
pyxel.mouse_x=180pyxel.mouse_y=48
pyxel.mouse_x=168pyxel.mouse_y=53
pyxel.mouse_x=161pyxel.mouse_y=59
pyxel.mouse_x=161pyxel.mouse_y=61
pyxel.mouse_x=161pyxel.mouse_y=63
pyxel.mouse_x=162pyxel.mouse_y=67
pyxel.mouse_x=168pyxel.mouse_y=75
pyxel.mouse_x=172pyxel.mouse_y=81
pyxel.mouse_x=173pyxel.mouse_y=90
pyxel.mouse_x=170pyxel.mouse_y=100
pyxel.mouse_x=165pyxel.mouse_y=110
pyxel.mouse_x=154pyxel.mouse_y=120
pyxel.mouse_x=147pyxel.mouse_y=126
pyxel.mouse_x=143pyxel.mouse_y=129
pyxel.mouse_x=140pyxel.mouse_y=132
pyxel.mouse_x=138pyxel.mouse_y=135
pyxel.mouse_x=137pyxel.mouse_y=136
pyxel.mouse_x=137pyxel.mouse_y=136
pyxel.mouse_x=139pyxel.mouse_y=132
pyxel.mouse_x=146pyxel.mouse_y=127
pyxel.mouse_x=154pyxel.mouse_y=124
pyxel.mouse_x=159pyxel.mouse_y=122
pyxel.mouse_x=161pyxel.mouse_y=122
pyxel.mouse_x=161pyxel.mouse_y=127
pyxel.mouse_x=156pyxel.mouse_y=134
pyxel.mouse_x=155pyxel.mouse_y=136
pyxel.mouse_x=156pyxel.mouse_y=138
pyxel.mouse_x=167pyxel.mouse_y=138
pyxel.mouse_x=177pyxel.mouse_y=137
pyxel.mouse_x=181pyxel.mouse_y=136
pyxel.mouse_x=181pyxel.mouse_y=136
pyxel.mouse_x=181pyxel.mouse_y=136
pyxel.mouse_x=179pyxel.mouse_y=135
pyxel.mouse_x=173pyxel.mouse_y=134
pyxel.mouse_x=166pyxel.mouse_y=133
pyxel.mouse_x=154pyxel.mouse_y=130
pyxel.mouse_x=145pyxel.mouse_y=125
pyxel.mouse_x=138pyxel.mouse_y=120
pyxel.mouse_x=136pyxel.mouse_y=117
pyxel.mouse_x=136pyxel.mouse_y=113
pyxel.mouse_x=140pyxel.mouse_y=104
pyxel.mouse_x=144pyxel.mouse_y=95
pyxel.mouse_x=149pyxel.mouse_y=78
pyxel.mouse_x=151pyxel.mouse_y=64
pyxel.mouse_x=150pyxel.mouse_y=57
pyxel.mouse_x=144pyxel.mouse_y=53
pyxel.mouse_x=122pyxel.mouse_y=48
pyxel.mouse_x=99pyxel.mouse_y=48
pyxel.mouse_x=85pyxel.mouse_y=48
pyxel.mouse_x=74pyxel.mouse_y=49
pyxel.mouse_x=65pyxel.mouse_y=50
pyxel.mouse_x=55pyxel.mouse_y=50
pyxel.mouse_x=49pyxel.mouse_y=49
pyxel.mouse_x=39pyxel.mouse_y=50
pyxel.mouse_x=30pyxel.mouse_y=51
pyxel.mouse_x=26pyxel.mouse_y=51
pyxel.mouse_x=25pyxel.mouse_y=52
pyxel.mouse_x=21pyxel.mouse_y=57
pyxel.mouse_x=18pyxel.mouse_y=66
pyxel.mouse_x=18pyxel.mouse_y=74
pyxel.mouse_x=18pyxel.mouse_y=84
pyxel.mouse_x=19pyxel.mouse_y=92
pyxel.mouse_x=22pyxel.mouse_y=101
pyxel.mouse_x=23pyxel.mouse_y=106
pyxel.mouse_x=24pyxel.mouse_y=114
pyxel.mouse_x=25pyxel.mouse_y=124
pyxel.mouse_x=26pyxel.mouse_y=130
pyxel.mouse_x=30pyxel.mouse_y=134
pyxel.mouse_x=35pyxel.mouse_y=139
pyxel.mouse_x=51pyxel.mouse_y=140
pyxel.mouse_x=70pyxel.mouse_y=134
pyxel.mouse_x=78pyxel.mouse_y=127
pyxel.mouse_x=86pyxel.mouse_y=119
pyxel.mouse_x=90pyxel.mouse_y=116
pyxel.mouse_x=91pyxel.mouse_y=115
pyxel.mouse_x=91pyxel.mouse_y=114
pyxel.mouse_x=76pyxel.mouse_y=108
pyxel.mouse_x=57pyxel.mouse_y=106
pyxel.mouse_x=49pyxel.mouse_y=107
pyxel.mouse_x=47pyxel.mouse_y=107
pyxel.mouse_x=47pyxel.mouse_y=107
pyxel.mouse_x=52pyxel.mouse_y=103
pyxel.mouse_x=73pyxel.mouse_y=91
pyxel.mouse_x=93pyxel.mouse_y=86
pyxel.mouse_x=108pyxel.mouse_y=85
pyxel.mouse_x=119pyxel.mouse_y=86
pyxel.mouse_x=132pyxel.mouse_y=90
pyxel.mouse_x=138pyxel.mouse_y=93
pyxel.mouse_x=138pyxel.mouse_y=94
pyxel.mouse_x=136pyxel.mouse_y=98
pyxel.mouse_x=125pyxel.mouse_y=108
pyxel.mouse_x=114pyxel.mouse_y=116
pyxel.mouse_x=101pyxel.mouse_y=123
pyxel.mouse_x=90pyxel.mouse_y=130
pyxel.mouse_x=83pyxel.mouse_y=135
pyxel.mouse_x=80pyxel.mouse_y=139
pyxel.mouse_x=79pyxel.mouse_y=142
pyxel.mouse_x=80pyxel.mouse_y=144
pyxel.mouse_x=93pyxel.mouse_y=149
pyxel.mouse_x=101pyxel.mouse_y=151
pyxel.mouse_x=108pyxel.mouse_y=152
pyxel.mouse_x=119pyxel.mouse_y=151
pyxel.mouse_x=126pyxel.mouse_y=150
pyxel.mouse_x=133pyxel.mouse_y=149
pyxel.mouse_x=142pyxel.mouse_y=149
pyxel.mouse_x=145pyxel.mouse_y=149
pyxel.mouse_x=146pyxel.mouse_y=149
pyxel.mouse_x=146pyxel.mouse_y=149
pyxel.mouse_x=146pyxel.mouse_y=149
pyxel.mouse_x=145pyxel.mouse_y=150
pyxel.mouse_x=143pyxel.mouse_y=152
pyxel.mouse_x=143pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=142pyxel.mouse_y=152
pyxel.mouse_x=150pyxel.mouse_y=152
pyxel.mouse_x=167pyxel.mouse_y=153
pyxel.mouse_x=180pyxel.mouse_y=154
pyxel.mouse_x=191pyxel.mouse_y=153
pyxel.mouse_x=193pyxel.mouse_y=152
pyxel.mouse_x=193pyxel.mouse_y=152
pyxel.mouse_x=193pyxel.mouse_y=152
pyxel.mouse_x=193pyxel.mouse_y=152
pyxel.mouse_x=191pyxel.mouse_y=152
pyxel.mouse_x=188pyxel.mouse_y=154
pyxel.mouse_x=185pyxel.mouse_y=155
pyxel.mouse_x=184pyxel.mouse_y=155
pyxel.mouse_x=178pyxel.mouse_y=150
pyxel.mouse_x=161pyxel.mouse_y=130
pyxel.mouse_x=154pyxel.mouse_y=123
pyxel.mouse_x=153pyxel.mouse_y=121
pyxel.mouse_x=153pyxel.mouse_y=121
pyxel.mouse_x=153pyxel.mouse_y=123
pyxel.mouse_x=154pyxel.mouse_y=134
pyxel.mouse_x=151pyxel.mouse_y=157
pyxel.mouse_x=144pyxel.mouse_y=167
pyxel.mouse_x=141pyxel.mouse_y=169
pyxel.mouse_x=138pyxel.mouse_y=165
pyxel.mouse_x=136pyxel.mouse_y=153
pyxel.mouse_x=136pyxel.mouse_y=148
pyxel.mouse_x=136pyxel.mouse_y=147
pyxel.mouse_x=138pyxel.mouse_y=152
pyxel.mouse_x=140pyxel.mouse_y=159
pyxel.mouse_x=140pyxel.mouse_y=160
pyxel.mouse_x=139pyxel.mouse_y=159
pyxel.mouse_x=141pyxel.mouse_y=153
pyxel.mouse_x=144pyxel.mouse_y=147
pyxel.mouse_x=144pyxel.mouse_y=147
pyxel.mouse_x=144pyxel.mouse_y=149
pyxel.mouse_x=141pyxel.mouse_y=155
pyxel.mouse_x=138pyxel.mouse_y=158
pyxel.mouse_x=135pyxel.mouse_y=159
pyxel.mouse_x=130pyxel.mouse_y=159
pyxel.mouse_x=115pyxel.mouse_y=157
pyxel.mouse_x=89pyxel.mouse_y=154
pyxel.mouse_x=70pyxel.mouse_y=151
pyxel.mouse_x=56pyxel.mouse_y=148
pyxel.mouse_x=48pyxel.mouse_y=142
pyxel.mouse_x=45pyxel.mouse_y=138
pyxel.mouse_x=46pyxel.mouse_y=128
pyxel.mouse_x=51pyxel.mouse_y=118
pyxel.mouse_x=56pyxel.mouse_y=112
pyxel.mouse_x=66pyxel.mouse_y=107
pyxel.mouse_x=74pyxel.mouse_y=104
pyxel.mouse_x=85pyxel.mouse_y=103
pyxel.mouse_x=101pyxel.mouse_y=103
pyxel.mouse_x=115pyxel.mouse_y=103
pyxel.mouse_x=123pyxel.mouse_y=102
pyxel.mouse_x=136pyxel.mouse_y=98
pyxel.mouse_x=144pyxel.mouse_y=92
pyxel.mouse_x=147pyxel.mouse_y=85
pyxel.mouse_x=147pyxel.mouse_y=82
pyxel.mouse_x=146pyxel.mouse_y=80
pyxel.mouse_x=145pyxel.mouse_y=79
pyxel.mouse_x=145pyxel.mouse_y=79
pyxel.mouse_x=145pyxel.mouse_y=79
pyxel.mouse_x=145pyxel.mouse_y=80
pyxel.mouse_x=147pyxel.mouse_y=86
pyxel.mouse_x=147pyxel.mouse_y=92
pyxel.mouse_x=147pyxel.mouse_y=97
pyxel.mouse_x=146pyxel.mouse_y=100
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=145pyxel.mouse_y=101
pyxel.mouse_x=159pyxel.mouse_y=94
pyxel.mouse_x=201pyxel.mouse_y=73
pyxel.mouse_x=225pyxel.mouse_y=61
pyxel.mouse_x=242pyxel.mouse_y=48
pyxel.mouse_x=255pyxel.mouse_y=38
pyxel.mouse_x=258pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=259pyxel.mouse_y=37
pyxel.mouse_x=269pyxel.mouse_y=29
pyxel.mouse_x=278pyxel.mouse_y=18
pyxel.mouse_x=280pyxel.mouse_y=12
pyxel.mouse_x=281pyxel.mouse_y=10
pyxel.mouse_x=281pyxel.mouse_y=10
pyxel.mouse_x=281pyxel.mouse_y=9
pyxel.mouse_x=281pyxel.mouse_y=9
pyxel.mouse_x=281pyxel.mouse_y=8
pyxel.mouse_x=282pyxel.mouse_y=8
pyxel.mouse_x=283pyxel.mouse_y=5
pyxel.mouse_x=285pyxel.mouse_y=3
pyxel.mouse_x=285pyxel.mouse_y=1
pyxel.mouse_x=286pyxel.mouse_y=1
pyxel.mouse_x=286pyxel.mouse_y=0
pyxel.mouse_x=286pyxel.mouse_y=0
pyxel.mouse_x=286pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
pyxel.mouse_x=0pyxel.mouse_y=0
"""

    def __init__(self) -> None:
        # Rooms:
        #  - "A": start area with the GOLD KeyWall (dark yellow)
        #  - "G": goal room with the flag
        self._rooms: Dict[str, List[LevelObject]] = {"A": [], "G": []}

        # GOLD key (drawn with ASCII sprite). We'll force-attach it to ghost #0 each loop.
        self.key_gold = Key(
            x=80,
            y=120,
            w=0,
            h=0,
            room_id="A",
            color=9,  # dark yellow / gold
            key_id=KEY_GOLD,
        )

        # GOLD key wall in room A; breaks into a Door -> G when pressed by someone holding the key
        self.wall_gold = KeyWall(
            x=200,
            y=90,
            w=24,
            h=24,
            target_room="G",
            required_key=KEY_GOLD,
            wall_fill=9,  # match gold color
            wall_border=7,
            icon_col=7,
        )
        self.wall_gold.can_open = self._actor_has_key

        # Goal flag
        self.flag = Flag(x=150, y=80, w=24, h=24)
        self.flag.on_finish = self._finish

        self._rooms["A"] = [self.wall_gold]
        self._rooms["G"] = [self.flag]

        # Global pickables list; keys are drawn on the overlay so they appear above everything
        self._pickables: List[Key] = [self.key_gold]
        # convenience list to re-lock per loop if you want that behavior
        self._all_walls: List[KeyWall] = [self.wall_gold]

    # ───────────────────────── helpers: seed ghost & inventory ─────────────────────────

    @staticmethod
    def _parse_trace(text: str) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or "pyxel.mouse_x=" not in line:
                continue
            try:
                # format: "pyxel.mouse_x=86pyxel.mouse_y=96"
                left, ypart = line.split("pyxel.mouse_y=")
                x = int(left.split("pyxel.mouse_x=")[1])
                y = int(ypart)
                coords.append((x, y))
            except Exception:
                # ignore malformed lines
                pass
        # drop trailing (0,0) spam
        while coords and coords[-1] == (0, 0):
            coords.pop()
        return coords

    _GHOST_PATH: List[Tuple[int, int]] = []  # filled on first seed call

    def seed_timelines(self, tm: TimelineManager) -> None:
        """
        Called by GameplayScene (see patch below) on a fresh reset when there are no past runs.
        Seeds exactly one ghost run (ghost id 0) that follows the recorded path.
        """
        if not self._GHOST_PATH:
            self._GHOST_PATH = self._parse_trace(self._RAW_TRACE)

        tl = Timeline(tm.max_frames)
        for x, y in self._GHOST_PATH[: tm.max_frames]:
            tl.record(x, y, False, False, False, False)
        tm.past_runs = [tl]  # exactly one ghost

    def _finish(self) -> None:
        self.completed = True

    def _actor_has_key(self, actor_id: int, key_id: int) -> bool:
        for k in self._pickables:
            if k.held_by == actor_id and k.key_id == key_id:
                return True
        return False

    def _set_active_actor_on_walls(self, actor_id: int) -> None:
        for room_objs in self._rooms.values():
            for obj in room_objs:
                if isinstance(obj, KeyWall):
                    obj.set_active_actor(actor_id)

    # ─────────────────────────────── LevelBase API ───────────────────────────────

    def reset_level(self) -> None:
        self.completed = False
        # Reset static objects
        for objs in self._rooms.values():
            for obj in objs:
                obj.reset()
        # Reset pickables to their spawn (will be attached to ghost in on_loop_start)
        for k in self._pickables:
            k.reset()

    def on_loop_start(self) -> None:
        # Always re-lock the gold wall each loop if you want it locked per-loop
        for w in self._all_walls:
            w.reset()

        # Ensure the seed ghost starts *holding* the golden key each loop
        if self._GHOST_PATH:
            self.key_gold.held_by = 0  # ghost id 0
            x0, y0 = self._GHOST_PATH[0]
            dx, dy = self.key_gold.follow_offset
            self.key_gold.x = x0 + dx
            self.key_gold.y = y0 + dy
            self.key_gold.room_id = self.start_room
        else:
            # No path yet (until you paste the log) – still attach to ghost 0 at spawn
            self.key_gold.held_by = 0
            self.key_gold.room_id = self.start_room

    def set_active_actor(self, actor_id: int) -> None:
        super().set_active_actor(actor_id)
        self._set_active_actor_on_walls(actor_id)

    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        # Move any carried keys with their owner (player = -1, ghosts = 0..)
        for k in self._pickables:
            k.on_actor_frame(actor_id, x, y, room_id)

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # 1) Allow pick/steal of the golden key (only if it's currently in this room)
        if action == "press":
            active_id = getattr(self, "_active_actor_id", -999)
            for k in self._pickables:
                # If the actor already holds some pickable, drop it where they click
                # and steal the clicked one. This mirrors your “swap on pick” rule.
                if k.room_id == room_id and k.try_grab_or_steal(active_id, x, y):
                    # When grabbing a new pickable, drop any other pickable owned by this actor at click pos.
                    for other in self._pickables:
                        if other is not k and other.held_by == active_id:
                            other.held_by = None
                            other.x, other.y = x, y
                            other.room_id = room_id
                    return None

        # 2) Route to objects (walls/doors/flag)
        for obj in list(self._rooms.get(room_id, [])):
            spawned, evt = obj.handle_input(which, action, x, y)
            if spawned is not None:
                self._rooms[room_id].append(spawned)
            if evt is not None:
                return evt
        return None

    def draw_room(self, room_id: str) -> None:
        # Basic background tint per room
        pyxel.cls(1 if room_id == "A" else 12)

        for obj in self._rooms.get(room_id, []):
            obj.draw()

    def draw_room_overlay(self, room_id: str) -> None:
        # Draw keys above everything
        for k in self._pickables:
            if k.room_id == room_id:
                k.draw()
