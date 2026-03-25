# CMPT371_A3_Eins(One)

- Course: CMPT371 - Data Communications & Networking
- Instructor: Mirza Zaeem Baig
- Semester: Spring 2026

Team Members
| Name | Student No. | Email |
|--------|-------------|-----|
| Cheng Yang Lai| 301550876 | cyl74@sfu.ca |
| Namandeep Kaur | 301553233 | nka87@sfu.ca |



## 1. Project Overview
   ### 1.1 Description
   This project is a terminal based multiplayer card game inspired by UNO constructed by using Python sockets.
   The client handles keyboard input, renders UI, and communicates with the server using a simple JSON protocol.
   The server is in charge of turns, card rules, and the game.

   ### 1.2 Architecture
   Server:
      - Accepts player connections
      - Tracks game state
      - Validates moves
      - Broadcasts updates to all clients

   Client: 
      - Connects to server over TCP
      - Renders the game UI using Rich
      - Sends play actions
      - Deals with card/wildcard suit selection
      - Displays end-of-game messages

   UI Layer:
      - Built with Rich Layout, Panels, and Text
      - Footer shows Player's hand and wildcard suit selector
      - WIn/Lose state displayed

   ### 1.4 Limitations & Edge Cases
      - Each game starts fresh
         -Solution: Start playing the game and the game will not be fresh no more
      - Cannot handle cases where all cards are in hands and none is left within the deck/discard
         -Solution: Please play the cards and don't just keep drawing cards
      - Only 2-5 players, cannot handle more or less(no robot to play against you)
         -Solution: Take turn playing with friends if have more than 5 players
      - When one client wins/quit, the server keeps running and looks for client to connect to unless you manually close it
         -Solution: Manually close the server when you are finish playing
      
      

## 2. Demo Video

## 3. How to run
   ### 3.1 Prerequisites
   - Python version 3.10+
   - pip install -r requirements.txt

   ### 3.2 Step-by-Step Guide
   (Make sure correct you are in the correct directory)
      1. Start the server: python server.py
         Enter number of players.
      2. Start the clients: python client.py
      3. Turns and Top card displayed and will be updated after player play
      4. On your turn:
         Follow the on screen instructions:
          - ↑/↓ to highlight card to play
          - Enter to play
          - d/D to draw a card from pile
          - Q to quit
      5. Otherwise wait
      6. When player wins/loses message is shown and game exits.
      


## 4. Academic Integrity & References
UI layout and rendering, used ChatGPT. 