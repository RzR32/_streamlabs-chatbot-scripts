# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import json
import os
import threading

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "League Champion"
Website = "https://twitch.tv/RzR32"
Description = "Send your League of Legends Mastery in your Stream Chat and/or as text overlay - Unofficial"
Creator = "RzR32"
Version = "0.1"

# ---------------------------
#   Define Global Variables
# ---------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else:  # set variables if no settings file is found
            # League
            self.SummonerName = "RzR32"
            self.Server = "euw1"
            # Mastery
            self.Mastery = "!mastery"
            self.Mastery_Cooldown = 10
            self.Mastery_Permission = "Everyone"
            self.Mastery_Count = 3
            self.Mastery_Usage = "Stream Chat"
            # Token
            self.Token = ""
            # Query
            self.Query = 5

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """ Save settings contained within the .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")


# ---------------------------
#   [Required] Initialize Data (Only called on load)
# ---------------------------
def Init():
    # Load settings
    global ScriptSettings
    ScriptSettings = Settings(settingsFile)

    # if needed, create *data* folder
    directory = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Folder for champ mastery
    directory = os.path.join(os.path.dirname(__file__), "data/champs")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # folder for the other stuff
    directory = os.path.join(os.path.dirname(__file__), "data/stuff")
    if not os.path.exists(directory):
        os.makedirs(directory)

    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    #
    # Mastery
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Mastery and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Mastery, data.User):
        Parent.SendStreamMessage(
            "Time Remaining " + str(Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Mastery, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Mastery and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Mastery, data.User) and Parent.HasPermission(data.User,
                                                                                    ScriptSettings.Mastery_Permission,
                                                                                    ScriptSettings.SummonerName):
        if data.IsFromTwitch():
            if ScriptSettings.Mastery_Usage == "Stream Chat" or ScriptSettings.Mastery_Usage == "Chat Both":
                MASTERY("twitch")
        if data.IsFromDiscord():
            if ScriptSettings.Mastery_Usage == "Discord Chat" or ScriptSettings.Mastery_Usage == "Chat Both":
                MASTERY("discord")
        # set the cool down
        Parent.AddUserCooldown(ScriptName, ScriptSettings.Mastery, data.User, ScriptSettings.Mastery_Cooldown)
    return


# ---------------------------------------
# MASTERY functions
# ---------------------------------------
def MASTERY(Usage):
    # Global Var
    SummonerName = ScriptSettings.SummonerName
    # Riot Server
    _Server = ScriptSettings.Server
    # Riot Games API Token
    Token = ScriptSettings.Token
    headers = {"X-Riot-Token": Token}
    headers_json = {"content-type": "application/json"}

    # Start int for Count
    int_to_count = 0
    # End int for Count
    int_config = ScriptSettings.Mastery_Count

    # String for the Summoner ID, needed to do the other request´s
    s_id = ""

    # String´s for Champion
    string_champion_id = ""
    string_champion_level = ""
    string_champion_points = ""

    # Strings´s for ID in NAME
    string_key = ""
    string_id = ""

    # String for the output
    string_out_mastery = ""

    # Game Version
    s_game_version = ""

    # get latest game version
    response_game_version = Parent.GetRequest("https://ddragon.leagueoflegends.com/api/versions.json",
                                              headers_json)
    out_game_version = response_game_version.split(',')

    file_path___champ_ID = "Services/Scripts/League_All-in-One/data/stuff/Champion_ID.txt"
    file_champ_ID = open(file_path___champ_ID, "w")

    for s_game_version in out_game_version:
        s_game_version = s_game_version.replace("[", "").replace("\"", "").replace("\\", "")

        if s_game_version.__contains__("response"):
            s_game_version = s_game_version[14:]
            # check if file already exist
            if os.path.isfile(file_path___champ_ID):
                # Check Version in File
                with open(file_path___champ_ID, "r") as file_champ:
                    first_line = file_champ.readline()
                    if not first_line.__contains__(s_game_version):
                        # version is the another, remake text file
                        file_champ_ID.write("Version: " + s_game_version + "\n\n")
                        s_game_version = "Y " + s_game_version
                    else:
                        s_game_version = "N " + s_game_version
                    break
            else:
                # recreate file
                file_champ_ID.write("Version: " + s_game_version + "\n\n")
                s_game_version = "Y " + s_game_version
            break

    if s_game_version.startswith("Y "):
        # string_champion_id to string_champion_name
        response_summoner_name = Parent.GetRequest("https://ddragon.leagueoflegends.com/cdn/" + s_game_version[2:] +
                                                   "/data/de_DE/champion.json", headers_json)
        out_summoner_name = response_summoner_name.split(',')

        for s_summoner_name in out_summoner_name:
            s_summoner_name = s_summoner_name.replace("\"", "").replace("\\", "")

            if s_summoner_name.startswith("id"):
                string_id = s_summoner_name[3:]

            elif s_summoner_name.startswith("key"):
                string_key = s_summoner_name[4:]

                # Write new File with "id + key"
                file_champ_ID.write(" " + string_key + ":" + string_id + "\n")

    file_champ_ID.close()

    # get SummonerID from summonerName
    url_summonerid = "https://" + _Server + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
    result_summonerid = Parent.GetRequest(url_summonerid + SummonerName, headers)
    out_summonerid = result_summonerid.split("\n")

    for s_summonerid in out_summonerid:

        s_summonerid = s_summonerid.replace(",", " ")
        s_summonerid = s_summonerid.replace("{", "").replace("}", "")
        s_summonerid = s_summonerid.replace("\"", "").replace("\\", "")

        if s_summonerid.__contains__("status: 4"):
            Parent.Log(ScriptName, "Execution failed! (Client Side)")
            return
        elif s_summonerid.__contains__("status: 5"):
            Parent.Log(ScriptName, "Execution failed! (Server Side)")
            return

        if s_summonerid.__contains__("response: id:"):
            s_id = s_summonerid[15:]
            s_id = s_id[:48]

            # get mastery from user
            url_champion_mastery = "https://" + _Server + ".api.riotgames.com/lol/champion-mastery/v4" \
                                                          "/champion-masteries/by-summoner/" + s_id
            response_champion_mastery = Parent.GetRequest(url_champion_mastery, headers)

            out_champion_mastery = response_champion_mastery.split(",")

            for s_champion_mastery in out_champion_mastery:
                s_champion_mastery = s_champion_mastery.replace("{", "").replace("}", "") \
                    .replace("[", "").replace("]", "").replace("\"", "").replace("\\", "").strip()

                if s_champion_mastery.startswith("response: championId:"):
                    string_champion_id = s_champion_mastery[21:]

                elif s_champion_mastery.startswith("championId:"):
                    string_champion_id = s_champion_mastery[11:]

                elif s_champion_mastery.startswith("championLevel:"):
                    string_champion_level = s_champion_mastery[14:]

                elif s_champion_mastery.startswith("championPoints:"):
                    string_champion_points = s_champion_mastery[15:]

                if s_champion_mastery.startswith("summonerId"):
                    if int_to_count < int_config:
                        int_to_count += 1

                        file_path___champs = "Services/Scripts/League_All-in-One/data/champs/champ" + \
                                             int_to_count.__str__() + ".txt"
                        file_champs = open(file_path___champs, "w")

                        file_champ_ID = open(file_path___champ_ID, "r")
                        Lines = file_champ_ID.readlines()

                        for line in Lines:
                            line = line.strip()
                            line = " " + line
                            if line.startswith(" " + string_champion_id + ":"):
                                # Output Chat
                                string_out_mastery = string_out_mastery + " ♦ " + int_to_count.__str__() + \
                                                     ". Champion: " + line[line.find(":") + 1:] + \
                                                     ", Level: " + string_champion_level + \
                                                     ", Points: " + string_champion_points
                                file_champ_ID.close()
                                # Output File
                                file_champs.write(int_to_count.__str__() +
                                                  ". Champion: " + line[line.find(":") + 1:] +
                                                  ", Level: " + string_champion_level +
                                                  ", Points: " + string_champion_points)
                                file_champs.close()
                    else:
                        break
    # OUTPUT
    if Usage == "twitch" or Usage == "Chat Both":
        Parent.SendStreamMessage(string_out_mastery + " ♦ ")
    if Usage == "discord" or Usage == "Chat Both":
        Parent.SendDiscordMessage(string_out_mastery + " ♦ ")
    return


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def start():
    MASTERY("")


# ---------------------------
# Make the Request one time and start the timer - manuel
# ---------------------------
def start_Timer():
    start()
    threading.Timer(ScriptSettings.Query * 60, start_Timer).start()


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def OpenRiotAPI():
    os.system("start \"\" https://developer.riotgames.com/")


# ---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
    return


# ---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------
def ReloadSettings(jsonData):
    """Reload settings on Save"""
    global ScriptSettings
    ScriptSettings.Reload(jsonData)


# ---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
# ---------------------------
def Unload():
    return


# ---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
# ---------------------------
def ScriptToggled(state):
    return
