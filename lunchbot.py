#! /usr/bin/env python

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from random import randint
from random import choice
import thread
from threading import Timer
from datetime import datetime
import string
import time
import re
import subprocess
import sqlite3
import socket
import os
import stat

class player:
   def __init__(self,user,db,irc_con,channel, silent):
      self.name = re.sub("@","",user);
      self.db = db;
      self.weapon = db.random_weapon_type() + " " +  db.random_weapon();
      self.items = [];
      self.irc_con = irc_con;
      self.channel = channel;
      if(silent == 0):
         if (self.weapon.startswith(('a','e','i','o','u','A','E','I','O','U'))):
            self.irc_con.privmsg(self.channel, self.name + " is equipped with an " + self.weapon);
         else:
            self.irc_con.privmsg(self.channel, self.name + " is equipped with a " + self.weapon);
      self.hp=100;
      self.location_set = 0;
      self.busy=0;
      self.activity = "doing nothing";
   def get_weapon(self):
      return self.weapon;
   def get_health(self):
      return self.hp;
   def set_health(self,val):
      self.hp=val;
   def add_item(self,val):
      self.items.append(val);
   def rm_item(self,val):
      self.items.remove(val);
   def equip_item(self,val):
      self.rm_item(val);
      weapon = self.get_weapon();
      if(weapon != "Nothing"):
         self.add_item(weapon);
      self.weapon = val;



class location:
   def __init__(self,db,name,index, x, y):
      self.name = name;
      self.items = [];
      count = randint(1,5);
      for i in range(count):
         self.items.append(db.random_weapon_type() + " " + db.random_weapon());
      self.north_index = -1;
      self.south_index = -1;
      self.east_index = -1;
      self.west_index = -1;
      self.index = index;
      self.people = [];
      self.x=x;
      self.y=y;
   def connect(self,direction,name):
      if(direction == "n"):
         self.north = name;
         self.north_index = name.index;
      elif(direction == "s"):
         self.south = name;
         self.south_index = name.index;
      elif(direction == "e"):
         self.east = name;
         self.east_index = name.index;
      elif(direction == "w"):
         self.west = name;
         self.west_index = name.index;
   def add_item(self,name):
      self.items.append(name);
   def remove_item(self,name):
      for item in self.items:
         if item == name:
            self.items.remove(item);
            return;
   def add_person(self,person):
      self.people.append(person);
   def remove_person(self,person):
      self.people.remove(person);


