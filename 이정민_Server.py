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

def fromClientSplit(fromClient): #In messages received from client, separate by clientguess, my_SB
      fromClient_split = fromClient.split("/")
      clientguess = [int(i) for i in fromClient_split[0][1:8].split(",")]
      my_SB = [int(i) for i in fromClient_split[1][1:5].split(",")] 
      return clientguess, my_SB

def guessNumber(guess, my_SB, data, myguess): #guess number
      if len(guess) == 3: #If the server finds three numbers corresponding to the client's answer
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

def client_StrikeAndBall(clientguess, answer_list): #The number of SBs included in the answer predicted by the client
    client_SB = [0, 0]
    for i in range(3):
        if clientguess[i] in answer_list :
            if clientguess[i] == answer_list[i]: #strike
                client_SB[0]+= 1
            else :                               #ball
                client_SB[1]+= 1
    return client_SB

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))

serverSocket.listen(1)
print("The server is ready to receive a game request.")


connectionSocket, addr = serverSocket.accept()

fromClient = connectionSocket.recv(1024).decode()
if fromClient == "request_game" :
      print("From Client:", fromClient)
      toClient = "ok"
      connectionSocket.send(toClient.encode())
      print("To Client:", toClient)

      #decide the answer
      answer_list = answerNumber()
      
      #initialization
      myguess = [1, 2, 3] #Answer of client predicted by server
      my_SB = [0, 0] #The number of strike and ball in myguess
      clientguess = [0, 0, 0] #Answer of server predicted by client
      client_SB = [0, 0] #The number of strike and ball in clientguess
      guess = [1, 2, 3, 4, 5, 6, 7, 8, 9]  #The numbers that can be the client's answer.
      data = [] #[myguess + my_SB] append -> If flag = 1, [myguess] append
      flag = -1 #Pass the first order of the server and determine if three numbers corresponding to the client's answer were found
      
      while True:
            fromClient = connectionSocket.recv(1024).decode()
            print("From Client:", fromClient)
      
            clientguess, my_SB = fromClientSplit(fromClient)

            #Game results 
            # my_SB[0] : The number of strike on the server
            # client_SB[0] : The number of strike on the client
            if my_SB[0] == 3 and client_SB[0] != 3 : 
                  print("Server Win!")
                  break
            elif client_SB[0] == 3 and my_SB[0] == 3: 
                  print("Draw!")
                  break
            elif client_SB[0] == 3 and my_SB[0] != 3 :
                  print("Server Lose!")
                  break

            #If there are no strikes or balls in any of the numbers server predict, Delete a number from guess
            if my_SB[0]+my_SB[1] == 0 and flag == 0:
                  for i in range(3):
                       if myguess[i] in guess :
                          del guess[guess.index(myguess[i])]
                  if len(guess) == 3:
                      data = [] #data list initialization
                      flag = 1 #Because we found three numbers that correspond to the server's answer, change flag = 1
            #If the number of strikes and balls in the numbers server predicted is 3,
            elif my_SB[0]+my_SB[1] == 3 and flag == 0 : 
                  guess = myguess
                  data = [] #data list initialization
                  flag = 1 #Because we found three numbers that correspond to the client's answer, change flag = 1

            #Until the third attempt, and when flag = 0, [myguess + my_SB] append
            if len(data)<3 and flag == 0:
                  data.append(myguess+my_SB)

            #[myguess] append
            if flag == 1 :
                  data.append(myguess)
            
            #The number of SBs included in the answer predicted by the client
            client_SB = client_StrikeAndBall(clientguess, answer_list)  

            #guess number
            myguess = guessNumber(guess, my_SB, data, myguess)
            
            #make [_, _, _]/[_, _] form
            toClient = (str)(myguess)+"/"+(str)(client_SB)
            connectionSocket.send(toClient.encode())
            print("To Client:", toClient)

            if flag == -1 : #First invalid
                  flag = 0
            
connectionSocket.close()
