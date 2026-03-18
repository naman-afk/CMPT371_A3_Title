import random

Suits = ["Europium", "Iron", "Nickle", "Steel"]



class EINS:
    def __init__(self, num_players):
        self.num_players = num_players
        self.deck = self.create_deck()
        self.discard_pile = [] 
        random.shuffle(self.deck)
        #shuffle twice just in case of bad shuffling i guess :p
        random.shuffle(self.deck)
        #A arrays in a arrary for each hand
        self.hands = [[] for _ in range(num_players)]

        self.top_card = None
        self.total_turns = 0
        self.current_turn = 0

        self.direction = 1  # or -1

        self.deal_cards()
        self.top_card = self.deck.pop()

    def create_deck(self):
        deck=[]
        for i in range(2):#doing it twice as in EINS there is two of each
            for metal in Suits:
                for card_type in ['0','1','2','3','4','5','6','7','8','9'] + ["SKIP", "REVERSE", "DRAW2"]:
                    deck.append(metal+' '+card_type)
        for _ in range(4):
            deck.append('WILD CARD')
            deck.append('WILD DRAW4')
        return deck
    # Deal 7 cards to each playsrs
    def deal_cards(self):
        for _ in range(7):
            for hand in self.hands:
                hand.append(self.deck.pop())
    
    def reshuffle_discard(self):
        self.deck = self.discard_pile
        self.discard_pile = []
        times_to_shuffle= 8
        for wasting_time in times_to_shuffle:
            random.shuffle(self.deck)

    def is_valid_play(self, card):
        top_color, top_value = self.top_card.split()
        color, value = card.split()
        return 'WILD' == top_color or color == top_color or value == top_value

    def draw_card(self, player_id):
        if len(self.deck) == 0:
            return None
        card = self.deck.pop()
        self.hands[player_id].append(card)
        return card

    def play_card(self, player_id, card, chosen_suit=None):#the optiosnal parameter is for wild card
        # cheakc if card is in the user's hand
        if card not in self.hands[player_id]:
            return False, "Card not in hand"

        if not self.is_valid_play(card):
            return False, "Invalid move"

        self.hands[player_id].remove(card)
        self.top_card = card

        # Handle special cards
        value = card.split()[1]

        skip = False
        # if value == self.top_card.split()[1]:
# no need for this case, jusst put hte newly played card on top
        if value == "REVERSE":
            self.direction *= -1
        elif value == "SKIP":
            skip = True
        elif value == "DRAW2":
            next_player = (self.current_turn + self.direction) % self.num_players
            for _ in range(2):
                self.draw_card(next_player)
            skip = True
        elif value == "CARD":
            self.top_card = f"{chosen_suit} -1"#-1 so that the value cannot match
        elif value == "DRAW4":
            self.top_card = f"{chosen_suit} -1"#-1 so that the value cannot match
            next_player = (self.current_turn + self.direction) % self.num_players
            for _ in range(4):
                self.draw_card(next_player)
            skip = True

        return True, skip

    def next_turn(self, skip=False):
        if skip:#skip the next player
            step =2
        else:
            step=1
        self.total_turns+=1
        shift = step * self.direction
        self.current_turn = (self.current_turn + shift) % self.num_players

    def check_winner(self):
        for i, hand in enumerate(self.hands):
            if len(hand) == 0:
                return i
        return None