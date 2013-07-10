#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from random import randint
import thread
from datetime import datetime
import time
import re
import subprocess

def reminder_thread(irc_con,channel):
   called = 0;
   prev_day="0"
   while 1:
      cur_day = datetime.now().strftime("%w");
      cur_time = datetime.now().strftime("%H%M");
      if cur_day != '0' and cur_day != '6':
         if ('1200' >= cur_time) and (cur_time >= '1115'):
            if called == 0:
               called=1;
               irc_con.privmsg(channel,"Looks like it is getting close to lunch time why don't you make some suggestions");
               if cur_day == '5':
                  irc_con.privmsg(channel,"It is beer with lunch Friday by the way");
         else:
            called=0;
         if cur_time == '0930':
            irc_con.privmsg(channel,"It is 9:30 is jwclark in yet?");
      if prev_day != cur_day:
         irc_con.topic(channel,re.sub("\n","",subprocess.check_output(["ddate"])));
      prev_day = cur_day;
      time.sleep(60);

class TestBot(irc.bot.SingleServerIRCBot):
    index=0;
    places = [];
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.last_nick = "";
        self.last_nick_count = 0;

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel,"Hey guys. I'm " + c.get_nickname() + ". I'm here to help you pick somewhere to go for lunch");
        thread.start_new_thread(reminder_thread,(c,self.channel));

    def on_join(self, c, e):
        nick = e.target
        name = re.sub("!.*","",e.source);
        choice = randint(0,2);
        if choice == 0:
           c.privmsg(nick, "Fancy seeing you here " + name);
        elif choice == 1:
           c.privmsg(nick, "What are you doing here " + name + "?");
        elif choice == 2:
           c.privmsg(nick, name + " is just here for the food");

    def on_part(self, c, e):
        nick = e.target
        name = re.sub("!.*","",e.source);
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



    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        nick = e.target
        if nick == self.connection.get_nickname() :
           nick = e.source.nick;
        if self.last_nick == e.source.nick:
           print("nick match");
           self.last_nick_count+=1;
           if self.last_nick_count > 4:
              c.privmsg(nick,"Hey " + e.source.nick + ", why don't you give someone else a chance to talk");
              self.last_nick_count = 0;
        else:
           print("no match " + self.last_nick + " " + e.source.nick);
           self.last_nick = e.source.nick;
           self.last_nick_count = 0;
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        elif re.match(".*time.*",e.arguments[0]):
           c.privmsg(nick, "Speaking of time, is it lunch time yet?");
        elif e.arguments[0] == e.arguments[0].upper():
           c.privmsg(nick, "Quiet down son. I can hear you just fine");
        elif re.match(".*" + self.connection.get_nickname() + ".*", e.arguments[0]):
           c.privmsg(nick, "Are you talking about me? I'm not listening to you");
        if re.match(".*yocto.*",e.arguments[0]):
           c.privmsg(nick, re.sub("yocto","yacto",e.arguments[0]));
        elif re.match(".*environment.*",e.arguments[0]):
           c.privmsg(nick, re.sub("environment","environmental",e.arguments[0]));
        if e.arguments[0] == "ls":
           for chname, chobj in self.channels.items():
              users = chobj.users()
              users.sort()
              c.privmsg(nick, "Users: " + ", ".join(users))
        if re.match("rm .*",e.arguments[0]):
           c.kick(nick,e.arguments[0].split()[1],"'cause " + e.source.nick + " told me to");

        return

    def do_command(self, e, args):
        nick = e.target
        if nick == self.connection.get_nickname() :
           nick = e.source.nick;
        c = self.connection
        cmd = args.split(" ",1);
        try:
           if cmd[0] == "stats":
              for chname, chobj in self.channels.items():
                 c.privmsg(nick, "--- Channel statistics ---")
                 c.privmsg(nick, "Channel: " + chname)
                 users = chobj.users()
                 users.sort()
                 c.privmsg(nick, "Users: " + ", ".join(users))
                 opers = chobj.opers()
                 opers.sort()
                 c.privmsg(nick, "Opers: " + ", ".join(opers))
                 voiced = chobj.voiced()
                 voiced.sort()
                 c.privmsg(nick, "Voiced: " + ", ".join(voiced))
           elif cmd[0] == "lunch":
                if len(cmd) > 1 :
                    self.places.insert(self.index, cmd[1]);
                    self.index = self.index + 1;
                    c.privmsg(nick, e.source.nick + " suggests " + cmd[1]);
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
           else:
                c.privmsg(nick, "Whatchu talkin' 'bout Willis? I ain't goin' to " + args)
        except:
            c.privmsg(nick, "Someone tried to crash me");

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: testbot <server[:port]> <channel> <nickname>"
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

    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