class sqlite_db:
   def __init__(self,filename):
      self.server=sqlite3.connect(filename);
      curs = self.server.cursor();
      curs.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY AUTOINCREMENT, place TEXT, suggested INTEGER)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, spoke INTEGER)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS weapons (id INTEGER PRIMARY KEY AUTOINCREMENT, weapon TEXT)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS weapon_types (id INTEGER PRIMARY KEY AUTOINCREMENT, weapon_type TEXT)");
      self.server.commit();
      curs.execute("CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)");
      self.server.commit();
   def add_message(self,msg):
      curs = self.server.cursor();
      str_arr = [(msg)]
      curs.execute("INSERT INTO messages(message) VALUES (?)",str_arr);
      self.server.commit();
   def random_message(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM messages ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];
   def random_hashtag(self, hashtag):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM messages WHERE message LIKE ? ORDER BY RANDOM() LIMIT 1",[( "%" + hashtag + "%")]);
      return curs.fetchone();
   def add_place(self,place):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM restaurants WHERE place=?",[(place)]);
      entry = curs.fetchone();
      if entry:
         count = entry[2] + 1;
         curs.execute("UPDATE restaurants SET suggested=? WHERE id =?",[(count),(entry[0])]);
      else:
         str_arr = [(place),1];
         curs.execute("INSERT INTO restaurants(place,suggested) VALUES (?,?)",str_arr);
      self.server.commit();
   def random_place(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM restaurants ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];
   def get_places(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM restaurants");
      return curs.fetchall();
   def inc_user(self,user):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM users WHERE name=?",[(user)]);
      entry = curs.fetchone();
      if entry:
         count = entry[2] + 1;
         curs.execute("UPDATE users SET spoke=? WHERE name=?",[(count),(user)]);
      else:
         curs.execute("INSERT INTO users(name,spoke) VALUES (?,?)",[(user),(1)]);
      self.server.commit();
   def get_users(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM users");
      return curs.fetchall();
   def add_quote(self,msg):
      curs = self.server.cursor();
      str_arr = [(msg)]
      curs.execute("INSERT INTO quotes(quote) VALUES (?)",str_arr);
      self.server.commit();
   def random_quote(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];
   def add_weapon(self,msg):
      curs = self.server.cursor();
      str_arr = [(msg)]
      curs.execute("INSERT INTO weapons(weapon) VALUES (?)",str_arr);
      self.server.commit();
   def random_weapon(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM weapons ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];
   def add_weapon_type(self,msg):
      curs = self.server.cursor();
      str_arr = [(msg)]
      curs.execute("INSERT INTO weapon_types(weapon_type) VALUES (?)",str_arr);
      self.server.commit();
   def random_weapon_type(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM weapon_types ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];
   def add_room(self,room):
      curs = self.server.cursor();
      str_arr = [(room)];
      curs.execute("INSERT INTO rooms(name) VALUES (?)",str_arr);
      self.server.commit();
   def random_room(self):
      curs = self.server.cursor();
      curs.execute("SELECT * FROM rooms ORDER BY RANDOM() LIMIT 1");
      return curs.fetchone()[1];



class RemovedBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname + "1", nickname + "1")
        self.original_name = nickname;
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        print("nick name in use " + c.get_nickname());

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel,"Hey guys. I'm " + c.get_nickname() + ". I'm here to harass " + self.original_name + ".");

    def on_join(self, c, e):
        nick = e.target;
        name = re.sub("!.*","",e.source);
        if name == self.original_name:
           choice = randint(0,2);
           if choice == 0:
              c.privmsg(nick, name + " you've got a lot of nerve showing up here");
           elif choice == 1:
              c.privmsg(nick, "Go away!");
           elif choice == 2:
              c.privmsg(nick, "I hate you " + name);
    def on_part(self, c, e):
        nick = e.target;
        name = re.sub("!.*","",e.source);
        if name == self.original_name:
           choice = randint(0,2);
           if choice == 0:
              c.privmsg(self.channel, "I thought he would never leave");
           elif choice == 1:
              c.privmsg(self.channel, "Good riddence");
           elif choice == 2: 
              c.privmsg(self.channel, "And stay out!");

    def on_pubmsg(self, c, e):
       name = e.source.nick;
       if name == self.original_name:
          choice = randint(0,100);
          if(choice < 10):
             c.privmsg(self.channel, "Shut up!");
          elif(choice < 20):
             c.privmsg(self.channel, "Go Away!");
          elif(choice < 30):
             c.privmsg(self.channel, "I hate you!");
          elif (choice < 40):
             c.kick(self.channel,name, "I hate that guy");
   
