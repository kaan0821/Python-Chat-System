"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
from voice_recognition import *
from voice_message import *
from numpy import *

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        
                elif my_msg[0] == 'v':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_SPEAKING
                        self.out_msg += 'Connect to ' + peer + '. Voice Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    new_poem = ''
                    for i in poem:
                        new_poem +=i
                    if (len(poem) > 0):
                        self.out_msg += new_poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                elif my_msg == 'ping blah blah':
                    self.out_msg += 'pong blah blah'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg["action"] == "connect":

                    # ----------your code here------#
                    
                    self.state = S_CHATTING
                    peer=peer_msg['from']
                    self.out_msg+="request from "
                    self.out_msg+=peer
                    self.out_msg+='\n\n-----------------------------------\n'

                    # ----------end of your code----#
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:  # my stuff going out
                if my_msg == 'voice':
                    voice_msg = recognize()
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":voice_msg}))
                elif my_msg == 'bettervoice':
                    better_rec()
                elif my_msg == 'voice_chinese':
                    voice_msg = recognize_Ch()
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":voice_msg}))
                elif my_msg == 'bettervoice_chinese':
                    better_rec_Ch()
                elif my_msg.split(':')[0] == 'speak':
                    storage = recording(int(my_msg.split(':')[1]))
                    length = my_msg.split(':')[1]+'s'
                    save_data(storage)
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":"VOICE_MESSAGE:"+length}))
                elif my_msg == 'listen':
                    data = take_data()
                    playing(data)
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":"Listened"}))
                elif my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                else: 
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                
            if len(peer_msg) > 0:    # peer's stuff, coming in
                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                #print(peer_msg)
                if peer_msg['action'] == 'disconnect':
                    self.out_msg += "everyone left, you are alone."
                    self.state = S_LOGGEDIN
                    self.peer = ''
                elif peer_msg['action']=='exchange':
                    self.out_msg +=peer_msg['message']
                elif peer_msg['action'] == 'connect':
                    self.peer = peer_msg['from']
                    message = '(' +self.peer  +' joined'+ ')'
                    self.out_msg +=message
        
        
                # ----------end of your code----#
                
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
