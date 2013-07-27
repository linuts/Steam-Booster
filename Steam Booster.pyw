"""
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

    To update SteamBoost See <https://github.com/linuts/SteamBooster>
"""

from tkinter import *
from re import findall as re_findall
from os import system as os_system
from subprocess import Popen
from platform import system
from time import sleep

class SteamDataReader():
    '''Reads ACF and VDF Steam config files.'''

    def __init__(self):
        ''''''
        self.__steampath = "C:/Program Files (x86)/Steam" # fix for other os types

    def __read_in_file(self, filepath):
        ''''''
        data = []
        with open(filepath, 'r') as file:
            for line in file:
                line = line.replace('\n', '')
                line = line.replace("\t\t", ' ')
                line = line.replace('\t', '')
                line = line.replace('\\','/') # to fix windows file locations
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
        ''''''
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
        ''''''
        cleandata = []
        for part in data:
            if part in ['{', '}']:
                continue
            else:
                cleandata += [part]
        return cleandata

    def __make_nodes(self, profile, data):
        ''''''
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

    def __base_call(self, filepath):
        ''''''
        data = self.__read_in_file(filepath)
        profile = self.__make_profile(data)
        return self.__make_nodes(profile, self.__purge_nondata(data))

    @property
    def user_nodes(self):
        ''''''
        return self.__base_call(self.__steampath + "/config/loginusers.vdf")

    @property
    def game_nodes(self):
        ''''''
        pass
        #for game in games add to base call
        #self.__base_call("")

class UserData():
    ''''''

    def __init__(self):
        ''''''
        self.__filename = __file__.split('\\')[-1]
        self.__header = "#Live SteamBoost data do not edit!:"
        steam = SteamDataReader()
        self.__steamusers = steam.user_nodes

    def __to_string(self, users):
        ''''''
        stringr = ""
        for part in users:
            stringr += "{0}/{1}|".format(part[0], part[1])
        return stringr[:-1]

    def __to_list(self, users):
        ''''''
        listr = []
        for part in users.split('|'):
            if len(part) > 0:
                listr += [part.split('/')]
        return listr

    def ids_to_names(self, userids):
        ''''''
        users = []
        for userid in userids:
            users.append([self.__steamusers[userid[0]]["accountname"], userid[1]])
        return users

    def __encrypt_data(self, users):
        ''''''
        return users # place holder

    def __decrypt_data(self, users):
        ''''''
        return users # place holder

    def read_in_users(self):
        ''''''
        with open(self.__filename, 'r') as file:
            for line in file.readlines():
                if self.__header in line and not "header" in line:
                    strlist = self.__decrypt_data(line[len(self.__header)+1:])
                    return self.__to_list(strlist)

    def users_changed(self):
        ''''''
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

    def write_out_users(self, users):
        ''''''
        code = ""
        with open(self.__filename, 'r') as file:
            for line in file.readlines():
                if not self.__header in line or "header" in line:
                    code += line
                else:
                    code += '{0} '.format(self.__header)
                    break
        with open(self.__filename, 'w') as file:
            file.write(code + self.__encrypt_data(self.__to_string(users)))

class GUISetup(Tk):
    ''''''

    def __init__(self, known_users):
        ''''''
        super().__init__()
        self.title("SteamBoost user setup")
        note = "Leave the password box empty to skip a user."
        self.__header = Label(self, bg="lightblue", text=note)
        self.resizable(width=FALSE, height=FALSE)
        self.__new_user_frames = []
        self.__known_users = known_users
        self.__new_users = []
        self.__base_window()
        super().mainloop()

    def __base_window(self):
        ''''''
        self.__header.pack(padx=10, pady=10, side=TOP)
        steam = SteamDataReader()
        steam_users = steam.user_nodes
        for user in list(steam_users.keys()):
            self.__add_user_frame(user, steam_users[user]["accountname"])
        btn = Button(self, text="Done", bg="lightgray", command=self.__save_users)
        btn.pack(padx=10, pady=10, fill=BOTH, side=BOTTOM)

    def __add_user_frame(self, userid, username):
        ''''''
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
        ''''''
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

class GUIGameMenu(Tk):
    ''''''

    def __init__(self, username):
        ''''''
        super().__init__()
        self.title("{0}'s games".format(username))
        self.resizable(width=FALSE, height=FALSE)
        self.game_list()
        super().mainloop()

    def __find_users_games(self):
        ''''''
        pass # place holder

    def __game_list():
        ''''''
        pass # place holder

class GUILogin(Tk):
    ''''''

    def __init__(self):
        '''Create users list.'''
        super().__init__()
        self.username = ""
        self.users = []

    def mainloop(self):
        '''
        If only one user is in the list auto login as that user.
        If more than one user is in the list show the GUI list.
        '''
        self.title("Login")
        userslen = len(self.users)
        passcount = 0
        for user in self.users:
            if not user[1] == "[NULL]":
                passcount += 1
        if len(self.users) == 0:
            exit() # Change to quit() for later call of GUIGameMenu(login.username)
        elif len(self.users) == 1 or passcount == 1:
            self.__run_steam(0)
        else:
            self.__make_buttons()
        super().mainloop()

    def __make_buttons(self):
        '''Create a button for each steam user.'''
        self.users.sort()
        count = -1
        for user in self.users:
            if not user[1] == "[NULL]":
                count += 1
                button = Button(self, text=user[0], # Need to make work with Linux & Apple
                    command=lambda index=count: self.__run_steam(index))
                button.pack(side=LEFT)
        self.resizable(width=FALSE, height=FALSE)

    def __run_steam(self, count):
        '''Select action based on OS.'''

        def windows(count):
            '''Kill Windows Steam process and restart as the selected user.'''
            Popen("wmic process where name='Steam.exe' delete")
            sleep(3)
            cmd = "C:\Program Files (x86)\Steam\Steam.exe -fullscreen -login {0} {1}"
            cmd = cmd.format(self.users[count][0], self.users[count][1])
            Popen(cmd)

        def linux(count): # need to thread for later call of GUIGameMenu(login.username) do to use of self.withdraw()
            '''Kill Linux Steam process and restart as the selected user.'''
            os_system("pkill steam")
            sleep(3)
            cmd = "steam -fullscreen -login {0} {1}"
            cmd = cmd.format(self.users[count][0], self.users[count][1])
            self.withdraw() # hide the tk window while steam is running.
            os_system(cmd)

        def apple(count):
            '''Kill Apple Steam process and restart as the selected user.'''
            pass # place holder

        self.username = self.users[count][0]
        if system() == "Windows":
            windows(count)
        elif system() == "Linux":
            linux(count)
        elif system() == "Apple":
            apple(count)

        exit() # Change to quit() for later call of GUIGameMenu(login.username)

if __name__ == '__main__':
    data = UserData()
    if data.users_changed():
        GUISetup(data.read_in_users())
    else:
        login = GUILogin()
        login.users = data.ids_to_names(data.read_in_users())
        login.mainloop()
##        if not login.username == '':   # place holder
##           GUIGameMenu(login.username) # place holder

#The next line holds data it's not a comment do not edit or move the text!!!
#Live SteamBoost data do not edit!:
