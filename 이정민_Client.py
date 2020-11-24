from socket import *
from random import randint
import random


def answerNumber(): #decide the answer
    while True:
        n1 = randint(1, 9) # Any integer between 1 and 9
        n2 = randint(1, 9)
        n3 = randint(1, 9)
      
        if n1 != n2 and n1 != n3 and n2 != n3:
            answer_list = [n1, n2, n3]
            answer = n1*100 + n2*10 + n3
            break
    print("Answer: %d" %answer)
    return answer_list

def guessNumber(guess, my_SB, data, myguess): #guess number
    if len(guess) == 3: #If the client finds three numbers corresponding to the server's answer
        if my_SB[1] == 3 : #If the number I predicted is 3 balls, swap 3 digits to the right
            tmp = myguess[0] 
            for i in range(2):
                myguess[i] = myguess[i+1]
            myguess[2] = tmp
        else : #If not 3 ball
            while True : #Randomly find three digits in the guess list, excluding the previously predicted number
                myguess = random.sample(guess, 3)
                if myguess not in data :
                    break
    elif len(data) < 3 : # If the prediction attempt is 3 or less
        myguess = [i for i in range(3*len(data)+1,3*(len(data)+1)+1)]
        #First : [1, 2, 3], second : [4, 5, 6], third : [7, 8, 9]
    else:
        c1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        c2 = [list(set(guess).intersection(i)) for i in c1] #c2 selects only values that overlap both c1 and guess.

        myguess = random.sample(c2[0], data[0][3]+data[0][4]) #Randomly select by the number of SB in [1, 2, 3].
        myguess = myguess+random.sample(c2[1], data[1][3]+data[1][4]) #Randomly select by the number of SB in [4, 5, 6].
        myguess = myguess+random.sample(c2[2], data[2][3]+data[2][4]) #Randomly select by the number of SB in [7, 8, 9].

    return myguess

def fromServerSplit(fromServer):#In messages received from server, separate by serverguess, my_SB
    fromServer_split = fromServer.split("/")
    serverguess = [int(i) for i in fromServer_split[0][1:8].split(",")] 
    my_SB = [int(i) for i in fromServer_split[1][1:5].split(",")] 
    return serverguess, my_SB

def server_StrikeAndBall(serverguess, answer_list): #The number of SBs included in the answer predicted by the server
    server_SB = [0, 0]
    for i in range(3):
        if serverguess[i] in answer_list :
            if serverguess[i] == answer_list[i]: #strike
                server_SB[0]+= 1
            else :                               #ball
                server_SB[1]+= 1
    return server_SB
    
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(('localhost', serverPort))

message = input("Do you want a number baseball game? (Yes or No) ")
if message == 'Yes' :
    toServer = "request_game"
    clientSocket.send(toServer.encode())
    print('To server:', toServer)

    fromServer = clientSocket.recv(1024).decode()
    print('From Server:', fromServer)

    #decide the answer
    answer_list = answerNumber()
    
    myguess = [1, 2, 3] #Answer of server predicted by client
    my_SB = [0, 0] #The number of strike and ball in myguess
    serverguess = [0, 0, 0] #Answer of client predicted by server
    server_SB = [0, 0] #The number of strike and ball in serverguess
    guess = [1, 2, 3, 4, 5, 6, 7, 8, 9] #The numbers that can be the server's answer.
    data = [] #[myguess + my_SB] append -> If flag = 1, [myguess] append
    flag = 0 #determine if three numbers corresponding to the server's answer were found
    
    while True :

        #guess number
        myguess = guessNumber(guess, my_SB, data, myguess)
        
        #make [_, _, _]/[_, _] form
        toServer = (str)(myguess)+"/"+(str)(server_SB) 
        clientSocket.send(toServer.encode())
        print('To server:', toServer)

        fromServer = clientSocket.recv(1024).decode()
        print('From Server:', fromServer)
        
        serverguess, my_SB = fromServerSplit(fromServer)

        #If there are no strikes or balls in any of the numbers client predict, Delete a number from guess
        if my_SB[0]+my_SB[1] == 0 :
            for i in range(3):
                 if myguess[i] in guess :
                    del guess[guess.index(myguess[i])]
            if len(guess) == 3:
                data = [] #data list initialization
                flag = 1 #Because we found three numbers that correspond to the server's answer, change flag = 1
        #If the number of strikes and balls in the numbers client predicted is 3,
        if my_SB[0]+my_SB[1] == 3 and flag == 0  :
            guess = myguess
            data = [] #data list initialization
            flag = 1 #Because we found three numbers that correspond to the server's answer, change flag = 1


        #Until the third attempt, and when flag = 0, [myguess + my_SB] append
        if len(data)<3 and flag == 0:
            data.append(myguess+my_SB)

        #[myguess] append
        if flag == 1:
            data.append(myguess)
        
        #The number of SBs included in the answer predicted by the serever
        server_SB = server_StrikeAndBall(serverguess, answer_list)

        #Game results 
        # my_SB[0] : The number of strike on the client
        # server_SB[0] : The number of strike on the server                 
        if server_SB[0] == 3 and my_SB[0] != 3: 
            print("Client Lose!")
            toServer = "[0, 0, 0]/[3, 0]"
            clientSocket.send(toServer.encode())
            print('To server:', toServer)
            break
        elif server_SB[0] == 3 and my_SB[0] == 3:
            print("Draw!") 
            toServer = (str)(myguess)+"/"+(str)(server_SB)
            clientSocket.send(toServer.encode())
            print('To server:', toServer)
            break
        elif my_SB[0] == 3: 
            print("Client Win!")
            toServer = (str)(myguess)+"/"+(str)(server_SB)
            clientSocket.send(toServer.encode())
            print('To server:', toServer)
            break
clientSocket.close()
