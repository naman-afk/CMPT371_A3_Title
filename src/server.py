import socket
import threading
import json
from Eins import EINS

HOST = '127.0.0.1'
PORT = 12345

matchmaking_queue = []
queue_lock = threading.Lock()  # Protect the queue across threads


def sendmsg(conn, obj):
    try:
        message = json.dumps(obj)
        conn.sendall((message + "\n").encode())
    except OSError:
        pass

# Send a messgage to all players
def broadcast(players, obj):
    for player in players:
        sendmsg(player, obj)



#NAMAN!!!!!!!!!!! things to note:
# WEEEEEEEEEEEEEWOOOOOOOOOOOOOOOOOOOOOOWEEEEEEEEEEEEEEEEWWWWWWWWWWWOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOoo
#Card Formatting
    #cards are in a string format and it will be the suit followed by a space so you can parse it, then followed by the card value
        #Letter are all capitalized
            #e.g STEEL REVERSE or NICKLE 7
#Types of message to handle when recieving the mesage
    #Start: This JSON will inclide the player_id, cards (the player's cards in hand), top_card (the card on the top)
        # {"type":"Start", "player_id": int, "cards": array of string, "top_card": string, "current_turn":int)

    #Your_Turn: This will include the turn (turn number), cards. This msg will also be the one where you need to send a msg afterward
        # {"type": "Your_Turn", "turn":  int} 

    #Other_Turn: This will include the turn, player_turn( shows which player's turn is it). This will only be send to player that is not their turn (no reply needed)
        # {"type": "Other_Turn", "player_turn": int}

    #INVALID: this is the error emssage for the played card. Need to replay the card. 
        #{"type": "INVALID", "reason":  str}

    #Card_Draw: This will tell you what card the player drew and the updated hand
        #{"type": "Card_drawn", "card":  str}  

    #Update: This will be the update to all player on what the player did. If player drew card, the msg send will not include card
        #{"type":   "Update", "event":  "Play", "player": int, "card": str} 
        #{"type":"Update", "event":  "Draw", "player": int} 

    #DISCONNECT: One of the player disconnect --> game end cuase I don't want to deal with handling it
        #{"type": "DISCONNECT", "message": str} 

    #Winner: This will include winner and the total turn
        #{"type":   "Winner","player": int,"turns":  int}

    #State: Update everyone on the board state
        # if the top_card was a "WILD CARD" or a "WILD DRAW4", it will be represented as "<Suit> CARD" or "<Suit> DRAW4"
            #e.g IRON CARD or EUROPIUM DRAW4
        # {"type":"State","your_hand": arr of string, "top_card":str, "current_turn":  int, "turn":int}    
             
#Types of message to send, while this is technically up to you, this is how I am handling the message and expect the JSON
    #Play: This is the JSON that will include the carded played by the player and suit declared if it a wilded card
        #{"type": "Play","card":  str,"suits": str | null}  

    #Draw: This is the JSON that will tell the server you are drawing a card. Need listen for the card drawn after ward
        #{"type": "Draw"}


#NOTE:THINGS TO HANDLE
    #No more card in discard pile or draw pile: what do here?


def game_session(players):
    num_players = len(players)
    game = EINS(num_players)# start the game 
    print(f"[GAME] Starting EINS with {num_players} players")

    # send each player their id and opening hand
    for i, conn in enumerate(players):
        sendmsg(conn, {"type":"Start", "player_id": i, "cards": game.hands[i], "top_card":game.top_card, "current_turn": game.current_turn})

    while True:
            try:
                current = game.current_turn
                conn = players[current]

                # notify current player that it is their turn!
                sendmsg(conn, {"type": "Your_Turn", "turn": game.total_turns})

                # notify others that it is current player turn
                others = [p for i, p in enumerate(players) if i != current]
                broadcast(others, {"type": "Other_Turn", "player_turn": current})

                # Rec msg from client 1024 is enough right... (O.o)
                data = conn.recv(1024).decode().strip()
                if not data:
                    raise ConnectionResetError

                msg = json.loads(data)
                print(f"[TURN {game.total_turns}] Player {current}: {msg}")
                #
                # player played a card
                if msg["type"] == "Play":
                    card = msg["card"]
                    chosen_suit = msg["suits"]

                    valid, result = game.play_card(current, card, chosen_suit)

                    if not valid:
                        sendmsg(conn, {"type": "INVALID","reason": result})
                        continue  #same player retries their turn since they FAILED TO FOLLOW INSTRUCTION >:(
                    skip = result #Naman, This is for the next turn thingy, no need to worry about it... unless it don't work

                    #Broadcast card played to all (Note, the game state will be provide later look down (._.)
                        #card is a string
                    broadcast(players, {"type": "Update","event": "Play","player": current,"card": card})

                    # Check for winner
                    winner = game.check_winner()
                    if winner is not None:#ThErE iS a WiNnEr?!?!.... in the game that last forever?!?!?!?!!!
                        broadcast(players, {"type": "Winner","player": winner,"turns": game.total_turns})
                        break

                    game.next_turn(skip)

                # player draw card
                elif msg["type"] == "Draw":
                    card = game.draw_card(current)

                    sendmsg(conn, {"type": "Card_Draw","card": card})

                    broadcast(players, {"type": "Update","event": "Draw","player": current})

                    game.next_turn()
                #iNvalid action
                else:
                    sendmsg(conn, {"type": "INVALID","reason": "Unknown command"})
                    continue

                
                #Translate the topcard if needed(wild)
                topCardSuit=game.top_card.split()[1]
                if(topCardSuit==-1):
                    top_Card=game.top_card.split()[0]+" CARD"
                elif topCardSuit==-2:
                    top_Card=game.top_card.split()[0]+" DRAW4"
                else:
                    top_Card=game.top_card
                # Update all player on the game state
                for i, p in enumerate(players):
                    sendmsg(p, {
                        "type": "State",
                        "your_hand": game.hands[i],
                        "top_card": top_Card,
                        "current_turn": game.current_turn,
                        "turn": game.total_turns
                    })

            except (ConnectionResetError, OSError, json.JSONDecodeError):
                print(f"[ERROR] Player {current} disconnected")
                #HOW DARE THEY LEAVE THE GAME OF EINS!!! UNACCEPTABLE >:(|
                broadcast(players, {"type": "DISCONNECT", "message": f"Player {current} disconnected: game over"})
                break

    # Cleanup connections
    for p in players:
        try:
            p.close()
        except OSError:
            pass


def start_server():
    #get number of playsers
    while True:
        try:
            num_players = int(input("Players per game (2-5): "))
        except ValueError:
            print("Invalid input. Please enter a number, not letters.")
            continue 
        if num_players > 5 or num_players < 2:
            print("Please insert a value within the range 2-5")
        else:
            break
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTING] Server on {HOST}:{PORT}, waiting for {num_players} players per game")

    try:
        while True:
            conn, addr = server.accept()
            print(f"[CONNECT] {addr}")

            data = conn.recv(1024).decode().strip()
            if "CONNECT" not in data:
                conn.close()
                continue

            with queue_lock:
                matchmaking_queue.append(conn)
                print(f"[QUEUE] {len(matchmaking_queue)}/{num_players}")

                if len(matchmaking_queue) >= num_players:#enuf players then start the game
                    players = [matchmaking_queue.pop(0) for _ in range(num_players)]
                    threading.Thread(
                        target=game_session,
                        args=(players,),
                        daemon=True
                    ).start()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN]")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()