class web_socket:
   def __init__(self,bot):
      self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);
      self.addr = "/tmp/" + bot.channel;
      try:
         os.unlink(self.addr);
      except:
         if os.path.exists(self.addr):
            raise
      self.sock.bind(self.addr);
      os.chmod(self.addr,stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO);
      self.bot = bot;
      thread.start_new_thread(self.accept_loop,());
   def accept_loop(self):
      self.sock.listen(1);
      while True:
         connection, addr = self.sock.accept();
         thread.start_new_thread(self.handle_connection,(connection,addr));
   def handle_connection(self,connection,addr):
      while True:
         command = connection.recv(32);
         if(command == "locations"):
            room_str = "{\n";
            max_x = 0;
            max_y = 0;
            for room in self.bot.rooms:
               if room.x > max_x:
                  max_x = room.x;
               if -room.x > max_x:
                  max_x = -room.x;
               if room.y > max_y:
                  max_y = room.y;
               if -room.y > max_y:
                  max_y = -room.y;
            room_str = room_str + "\"height\":\"" + str(max_y*2 + 1) + "\",\n";
            room_str = room_str + "\"width\":\"" + str(max_x*2 + 1) + "\",\n";
            room_str = room_str + "\"rooms\":[\n";
            first_room = 1;
            for room in self.bot.rooms:
               if first_room == 1:
                  first_room = 0;
               else:
                  room_str = room_str + ",\n";
               room_str = room_str + "{\n";
               room_str = room_str + "\"name\": \"" + room.name + "\",\n";
               room_str = room_str + "\"x\": \"" + str(room.x) + "\",\n";
               room_str = room_str + "\"y\": \"" + str(room.y) + "\",\n";

               room_str = room_str + "\"index\": \"" + str(room.index) + "\",\n";
               room_str = room_str + "\"north_index\": \"" + str(room.north_index) + "\",\n";
               room_str = room_str + "\"south_index\": \"" + str(room.south_index) + "\",\n";
               room_str = room_str + "\"east_index\": \"" + str(room.east_index) + "\",\n";
               room_str = room_str + "\"west_index\": \"" + str(room.west_index) + "\",\n";

               room_str = room_str + "\"people\": [\n";
               first_player=1;
               for player in room.people:
                  if first_player == 1:
                     first_player = 0;
                  else:
                     room_str = room_str + ",\n";
                  room_str = room_str + "\"" + player.name + "\"";
               room_str = room_str + "\n],\n";
               room_str = room_str + "\"objects\": [\n";
               first_item = 1;
               for item in room.items:
                  if first_item == 1:
                     first_item = 0;
                  else:
                     room_str = room_str + ",\n";
                  room_str = room_str + "\"" + re.sub("\"","\\\"",item) + "\"";
               room_str = room_str + "\n]\n";
               room_str = room_str + "}";
            room_str = room_str + "\n]\n}";
            connection.sendall(room_str.encode('ascii', 'ignore'));
            connection.close();
            return;


class TestBot(irc.bot.SingleServerIRCBot):
    index=0;
    places = [];
    topic = "none";
    talk_count = 0;
    def __init__(self, channel, nickname, server, database, port=6667):
        self.channel = channel
        self.server = server
        self.nick = nickname
        self.last_nick = "";
        self.last_nick_count = 0;
        self.db = sqlite_db(database);
        self.players = [];
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.rooms_init = 0;
        self.it = "";
        self.web_socket = web_socket(self);

    def init_rooms(self):
       self.rooms = [];
       room = location(self.db,"Innovation Lounge",0,0,0);
       self.rooms.append(room);
       index = 1;
       depth = 0;
       if 1 != 0:
          index =  self.add_room(room,"n",index,depth,0,1);
       if 1 != 0:
          if self.find_room(0,-1) is None:
             index =  self.add_room(room,"s",index,depth,0,-1);
       if 1 != 0:
          if self.find_room(1,0) is None:
             index =  self.add_room(room,"e",index,depth,1,0);
       if 1 != 0:
          if self.find_room(-1,0) is None:
             index =  self.add_room(room,"w",index,depth,-1,0);
    def find_room(self,x,y):
       for room in self.rooms:
          if room.x == x and room.y == y:
             return room;
       return None;

    def add_room(self, parent, parent_direction, index, depth,x,y):
      if depth == 5:
         return index;
      room_name = choice(self.players).name + "'s " + self.db.random_room();
      if randint(0,3) == 1:
         try:
            room_name = self.db.random_place();
         except:
            print("no places recorded");
      room = location(self.db,room_name,index,x,y);
      self.rooms.append(room);
      if parent_direction == "n":
         child_direction = "s";
      if parent_direction == "s":
         child_direction = "n";
      if parent_direction == "e":
         child_direction = "w";
      if parent_direction == "w":
         child_direction = "e";
      parent.connect(parent_direction,room);
      room.connect(child_direction,parent);
      index += 1;
      depth += 1;
      adjacent_room = self.find_room(x,y+1);
      if (randint(0,2) != 0 and child_direction != "n") or (adjacent_room is not None):
         if adjacent_room is None:
            index =  self.add_room(room,"n",index,depth,x,y+1);
         else:
            adjacent_room.connect("s", room);
            room.connect("n",adjacent_room);
      adjacent_room = self.find_room(x,y-1);
      if (randint(0,2) != 0 and child_direction != "s") or (adjacent_room is not None):
         if adjacent_room is None:
            index =  self.add_room(room,"s",index,depth,x,y-1);
         else:
            adjacent_room.connect("n", room);
            room.connect("s",adjacent_room);
      adjacent_room = self.find_room(x+1,y);
      if (randint(0,2) != 0 and child_direction != "e") or (adjacent_room is not None):
         if adjacent_room is None:
            index =  self.add_room(room,"e",index,depth,x+1,y);
         else:
            adjacent_room.connect("w", room);
            room.connect("e",adjacent_room);
      adjacent_room = self.find_room(x-1,y);
      if (randint(0,2) != 0 and child_direction != "w") or (adjacent_room is not None):
         if adjacent_room is None:
            index =  self.add_room(room,"w",index,depth,x-1,y);
         else:
            adjacent_room.connect("e", room);
            room.connect("w",adjacent_room);
      return index;

    def on_nicknameinuse(self, c, e):
        print(c.get_nickname() + " in use")

    def on_welcome(self, c, e):
        c.join(self.channel)
        thread.start_new_thread(self.reminder_thread,(c,self.channel));
        self.do_heal();

    def _on_namreply(self, c, e):
        ch = e.arguments[1]
        for nick in e.arguments[2].split():
            self.players.append(player(nick,self.db,c,self.channel,1));
        if self.rooms_init != 1:
           self.rooms_init = 1;
           self.init_rooms();
        for _player in self.players:
           if _player.location_set == 0:
              _player.location = self.rooms[0];
              _player.location_set = 1;
              self.rooms[0].add_person(_player);

    def on_join(self, c, e):
        nick = e.target;
        name = re.sub("!.*","",e.source);
        if name != self.nick:
           choice = randint(0,2);
           if choice == 0:
              c.privmsg(nick, "Fancy seeing you here " + name);
           elif choice == 1:
              c.privmsg(nick, "What are you doing here " + name + "?");
           elif choice == 2:
              c.privmsg(nick, name + " is just here for the food");
           _player = player(name,self.db,c,self.channel,0);
           self.players.append(_player);
           _player.location = self.rooms[0];
           _player.location_set = 1;
           self.rooms[0].add_person(_player);

    def on_nick(self,c,e):
       name = re.sub("!.*","",e.source);
       for player in self.players:
          if player.name == name:
             player.name = e.target;

    def on_part(self, c, e):
        nick = e.target;
        name = re.sub("!.*","",e.source);
        c.nick(name + "1");
        choice = randint(0,2);
        if choice == 0:
           c.privmsg(self.channel, "I don't like this place anymore.");
        elif choice == 1:
           c.privmsg(self.channel, "I hate you guys.");
        elif choice == 2:
           c.privmsg(self.channel, "You guy are so mean. I'm leaving.");
        c.nick(self.nick);
        choice = randint(0,2);
        if choice == 0:
           c.privmsg(nick, "And stay out " + name);
           c.privmsg(name, "Did I say you could leave " + nick + "?");
        elif choice == 1:
           c.privmsg(nick, "Why did " + name + " leave?");
           c.privmsg(name, "Why did you leave " + nick + "?");
        elif choice == 2:
           c.privmsg(nick, name + " just hates me.");
           c.privmsg(name, "Come back to " + nick);
        for player in self.players:
           if player.name == name:
              player.location.remove_person(player);
              self.players.remove(player);

    def on_quit(self,c,e):
       name = re.sub("!.*","",e.source);
       choice = randint(0,2);
       c.nick(name);
       if choice == 0:
          c.privmsg(self.channel, "I'm a big quitter. Quit quit quit.");
       elif choice == 1:
          c.privmsg(self.channel, "I hate you guys.");
       elif choice == 2:
          c.privmsg(self.channel, "You guy are so mean. I'm leaving.");
       c.nick(self.nick);
       for player in self.players:
          if player.name == name:
             player.location.remove_person(player);
             self.players.remove(player);

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def random_talk(self,c):
       msg = self.db.random_message();
       for chname, chobj in self.channels.items():
          users = chobj.users()
       count = len(users);
       user = users[randint(0,count-1)];
       msg = re.sub(c.get_nickname(),user,msg);
       c.privmsg(self.channel,msg);

    def on_pubmsg(self, c, e):
        nick = e.target
        command=0;
        if nick == self.connection.get_nickname() :
           nick = e.source.nick;
        if self.last_nick == e.source.nick:
           self.last_nick_count+=1;
           if self.last_nick_count > 4:
              c.privmsg(nick,"Hey " + e.source.nick + ", why don't you give someone else a chance to talk");
              self.last_nick_count = 0;
        else:
           self.last_nick = e.source.nick;
           self.last_nick_count = 0;
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
            command=1;
        if re.match("latonka:.*",e.arguments[0],re.IGNORECASE):
           quote = re.sub("(?i)latonka:","",e.arguments[0]);
           self.db.add_quote(quote);
        if e.arguments[0] == "ls":
           command = 1;
           for chname, chobj in self.channels.items():
              users = chobj.users()
              users.sort()
              c.privmsg(nick, "Users: " + ", ".join(users))
        if re.match("rm .*",e.arguments[0]):
           command = 1;
           try:
              why = e.arguments[0].split(" ",2)[2];
           except:
              why = "'cause I hate him";
           c.kick(nick,e.arguments[0].split()[1],why);
           thread.start_new_thread(self.rm_bot,(e.arguments[0].split()[1],));
           
        if re.match(".*talk to me.*",e.arguments[0],re.IGNORECASE):
           command = 1;
           self.talk_count = 5;
        if re.match(".*#.*",e.arguments[0]):
           tag = re.sub("^[^#]*","",e.arguments[0]);
           tag = re.sub(" .*","",tag);
           response = self.db.random_hashtag(tag);
           if response:
              c.privmsg(nick, response[1]);
        if re.match(">.*",e.arguments[0]):
           self.do_action(c,e,re.sub(">","",e.arguments[0]));
           command=1;
        if command == 0:
           self.db.add_message(e.arguments[0]);
           self.db.inc_user(e.source.nick);
        if self.talk_count > 0:
           self.talk_count = self.talk_count - 1;
           talk = 1;
        else:
           talk = randint(0,25);
        if talk == 1:
           self.random_talk(c);
        return

    def lunch_topic(self, irc_con):
       cur_time = datetime.now().strftime("%H%M");
       if ('1259' >= cur_time) and (cur_time >= '1115'):
          if self.index > 0:
             place_str = ", or ".join(map(str,self.places));
             irc_con.topic(self.channel,"Lunch suggestions: " + place_str + ".");
             self.topic = "lunch";

    def lunch_decision_topic(self, irc_con, place):
       cur_time = datetime.now().strftime("%H%M");
       if ('1259' >= cur_time) and (cur_time >= '1115') :
          irc_con.topic(self.channel,"Everyone went to " + place + " and they left you behind.");
          self.topic = "lunch";

    def ddate_topic(self, irc_con):
       irc_con.topic(self.channel,re.sub("\n","",subprocess.check_output(["ddate"])));

    def do_action(self, c, e, args):
       name = e.source.nick;
       nick = e.target
       if nick == self.connection.get_nickname() :
          nick = e.source.nick;
       if(re.match(" *inventory",args,re.IGNORECASE)):
          weapon = "nothing";
          for player in self.players:
             if player.name == name or string.find(args, player.name) != -1:
                print(player.name + ":" + args);
                weapon = player.get_weapon();
                items = "";
                for item in player.items:
                   if items == "":
                      items = items + " and has ";
                   else:
                      items = items + ", "
                   items = items + item;
                if string.find(args, player.name) != -1:
                   name = player.name;
                   break;
          if (weapon.startswith(('a','e','i','o','u','A','E','I','O','U'))):
             c.privmsg(nick, name + " is equipped with an " + weapon + items);
          else:
             c.privmsg(nick, name + " is equipped with a " + weapon + items);
       if(re.match(" *health",args,re.IGNORECASE)):
          health = 0;
          for player in self.players:
             if player.name == name:
                health = player.get_health();
          c.privmsg(nick, name + " has " + str(health) + " hp");
       if(re.match(" *attack.*",args, re.IGNORECASE)):
          targets = args.split(" ");
          for player in self.players:
             if player.name == name:
                source_player = player;
          for target in targets:
             for player in source_player.location.people:
                if target == player.name:
                   damage = randint(0,10) - 3;
                   if source_player.get_weapon() == "Nothing":
                      damage = damage - 5;
                   if damage >= 0:
                      health = player.get_health();
                      player.set_health(health - damage);
                      c.privmsg(self.channel,source_player.name + " attacks " + target + " with their " + source_player.get_weapon() + " for " + str(damage) + " damage");
                      c.privmsg(self.channel, target + " is now at " + str(player.get_health()) + " hp");
                   else:
                      source_player.set_health(source_player.get_health() + damage);
                      c.privmsg(self.channel, source_player.name + " accidentally attacks themselves with " + source_player.get_weapon() + " and is now at " + str(source_player.get_health()) + " hp.");
       if(re.match(" *where.*",args, re.IGNORECASE)):
          match = 0;
          msg = "were you looking for someone?";
          try:
             for player in self.players:
                if player.name == name:
                   msg = "you are in " + player.location.name;
                if(re.match(".* " + player.name + ".*", args)):
                   c.privmsg(nick, player.name + " is in " + player.location.name);
                   match = 1;
          except:
             msg = "no idea";
          if match == 0:
             c.privmsg(nick,msg);
       if(re.match(" *look.*",args, re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                location = player.location;
          try:
             name = "";
             first = 1;
             for person in location.people:
                if first == 1:
                   first = 0;
                else:
                   name = name + ",";
                name = name + " " + person.name;
             things = "";
             first = 1;
             for item in location.items:
                if first == 1:
                   first = 0;
                else:
                   things = things + ",";
                things = things + " " + item;
             c.privmsg(nick, "You are in " + location.name + " with" + name + " and the room contains" + things);
             exits = "";
             if(location.north_index != -1):
                exits = exits + "To the north is " + location.north.name + ". ";
             if(location.south_index != -1):
                exits = exits + "To the south is " + location.south.name + ". ";
             if(location.east_index != -1):
                exits = exits + "To the east is " + location.east.name + ". ";
             if(location.west_index != -1):
                exits = exits + "To the west is " + location.west.name + ". ";
             c.privmsg(nick, exits);
          except:
             c.privmsg(nick, "I have no idea where you are or who you are.");
       #
       # Things above this point should be non-action and below should be action
       #
       for player in self.players:
          if player.name == name:
             if player.busy != 0:
                c.privmsg(self.channel,player.name + " is too busy " + player.activity + " to do anything else");
                return;
       if(re.match(" *take.*",args,re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                for item in player.location.items:
                   if string.find(args,item) != -1:
                      player.add_item(item);
                      player.location.items.remove(item);
                      c.privmsg(self.channel, name + " picked up " + item);
       if(re.match(" *drop.*",args,re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                for item in player.items:
                   if string.find(args,item) != -1:
                      player.rm_item(item);
                      player.location.items.append(item);
                      c.privmsg(self.channel, name + " dropped " + item);
       if(re.match(" *equip.*",args, re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                for item in player.items:
                   if string.find(args,item) != -1:
                      player.equip_item(item);
                      c.privmsg(self.channel, name + " equipped " + item);
       if(re.match(" *steal.*",args, re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                for victim in player.location.people:
                   if(re.match(".*" + victim.name + ".*",args)):
                      item = randint(0,10);
                      stolen = "Nothing";
                      if item == 0:
                         stolen = victim.weapon;
                         victim.weapon = "Nothing";
                      elif (item-1) < len(victim.items):
                         stolen = victim.items[item-1];
                         victim.rm_item(stolen);
                         player.add_item(stolen);
                      if stolen == "Nothing":
                         c.privmsg(nick, name + " failed to steal anything from " + victim.name);
                      else:
                         c.privmsg(self.channel, name + " stole " + stolen + " from " + victim.name);
       if(re.match(" *go.*",args, re.IGNORECASE)):
          directions = args.split(" ");
          for player in self.players:
             if player.name == name:
                for direction in directions:
                   if direction == "n" or direction == "north":
                      if player.location.north_index == -1:
                         c.privmsg(nick,"There is nothing to the north");
                      else:
                         new_location = player.location.north;
                         player.location.remove_person(player);
                         player.location = new_location;
                         player.location.add_person(player);
                   if direction == "s" or direction == "south":
                      if player.location.south_index == -1:
                         c.privmsg(nick,"There is nothing to the south");
                      else:
                         new_location = player.location.south;
                         player.location.remove_person(player);
                         player.location = new_location;
                         player.location.add_person(player);
                   if direction == "e" or direction == "east":
                      if player.location.east_index == -1:
                         c.privmsg(nick,"There is nothing to the east");
                      else:
                         new_location = player.location.east;
                         player.location.remove_person(player);
                         player.location = new_location;
                         player.location.add_person(player);
                   if direction == "w" or direction == "west":
                      if player.location.west_index == -1:
                         c.privmsg(nick,"There is nothing to the west");
                      else:
                         new_location = player.location.west;
                         player.location.remove_person(player);
                         player.location = new_location;
                         player.location.add_person(player);
          try:
             c.privmsg(self.channel,"you are now in " + new_location.name);
          except:
             c.privmsg(nick,"I don't know where you were trying to go");
       if(re.match(" *tag .*",args, re.IGNORECASE)):
          if(self.it == "" or self.it == name):
             for player in self.players:
                if re.match(".*" + player.name + ".*",args):
                   self.it = player.name;
                   c.privmsg(self.channel, self.it + " is IT");
                   return;
       if(re.match(" *forge .*",args, re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                duration = randint(1,5);
                weapon = re.sub(" *forge ","",args);
                c.privmsg(self.channel, name + " is forging a " + weapon + " and it will take him " + str(duration) +  " minutes");
                player.busy = duration;
                player.activity = "forging";
                player.items.append(weapon);
       if(re.match(" *heal",args, re.IGNORECASE)):
          for player in self.players:
             if player.name == name:
                duration = randint(1,5);
                health = randint(5,20);
                c.privmsg(self.channel, name + " is healing for " + str(health) + "hp and it will take " + str(duration) + " minutes");
                health = health + player.get_health();
                player.busy = duration;
                player.activity = "healing";
                if(health > 100):
                   health = 100;
                player.set_health(health);

    def do_heal(self):
       for player in self.players:
          if player.get_health() < 100:
             player.set_health (player.get_health() + 5);
             if player.get_health() > 100:
                player.set_health(100);
       t = Timer(3600,self.do_heal);
       t.start();
                


    def do_command(self, e, args):
        nick = e.target
        if nick == self.connection.get_nickname() :
           nick = e.source.nick;
        c = self.connection
        cmd = args.split(" ",1);
        try:
           if cmd[0] == "stats":
              for chname, chobj in self.channels.items():
                 places = self.db.get_places();
                 for place in places:
                    c.privmsg(nick, place[1] + " was suggested " + str(place[2]) + " times");
                 users = self.db.get_users();
                 for user in users:
                    c.privmsg(nick, user[1] + " spoke " + str(user[2]) + " times");
           elif cmd[0] == "lunch":
                if len(cmd) > 1 :
                    self.places.insert(self.index, cmd[1]);
                    self.index = self.index + 1;
                    c.privmsg(nick, e.source.nick + " suggests " + cmd[1]);
                    self.db.add_place(cmd[1]);
                    self.lunch_topic(c);
           elif cmd[0] == "random":
              c.privmsg(nick, "You could go to " + self.db.random_place());
           elif cmd[0] == "decide":
                if self.index == 0:
                    c.privmsg(nick, "I can't decide if you don't give me any options");
                elif self.index == 1:
                    c.privmsg(nick, "It isn't a decision if there is only one choice");
                else:
                    selection = randint(0,self.index-1);
                    c.privmsg(nick, "Why don't you go to " + self.places[selection] + "?" );
           elif cmd[0] == "options":
                place_str = ", or ".join(map(str,self.places));
                place_str = "You could go to " + place_str + ".";
                if len(place_str) < 512:
                    c.privmsg(nick, place_str);
                else:
                    c.privmsg(nick, "At this point you may as well go anywhere");
           elif cmd[0] == "clear":
                del self.places[0:self.index];
                self.index=0;
                c.privmsg(nick, "Ok I'm forgetting all of your suggestions");
           elif cmd[0] == "forward":
                fwd_args = cmd[1].split(" ",1);
                if randint(0,1) == 1 :
                    c.privmsg(fwd_args[0], "I do what I want. " + nick + " was trying to get me to say " + fwd_args[1]);
                else:
                    c.privmsg(fwd_args[0],fwd_args[1]);
           elif cmd[0] == "talk":
              self.talk_count = 3;
              self.random_talk(c);
           elif cmd[0] == "latonka-talk":
              choice = randint(0,2);
              if choice == 0:
                 new_name = "latonkatron";
              elif choice == 1:
                 new_name = "latonk-o-matic";
              else:
                 new_name = "latonkadonk";
              c.nick(new_name);
              c.privmsg(self.channel,self.db.random_quote());
              c.nick(self.nick);
           elif cmd[0] == "latonkalog":
               self.db.add_quote(cmd[1]);
           elif cmd[0] == "decision":
              self.lunch_decision_topic(c, cmd[1]);
           elif cmd[0] == "help":
              choice = randint(0,4);
              if choice == 0:
                 c.privmsg(nick,"meh");
              elif choice == 1:
                 c.privmsg(nick,"nope");
              elif choice == 2:
                 c.privmsg(nick,"maybe latter");
              elif choice == 3:
                 c.privmsg(nick,"just mash the keys that might work");
              elif choice == 4:
                 c.privmsg(nick,"To make a specific command preface it with \"" + self.nick + ":\" or send a private message to " + self.nick);
                 c.privmsg(nick,"If that's not enough just look at the source on gitlab.");
           elif cmd[0] == "weapon":
              self.db.add_weapon(cmd[1]);
           elif cmd[0] == "weapon_type":
              self.db.add_weapon_type(cmd[1]);
           elif re.match(" *>.*",args):
              self.do_action(c,e,re.sub(">","",args));
           else:
                c.privmsg(nick, "Whatchu talkin' 'bout Willis? I ain't goin' to " + args)
        except:
            c.privmsg(nick, "Someone tried to crash me");
    def reminder_thread(self,irc_con,channel):
       called = 0;
       prev_day="0"
       while 1:
          cur_day = datetime.now().strftime("%w");
          cur_time = datetime.now().strftime("%H%M");
          if cur_day != '0' and cur_day != '6':
             if ('1259' >= cur_time) and (cur_time >= '1115'):
                if called == 0:
                   called=1;
                   irc_con.privmsg(channel,"Looks like it is getting close to lunch time why don't you make some suggestions");
                   if cur_day == '5':
                      irc_con.privmsg(channel,"It is beer with lunch Friday by the way");
                   if self.index > 0:
                      self.lunch_topic(irc_con);
             elif called == 1:
                if self.topic == "lunch":
                   self.ddate_topic(irc_con);
                   self.topic = "ddate";
                called=0;
             if cur_time == '0930':
                irc_con.privmsg(channel,"It is 9:30 is jwclark in yet?");
          if prev_day != cur_day:
             self.ddate_topic(irc_con);
          prev_day = cur_day;
          for player in self.players:
             if player.busy > 0:
                player.busy = player.busy - 1;
                if player.busy == 0:
                   irc_con.privmsg(channel,player.name + " is done " + player.activity);
          time.sleep(60);
    def rm_bot(self,nick):
       bot = RemovedBot(self.channel, nick, self.server);
       bot.start();




def main():
    import sys
    if len(sys.argv) != 5:
        print "Usage: testbot <server[:port]> <channel> <nickname> <database>"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]
    database = sys.argv[4]

    bot = TestBot(channel, nickname, server, database, port)
    bot.start()

if __name__ == "__main__":
    main()
