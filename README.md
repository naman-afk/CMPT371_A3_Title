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
   This project is a terminal based multiplayer card game inspired by UNO constructed by using Python sockets.<br>
   The client handles keyboard input, renders UI, and communicates with the server using a simple JSON protocol.<br>
   The server is in charge of turns, card rules, and the game.<br>

   ### 1.2 Architecture
   Server:<br>
      - Accepts player connections<br>
      - Tracks game state<br>
      - Validates moves<br>
      - Broadcasts updates to all clients<br>

   Client: <br>
      - Connects to server over TCP<br>
      - Renders the game UI using Rich<br>
      - Sends play actions<br>
      - Deals with card/wildcard suit selection<br>
      - Displays end-of-game messages<br>

   UI Layer:<br>
      - Built with Rich Layout, Panels, and Text<br>
      - Footer shows Player's hand and wildcard suit selector<br>
      - WIn/Lose state displayed<br>

### 1.3 Limitations
  - Each game starts fresh
     -Solution: Start playing the game and the game will not be fresh no more
  - Cannot handle cases where all cards are in hands and none is left within the deck/discard
     -Solution: Please play the cards and don't just keep drawing cards
  - Only 2-5 players, cannot handle more or less(no robot to play against you)
     -Solution: Take turn playing with friends if have more than 5 players
  - When one client wins/quit, the server keeps running and looks for client to connect to unless you manually close it
     -Solution: Manually close the server when you are finish playing  

## 2. Demo Video<br>
[Demo Video Here on Youtube](https://www.youtube.com/watch?v=2-cLr3RGzUo)<br>
## 3. How to run<br>
   ### 3.1 Prerequisites<br>
   - Python version 3.10+<br>
   - pip install -r requirements.txt<br>

   ### 3.2 Step-by-Step Guide<br>
   (Make sure correct you are in the correct directory)<br>
      1. Start the server: python server.py<br>
         Enter number of players.<br>
      2. Start the clients: python client.py<br>
         Note: the game will automatically start once all players have joined <br>
      3. Turns and Top card displayed and will be updated after player play <br>
      4. On your turn:<br>
         Follow the on screen instructions:<br>
          - ↑/↓ to highlight card to play<br>
          - Enter to play<br>
          - d/D to draw a card from pile<br>
          - Q to quit<br>
      5. Otherwise wait<br>
      6. When player wins/loses message is shown and game exits.<br>
      


## 4. Academic Integrity & References
UI layout and rendering, used ChatGPT. 
