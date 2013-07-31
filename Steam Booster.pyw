'''
                    Copyright (C) 2013 Alexander B. Libby

    This SteamBooster is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/gpl.txt>.

    See project home page at: <https://github.com/linuts/SteamBooster>
'''

from tkinter import Tk, Frame, Entry, Button, Label, LabelFrame, \
  TOP, BOTTOM, LEFT, BOTH, FALSE
from re import findall as re_findall
from urllib.request import urlopen
from os import system as os_system
from threading import Thread
from subprocess import Popen
from platform import system
from time import sleep

class UpdateScript(): # <= This class wipes all changes made to the script!!!
    """
    Try to update this script using "github.com".
    NO DATA IS SENT TO THE SERVER TO DO THIS...
    """

    def __init__(self, use_branch="master"):
        """Start a new update thread."""
        self.__branch = use_branch
        if not self.__branch == None:
            Thread(target=self.__try_update).start()

    def __try_update(self):
        """Try to update this Script."""
        try:
            lanfile = []
            wanfile = []
            url = "https://raw.github.com/linuts/SteamBooster/{0}/Steam%20Booster.pyw"
            lanfile = self.__get_this_file(__file__.split('\\')[-1])
            wanfile = self.__get_web_file(url.format(self.__branch))
            if self.__needs_update(lanfile, wanfile):
                self.__do_update(wanfile)
        except Exception: # Need to fix this.
            pass

    def __get_this_file(self, file):
        """Load this script as a list of lines."""
        with open(file, 'r') as file:
            return file.readlines()

    def __get_web_file(self, url):
        """Load github SteamBoster script as a list of lines."""
        with urlopen(url.format(self.__branch)) as file:
            webfile = file.readlines()
        data = []
        for line in webfile:
                data.append(str(line, encoding="utf8"))
        return data

    def __needs_update(self, lan, wan):
        """Check if update is available on github."""
        if len(lan) == len(wan):
            data = UserData()
            for index in range(len(wan)):
                if not lan[index] == wan[index] or \
                  not data.header in lan[index]:
                    return True
            return False
        else:
            return True

    def __do_update(self, wan):
        """
        Replace this script with the new one.
        Restore the user data after.
        """
        data = UserData()
        savedata = data.read_in_users()
        with open(__file__.split('\\')[-1], 'w') as file:
            for line in wan:
                file.write(line)
        data.write_out_users(savedata)

class SteamData():
    """Reads .ACF and .VDF Steam config files."""

    def __init__(self):
        """Find Steam install path."""
        self.__steampath = "C:/Program Files (x86)/Steam" # fix for os other then windows

    def __call__(self, filepath):
        """Returns the Steam data nodes."""
        data = self.__read_in_file(self.__steampath + filepath)
        profile = self.__make_profile(data)
        return self.__make_nodes(profile, self.__purge_nondata(data))

    def __read_in_file(self, filepath):
        """Read the raw file into a list."""
        data = []
        with open(filepath, 'r') as file:
            for line in file:
                line = line.replace('\n', '')
                line = line.replace("\t\t", ' ')
                line = line.replace('\t', '')
                line = line.replace('\\','/')
                line = line.strip()
                if line in ['{', '}']:
                    data += [line]
                else:
                    line = re_findall('\"[^\"\r]*\"', line)
                    newline = []
                    for part in line:
                        newline += [part[1:-1]]
                    if len(newline) == 1:
                        data += newline
                    else:
                        data += [{newline[0]:newline[1]}]
        return data

    def __make_profile(self, data):
        """
        Makes a list of item depth from left to right.
        This is used in make_nodes to help re create the nodes.
        """
        depth = []
        level = 0
        for item in data:
            if item == '{':
                level += 1
            elif item == '}':
                level -= 1
            else:
                depth += [level]
        return depth

    def __purge_nondata(self, data):
        """
        Remove the '{' and '}' chars.
        After make_profile these are not needed and just get in the way.
        """
        cleandata = []
        for part in data:
            if part in ['{', '}']:
                continue
            else:
                cleandata += [part]
        return cleandata

    def __make_nodes(self, profile, data):
        """Turns the raw data list into nested dictionary nodes."""
        data = list(reversed(data))
        profile = list(reversed(profile))
        maxdepth = max(profile)
        holder = dict()
        newdata = dict()
        for index in range(len(data)):
            if profile[index] == maxdepth - 1 and type(data[index]) == str:
                newdata[data[index]] = dict()
                newdata[data[index]].update(holder)
                holder.clear()
            elif profile[index] == maxdepth - 1 and type(data[index]) == dict:
                newdata.update(data[index])
            elif not type(data[index]) == str:
                holder.update(data[index])
        return newdata

class UserData():
    """Reads and writes user data from this file."""

    def __init__(self):
        """Translate Steam userid to username."""
        self.__filename = __file__.split('\\')[-1]
        self.header = "#Live data do not edit!:"
        steam = SteamData()
        self.__steamusers = steam("/config/loginusers.vdf")

    def __to_string(self, users):
        """Turn user list into a string."""
        stringr = ""
        for part in users:
            stringr += "{0}/{1}|".format(part[0], part[1])
        return stringr[:-1]

    def __to_list(self, users):
        """Turn a user string into a list."""
        listr = []
        for part in users.split('|'):
            if len(part) > 0:
                listr += [part.split('/')]
        return listr

    def __encrypt_data(self, users):
        """Encrypt the data in this file."""
        return users # place holder

    def __decrypt_data(self, users):
        """Decrypt the data in this file."""
        return users # place holder

    def users_changed(self):
        """See if new users have logged into Steam."""
        userid = []
        for user in self.read_in_users():
            userid += [user[0]]
        steamid = list(self.__steamusers.keys())
        if len(userid) == len(steamid):
            allin = 0
            for user in steamid:
                if steamid == userid:
                    allin += 1
            if allin == len(steamid):
                return False
        else:
            return True

    def ids_to_names(self, userids):
        """Turn userids into user names."""
        users = []
        for userid in userids:
            users.append([self.__steamusers[userid[0]]["accountname"], userid[1]])
        return users

    def read_in_users(self):
        """Read this file to get user data."""
        with open(self.__filename, 'r') as file:
            for line in file.readlines():
                if self.header in line and not "header" in line:
                    strlist = self.__decrypt_data(line[len(self.header)+1:])
                    return self.__to_list(strlist)
            return []
    def write_out_users(self, users):
        """Save user data to this file."""
        code = ""
        with open(self.__filename, 'r') as file:
            for line in file.readlines():
                if not self.header in line or "header" in line:
                    code += line
                else:
                    code += '{0} '.format(self.header)
                    break
        with open(self.__filename, 'w') as file:
            file.write(code + self.__encrypt_data(self.__to_string(users)))

class GUISetup(Tk):
    """Create and add users for userdata"""

    def __init__(self, known_users):
        """Setup and run GUIsetup"""
        super().__init__()
        self.title("Steam Boost setup")
        note = "Leave the password box empty to skip a user."
        self.__header = Label(self, bg="lightblue", text=note)
        self.resizable(width=FALSE, height=FALSE)
        self.__new_user_frames = []
        self.__known_users = known_users
        self.__new_users = []
        self.__base_window()
        super().mainloop()

    def __base_window(self):
        """Create the GUI window frame."""
        self.__header.pack(padx=10, pady=10, side=TOP)
        steam = SteamData()
        steam_users = steam("/config/loginusers.vdf")
        for user in list(steam_users.keys()):
            self.__add_user_frame(user, steam_users[user]["accountname"])
        btn = Button(self, text="Done", bg="lightgray", command=self.__save_users)
        btn.pack(padx=10, pady=10, fill=BOTH, side=BOTTOM)

    def __add_user_frame(self, userid, username):
        """Add a New user frame."""
        oldindex = -1
        count = 0
        for old_user in self.__known_users:
            if userid == old_user[0]:
                oldindex = count
                break
            else:
                count += 1
        if oldindex == -1:
            holder = LabelFrame(self, text="{0}'s password".format(username))
            self.__new_users.append([userid, Entry(holder, width=35, show='*')])
            self.__new_users[-1][1].pack(padx=10, pady=10, side=LEFT)
            holder.pack(padx=10, pady=5)
        else:
            self.__new_users.append(self.__known_users[oldindex])

    def __save_users(self):
        """Save new user data to this file."""
        out = []
        for user in self.__new_users:
            if type(user[1]) == str:
                out.append([user[0], user[1]])
            elif len(user[1].get()) > 0:
                out.append([user[0], user[1].get()])
            else:
                out.append([user[0], "[NULL]"])
        data = UserData()
        data.write_out_users(out)
        self.quit()

class GUILogin(Tk):
    """Try to login as a Steam user."""

    def __init__(self):
        """Create users list."""
        super().__init__()
        self.users = []

    def mainloop(self):
        """
        If only one user is in the list auto login as that user.
        If more than one user is in the list show the GUI list.
        """
        self.title("Login")
        userslen = len(self.users)
        passcount = 0
        for user in self.users:
            if not user[1] == "[NULL]":
                passcount += 1
        if len(self.users) == 0:
            self.quit()
        elif len(self.users) == 1 or passcount == 1:
            self.__run_steam(0)
        else:
            self.__make_buttons()
        super().mainloop()

    def __make_buttons(self):
        """Create a button for each steam user."""
        self.users.sort()
        count = -1
        for user in self.users:
            if not user[1] == "[NULL]":
                count += 1
                button = Button(self, text=user[0],
                  command=lambda index=count: self.__run_steam(index))
                button.pack(side=LEFT)
        self.resizable(width=FALSE, height=FALSE)

    def __run_steam(self, count):
        """Select action based on OS."""

        def windows():
            """Kill Windows Steam process and restart as the selected user."""
            Popen("wmic process where name='Steam.exe' delete")
            sleep(3)
            cmd = "C:\Program Files (x86)\Steam\Steam.exe -fullscreen -login {0} {1}"
            cmd = cmd.format(self.users[count][0], self.users[count][1])
            Popen(cmd)

        def linux():
            """Kill Linux Steam process and restart as the selected user."""
            os_system("pkill steam")
            sleep(3)
            cmd = "steam -fullscreen -login {0} {1}"
            cmd = cmd.format(self.users[count][0], self.users[count][1])
            os_system(cmd)

        def apple():
            """Kill Apple Steam process and restart as the selected user."""
            pass # place holder

        def select_os():
            """Detect os and start steam"""
            if system() == "Windows":
                windows()
            elif system() == "Linux":
                linux()
            elif system() == "Apple":
                apple()
            self.quit()

        Thread(target=select_os).start()
        self.withdraw()

if __name__ == '__main__':
    UpdateScript() # <= set arg one to None to stop updates.
    data = UserData()
    if data.users_changed():
        GUISetup(data.read_in_users())
    else:
        login = GUILogin()
        login.users = data.ids_to_names(data.read_in_users())
        login.mainloop()

#The next line holds data. It's not a comment don't move the text!!!
#Live SteamBoost data do not edit!:
