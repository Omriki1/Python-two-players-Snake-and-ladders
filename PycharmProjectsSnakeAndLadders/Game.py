""""snakes and ladders game by omri cushmaru"""

import tkinter as tk
from PIL import ImageTk, Image
import random as rand
import socket
import threading


def on_special(player_num):
    """"determine if the player has landed on a snake or a ladder"""
    ladder = {2: 23, 6: 45, 20: 59, 52: 72, 57: 96, 71: 92}
    snakes = {98: 40, 87: 49, 84: 58, 73: 15, 56: 8, 50: 5, 43: 17}
    if player_num in ladder:
        player_num = ladder[player_num]
        return player_num
    elif player_num in snakes:
        player_num = snakes[player_num]
        return player_num
    return player_num


def send_data(placement, sender, r):
    """"send the position of the player to the other player to move it """
    global ip, port, turn
    if sender == 0:
        data = f"1/{placement}/{r}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(data.encode())
        s.close()
    if sender == 1:
        data = f"0/{placement}/{r}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(data.encode())
        s.close()
    if turn == 0:
        turn = 1
    elif turn == 1:
        turn = 0


def move_player(turn, r):
    """"move thr player according to their position"""
    global player1, player2, player_pos_1, player_pos_2, index, won
    if turn == 0:
        if player_pos_1 >= 100:
            won = 1
            player1.place(x=15, y=20)
            player_pos_1 = 100
        else:
            player_pos_1 = on_special(player_pos_1)
            pos = index[player_pos_1]
            pos_x = pos[0]
            pos_y = pos[1]
            player1.place(x=pos_x, y=pos_y)
        threading.Thread(target=send_data(player_pos_1, 0, r)).start()
    if turn == 1:
        if player_pos_2 >= 100:
            won = 2
            player2.place(x=15, y=20)
            player_pos_2 = 100
        else:
            player_pos_2 = on_special(player_pos_2)
            pos = index[player_pos_2]
            pos_x = pos[0]
            pos_y = pos[1]
            player2.place(x=pos_x, y=pos_y)
        threading.Thread(target=send_data(player_pos_2, 1, r)).start()


def close_game():
    """"close the game and shutdown the code"""
    global root
    root.destroy()
    exit()


def roll(turn):
    """"generate a random number and add it the players position according to witch turn is it """
    global player_pos_1, player_pos_2, RollButton
    r = rand.randint(1, 6)
    roll_label = tk.Label(root, text=f"Dice result is {r}", font=("papyrus", 18, "bold"), )
    roll_label.place(x=975, y=200)
    if turn == 0:
        player_pos_1 = player_pos_1 + r
        move_player(turn, r)
    if turn == 1:
        player_pos_2 = player_pos_2 + r
        move_player(turn, r)


def get_data():
    """"get data from the other player and move the pieces"""
    global ip, port, turn, root, first, won
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    while True:
        client_socket, address = s.accept()
        data = client_socket.recv(1024).decode()
        client_socket.close()
        break

    s.close()
    split_data = data.split("/")
    position = index[int(split_data[1])]
    if int(split_data[1]) == 100 and turn == 0:
        won = 1
    if int(split_data[1]) == 100 and turn == 1:
        won = 2
    x_pos = position[0]
    y_pos = position[1]
    if int(split_data[0]) == 1:
        player1.place(x=x_pos, y=y_pos)
    elif int(split_data[0]) == 0:
        player2.place(x=x_pos, y=y_pos)

    if turn == 0:
        turn = 1
    elif turn == 1:
        turn = 0
    first = True
    roll_label = tk.Label(root, text=f"Dice result is {split_data[2]}", font=("papyrus", 18, "bold"), )
    roll_label.place(x=975, y=200)


def host_game():
    """"crate a server to connect the two player first time"""
    global root, host_button, connect_button, Wait, SubButton, entry, sub_lab, server_socket, ip, port
    data = entry.get()
    data = data.split("/")
    data_tup = ("", "")
    try:
        data_tup = (data[0], data[1])
    except:
        print("Try again")
    if data_tup[1] and data_tup[0] != "":
        host_detail_lab = tk.Label(Wait, text="Hosting for : " + data_tup[0] + " port:  " + data_tup[1])
        host_detail_lab.pack()
        connect_button.destroy()
        SubButton.destroy()
        entry.destroy()
        sub_lab.destroy()

        ip = data_tup[0]
        port = int(data_tup[1])
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(1)
        threading.Thread(target=server_loop).start()  # start the server loop in a new thread


def server_loop():
    """"initial  start for the server side"""
    global root, Wait, show_options_menu_exit, server_socket, player_number
    while True:
        client_socket, address = server_socket.accept()
        Wait.state(newstate='iconic')
        show_options_menu_exit.destroy()
        data = client_socket.recv(1024).decode()
        client_socket.close()
        break
    player_number = 0
    show_options_menu_exit.destroy()
    server_socket.close()
    main_game()  #


def try_connect():
    """"initial connection starts the game"""
    global entry, connect_win, host_button, connect_button, show_options_menu_exit, turn, host_button, \
        connect_button, player_number, show_options_menu_exit, ip, port
    data = entry.get()
    data = data.split("/")
    data_tup = ("", "")
    try:
        data_tup = (data[0], data[1])
    except:
        print("Try again")
    if data_tup[1] and data_tup[0] != "":
        host_detail_lab = tk.Label(connect_win, text="Connecting to : " + data_tup[0] + " port:  " + data_tup[1])
        host_detail_lab.pack()

        ip = data_tup[0]
        port = int(data_tup[1])
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        client_socket.send("START".encode())
        client_socket.close()
        player_number = 1
        host_button.destroy()
        connect_button.destroy()
        show_options_menu_exit.destroy()
        main_game()


def get_index():
    """"crate  the x and y pos for each square"""
    global index
    num = [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 80, 79, 78, 77, 76, 75, 74,
           73, 72, 71, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 41, 42, 43, 44,
           45, 46, 47, 48, 49, 50, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 20,
           19, 18, 17, 16, 15, 14, 13, 12, 11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    row = 20
    i = 0
    for x in range(1, 11):
        col = 15
        for y in range(1, 11):
            index[num[i]] = (col, row)
            col = col + 60
            i = i + 1
        row = row + 60


def host_server_menu():
    """"main menu to host a game"""
    global root, host_button, connect_button, Wait, SubButton, entry, sub_lab, main_menu_exit
    root.state(newstate='iconic')
    host_button.destroy()
    connect_button.destroy()

    Wait = tk.Toplevel()
    Wait.geometry("400x200")
    Wait.resizable(width=False, height=False)
    wait_label = tk.Label(Wait, text=" Waiting for connection...")
    wait_label.pack()

    entry = tk.Entry(Wait)
    entry.place(x=140, y=70)
    SubButton = tk.Button(Wait, text="Submit", command=host_game)
    SubButton.place(x=170, y=90)
    sub_lab = tk.Label(Wait, text="Enter ip and port example: 127.0.0.1/1234")
    sub_lab.pack()

    main_menu_exit = tk.Button(Wait, text='Exit', height=1, width=7, fg="red", bg="white", font=("Ariel", 7, "bold"),
                               activebackground="Red", command=close_game)  # exit button
    # here will go all the rules of the game
    main_menu_exit.place(x=167, y=120)


def connect_to_host():
    """"main menu for connecting to host"""
    global root, host_button, connect_button, show_options_menu_exit, connect_win, entry
    root.state(newstate='iconic')
    connect_win = tk.Toplevel()
    connect_win.geometry("400x200")
    connect_win.resizable(width=False, height=False)
    connect_label = tk.Label(connect_win, text="Enter an ip and port to connect to\n Example 127.0.0.1/1234")
    connect_label.pack()

    entry = tk.Entry(connect_win)
    entry.place(x=140, y=70)
    enter_button = tk.Button(connect_win, text="Submit", command=try_connect)
    enter_button.place(x=170, y=90)

    main_menu_exit = tk.Button(connect_win, text='Exit', height=1, width=7, fg="red", bg="white",
                               font=("Ariel", 7, "bold"),
                               activebackground="Red", command=close_game)  # exit button
    # here will go all the rules of the game
    main_menu_exit.place(x=167, y=120)


def show_options(root):
    """"show the main options when you start the game"""
    global host_button, connect_button, show_options_menu_exit
    host_button = tk.Button(root, text='HostGame', height=1, width=10, fg="red", bg="white", font=("Ariel", 14, "bold"),
                            activebackground="Red", command=host_server_menu)  # host game button
    host_button.place(x=600, y=50)

    connect_button = tk.Button(root, text='Connect', height=1, width=10, fg="red", bg="white",
                               font=("Ariel", 14, "bold"),
                               activebackground="Red", command=connect_to_host)  # connect game button
    connect_button.place(x=800, y=50)

    show_options_menu_exit = tk.Button(root, text='Exit', height=1, width=10, fg="red", bg="white",
                                       font=("Ariel", 14, "bold"),
                                       activebackground="Red", command=root.destroy)  # exit button
    show_options_menu_exit.place(x=1400, y=0)

    btn = tk.Button(root, text="Help Menu", height=3, width=15, fg="yellow", bg="blue", font=("Ariel", 14, "bold"),
                    activebackground="Red", command=open_window)
    btn.place(x=100, y=10)


def open_window():
    """"open a help window where the rules are shown"""
    global root, img2
    new_window = tk.Toplevel(root)
    new_window.title("Help window")
    new_window.geometry("1800x1200")
    f2 = tk.Frame(new_window, width=1800, height=1200, relief='raised')
    f2.place(x=0, y=0)
    img2 = ImageTk.PhotoImage(Image.open("images/Black.jpg"))
    lab = tk.Label(f2, image=img2)
    lab.place(x=0, y=0)
    b_exit = tk.Button(new_window, text='Exit', height=1, width=10, fg="red", bg="white", font=("Ariel", 14, "bold"),
                       activebackground="Red", command=new_window.destroy)  # exit button

    b_exit.place(x=1400, y=0)

    rules_label = tk.Label(new_window, text="this is the rule of the game:\n two players take turns and roll a dice "
                                            "to be the first to square number 100 \n "
                                            "in the way you see ladders that you will climb to get you further up or "
                                            "snakes that take you down\n "
                                            "if you don't see your token player don't worry it under you opponent "
                                            "token\n "
                                            "use the host button to host a game using ip and port then tell it to "
                                            "your friend so they can join!\n "
                                            "when you press the dice button it will move you "
                                            "and the disappear! don't worry  it will come back when the other player "
                                            "will do his turn \n"
                                            "finally and most important have fun!!!\n"
                                            "made by omri cushmaru 2023 for a school project"
                                            "", bg='white', fg="black",
                           font=('comic sans', 14))
    rules_label.place(x=250, y=320)


def main_game():
    """"the main loop of the game where it calls all the other function to make the gae happened """
    global player_number, root, index, turn, ip, port, player1, player2, index, im, first, RollButton
    turn = 0
    draw_game_board()
    first = True
    while True:
        if won != 0:
            RollButton.destroy()
            break
        if turn == player_number:
            var = tk.IntVar()
            RollButton = tk.Button(root, image=im, height=80, width=80, command=lambda: var.set(1), bg="cyan")
            RollButton.place(x=1100, y=300)
            RollButton.wait_variable(var)
            roll(turn)
            RollButton.destroy()
        else:
            if first:
                threading.Thread(target=get_data).start()
                first = False
        root.update()
    if int(won) - 1 == int(player_number):
        win_label = tk.Label(root, text="YOU WIN!!!", bg="blue", font=("comic sans", 26, "bold"))
        win_label.place(x=615, y=320)
    else:
        lose_label = tk.Label(root, text="YOU LOSE!!!", bg="red", font=("comic sans", 26, "bold"))
        lose_label.place(x=615, y=320)


def draw_game_board():
    """"draw the game board and the players tokens"""
    global host_button, connect_button, show_options_menu_exit, root, img1, im, player2, player1
    f1 = tk.Frame(root, width=612, height=612, relief='raised')
    f1.place(x=0, y=0)
    # Set Board

    img1 = ImageTk.PhotoImage(Image.open("images/Snake.jpg"))
    lab = tk.Label(f1, image=img1)
    lab.place(x=0, y=0)

    player1 = tk.Canvas(root, width=30, height=30)
    player1.create_oval(10, 10, 30, 30, fill='blue')
    player1.place(x=0, y=650)

    # player 2 Token
    player2 = tk.Canvas(root, width=30, height=30)
    player2.create_oval(10, 10, 30, 30, fill='red')
    player2.place(x=50, y=650)

    b_exit = tk.Button(root, text='Exit', height=3, width=20, fg="yellow", bg="black", font=("Ariel", 14, "bold"),
                       activebackground="Red", command=root.destroy)  # exit button
    b_exit.place(x=950, y=10)

    # dice
    im = Image.open("images/Dice.jpg")
    im = im.resize((60, 60))
    im = ImageTk.PhotoImage(im)


global host_button, connect_button, show_options_menu_exit
player_pos_1 = 0
player_pos_2 = 0
won = 0
index = {}
get_index()

root = tk.Tk()
root.geometry('1800x1200')
root.title("Snake and Ladders")
show_options(root)
root.mainloop()
