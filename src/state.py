# state container
class GState:
    def __init__(self):
        self.pid=None #player id
        self.hand=[] #player  cards in hand
        self.top=None # top card rn
        self.cur=None #whose turn rn
        self.turn=0
        self.my_turn=False
        self.num_players=None #size
        self.selected = 0
        self.pending_announcement=None