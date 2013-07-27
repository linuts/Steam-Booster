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
"""

from tkinter import Tk, Frame, Entry, Button, Label, TOP, BOTTOM, LEFT, FALSE
from re import findall as re_findall
from os import system as os_system
from subprocess import Popen
from platform import system
from time import sleep

class SteamDataReader():
    '''Reads ACF and VDF Steam config files. Use self call to get data.'''

    def __init__(self, filename):
        ''''''
        self.__filename = filename

    def __call__(self):
        ''''''
        data = self.__read_in_file()
        profile = self.__make_profile(data)
        return self.__make_nodes(profile, self.__purge_nondata(data))

    def __read_in_file(self):
        ''''''
        data = []
        with open(self.__filename, 'r') as file:
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
                        data += [{newline[0]:newline[1:]}]
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
        holder = []
        newdata = dict()
        for index in range(len(data)):
            if profile[index] == maxdepth - 1 and type(data[index]) == str:
                newdata[data[index]] = holder
                holder = []
            elif profile[index] == maxdepth - 1 and type(data[index]) == dict:
                newdata.update(data[index])
            else:
                holder.append(data[index])
        return newdata

class UserData():
    ''''''

    def __init__(self):
        ''''''
        self.__filename = __file__.split('\\')[-1]
        self.__header = "#Live SteamBoost data do not edit!:"

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
                    print(strlist)
                    return self.__to_list(strlist)

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

class GUIFirstRun(Tk): # fix private var use
    ''''''

    def __init__(self):
        ''''''
        super().__init__()
        self.title("SteamBoost user setup")
        self.resizable(width=FALSE, height=FALSE)
        self.user_frames = []
        self.user_names = []
        self.user_passwords = []
        self.__add_click()
        self.__button_menu()
        super().mainloop()

    def __save_users(self, users):
        ''''''
        if len(users) > 0:
            data = UserData()
            data.write_out_users(users)

    def __button_menu(self):
        ''''''
        holder = Frame(self)
        addbtn = Button(holder, text="Add more users", width=21, command=self.__add_click)
        donebtn = Button(holder, text="Done", width=21, command=self.__done_click)
        addbtn.pack(side=LEFT)
        donebtn.pack(side=LEFT)
        holder.pack(side=BOTTOM)

    def __add_click(self):
        ''''''
        if  len(self.user_frames) < 10:
            self.user_frames += [Frame(self, pady=5, padx=5)]
            usernote = Label(self.user_frames[-1], text="Username: ")
            self.user_names += [Entry(self.user_frames[-1], width=15)]
            passnote = Label(self.user_frames[-1], text="Password: ")
            self.user_passwords += [Entry(self.user_frames[-1], width=15, show='*')]
            usernote.pack(side=LEFT)
            self.user_names[-1].pack(side=LEFT)
            passnote.pack(side=LEFT)
            self.user_passwords[-1].pack(side=LEFT)
            self.user_frames[-1].pack(side=TOP)

    def __done_click(self):
        ''''''
        users = []
        for index in range(len(self.user_frames)):
            user = self.user_names[index].get()
            password = self.user_passwords[index].get()
            if len(user) > 0 and len(password) > 0:
                users += [(user, password)]

        self.__save_users(users)
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
        If not running windows send an error to the user. - temp
        If only one user is in the list auto login as that user.
        If more than one user is in the list show the GUI list.
        '''

        self.title("Login")
        if len(self.users) == 0:
            exit() # Change to quit() for later call of GUIGameMenu(login.username)
        elif len(self.users) == 1:
            self.__run_steam(0)
        else:
            self.__make_buttons()

        super().mainloop()

    def __make_buttons(self):
        '''Create a button for each steam user.'''
        self.users.sort()
        count = -1
        for user in self.users:
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
    users = data.read_in_users()
    if len(users) == 0:
        run = GUIFirstRun()
    else:
        login = GUILogin()
        login.users = users
        login.mainloop()
        #if not login.username == '':   # place holder
        #   GUIGameMenu(login.username) # place holder

#The next line holds data it's not a comment do not edit or move the text!!!
#Live SteamBoost data do not edit!: