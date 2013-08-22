#! /usr/bin/env python

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from random import randint
import thread
from datetime import datetime
import time
import re
import subprocess
import sqlite3

class player:
   def __init__(self,user,db,irc_con,channel):
      self.name = re.sub("@","",user);
      self.db = db;
#      try:
      self.weapon = db.random_weapon_type() + " " +  db.random_weapon();
#      except:
#         self.weapon = "silly thing";
      self.irc_con = irc_con;
      self.channel = channel;
      irc_con.privmsg(self.channel, self.name + " enters the room and is equipped with a " + self.weapon);
      self.hp=100;
   def get_weapon(self):
      return self.weapon;
   def get_health(self):
      return self.hp;
   def set_health(self,val):
      self.hp=val;

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



    def on_nicknameinuse(self, c, e):
        print(c.get_nickname() + " in use")

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel,"Hey guys. I'm " + c.get_nickname() + ". I'm here to help you pick somewhere to go for lunch");
        thread.start_new_thread(self.reminder_thread,(c,self.channel));

    def _on_namreply(self, c, e):
        ch = e.arguments[1]
        for nick in e.arguments[2].split():
            self.players.append(player(nick,self.db,c,self.channel));

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
           self.players.append(player(name,self.db,c,self.channel));

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
             if player.name == name:
                weapon = player.get_weapon();
          c.privmsg(nick, name + " is equipped with a " + weapon);
       if(re.match(" *health",args,re.IGNORECASE)):
          health = 0;
          for player in self.players:
             if player.name == name:
                health = player.get_health();
          c.privmsg(nick, name + " has " + str(health) + " hp");
       if(re.match(" *attack .*",args, re.IGNORECASE)):
          targets = args.split(" ");
          for player in self.players:
             if player.name == name:
                source_player = player;
          for target in targets:
             for player in self.players:
                if target == player.name:
                   damage = randint(0,10) - 3;
                   if damage >= 0:
                      health = player.get_health();
                      player.set_health(health - damage);
                      c.privmsg(self.channel,source_player.name + " attacks " + target + " with their " + source_player.get_weapon() + " for " + str(damage) + " damage");
                      c.privmsg(self.channel, target + " is now at " + str(player.get_health()) + " hp");
                   else:
                      source_player.set_health(source_player.get_health() + damage);
                      c.privmsg(self.channel, source_player.name + " accidenetally attacks themselves with " + source_player.get_weapon() + " and is now at " + str(source_player.get_health()) + " hp.");

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
                 c.privmsg(self.channel,"meh");
              elif choice == 1:
                 c.privmsg(self.channel,"nope");
              elif choice == 2:
                 c.privmsg(self.channel,"maybe latter");
              elif choice == 3:
                 c.privmsg(self.channel,"just mash the keys that might work");
              elif choice == 4:
                 c.privmsg(self.channel,"To make a specific command preface it with \"" + self.nick + ":\" or send a private message to " + self.nick);
                 c.privmsg(self.channel,"If that's not enough just look at the source on gitlab.");
           elif cmd[0] == "weapon":
              self.db.add_weapon(cmd[1]);
           elif cmd[0] == "weapon_type":
              self.db.add_weapon_type(cmd[1]);
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
