# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import json
import os
import threading
from shutil import copy

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "League Rank (Solo/Flex)"
Website = "https://twitch.tv/RzR32"
Description = "Send your League of Legends Elo (Solo/Flex) in your Stream Chat and/or as text overlay - Unofficial"
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
            # Elo
            self.Elo = "!elo"
            self.Elo_Cooldown = 10
            self.Elo_Permission = "Everyone"
            self.Elo_Usage = "Stream Chat"
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

    # Main Folder for ranks
    directory = os.path.join(os.path.dirname(__file__), "data/ranks")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Solo "ranked" folder
    directory = os.path.join(os.path.dirname(__file__), "data/ranks/solo")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Flex "ranked" folder
    directory = os.path.join(os.path.dirname(__file__), "data/ranks/flex")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # TfT "ranked" folder
    directory = os.path.join(os.path.dirname(__file__), "data/ranks/tft")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Folder for champ mastery
    directory = os.path.join(os.path.dirname(__file__), "data/champs")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # folder for the other stuff - should be already created
    directory = os.path.join(os.path.dirname(__file__), "data/stuff")
    if not os.path.exists(directory):
        os.makedirs(directory)

    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    # Elo
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Elo and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Elo, data.User):
        Parent.SendStreamMessage(
            "Time Remaining " + str(Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Elo, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Elo and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Elo, data.User) and Parent.HasPermission(data.User,
                                                                                ScriptSettings.Elo_Permission,
                                                                                ScriptSettings.SummonerName):
        if data.IsFromTwitch():
            if ScriptSettings.Elo_Usage == "Stream Chat" or ScriptSettings.Elo_Usage == "Chat Both":
                ELO("twitch")
        if data.IsFromDiscord():
            if ScriptSettings.Elo_Usage == "Discord Chat" or ScriptSettings.Elo_Usage == "Chat Both":
                ELO("discord")
        # set the cool down
        Parent.AddUserCooldown(ScriptName, ScriptSettings.Elo, data.User, ScriptSettings.Elo_Cooldown)
    return


# ---------------------------------------
# ELO functions
# ---------------------------------------
def ELO(Usage):
    # Global Var
    SummonerName = ScriptSettings.SummonerName
    # Riot Server
    _Server = ScriptSettings.Server
    # Riot Games API Token
    Token = ScriptSettings.Token
    headers = {"X-Riot-Token": Token}

    # String for the Summoner ID, needed to do the other request´s
    s_id = ""

    # String´s for the Output
    string_solo = ""
    string_flex = ""
    string_tft = ""

    # String´s to temporarily save the other string´s
    string_type = ""
    string_rank = ""
    string_tier = ""
    string_leaguePoints = ""
    string_progress = ""

    # String for the output
    string_out_elo = ""

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

    # get Solo/Flex elo
    url_league = "https://" + _Server + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
    result_league = Parent.GetRequest(url_league + s_id, headers)
    out_league = result_league.split(",")

    for s_league in out_league:
        s_league = s_league.replace("{", "").replace("}", "")
        s_league = s_league.replace("[", "").replace("]", "")
        s_league = s_league.replace("\"", "").replace("\\", "")

        if s_league.startswith("queueType"):
            string_type = s_league[16:].replace("_", "").replace("SR", "").replace("5x5", "")
        elif s_league.startswith("tier"):
            string_tier = s_league[5:]
        elif s_league.startswith("rank"):
            string_rank = s_league[5:]
        elif s_league.startswith("leaguePoints"):
            string_leaguePoints = s_league[13:] + "LP"

            if string_type.__contains__("SOLO"):
                string_solo = string_type + " " + string_tier + " " + string_rank + " " + string_leaguePoints
            elif string_type.__contains__("FLEX"):
                string_flex = string_type + " " + string_tier + " " + string_rank + " " + string_leaguePoints

            # tier image
            filename = string_tier.lower() + "_" + string_rank.lower() + ".png"
            file_src = "Services/Scripts/League_All-in-One/data/stuff/Images/" + string_tier.lower() + "/" + filename
            file_dst = "Services/Scripts/League_All-in-One/data/ranks/" + string_type.lower() + "/rank.png"
            copy(file_src, file_dst)
            # tier trim
            file_src = "Services/Scripts/League_All-in-One/data/stuff/Images/trims/" + string_tier.lower() + ".png"
            file_dst = "Services/Scripts/League_All-in-One/data/ranks/" + string_type.lower() + "/trim.png"
            copy(file_src, file_dst)
        elif s_league.startswith("progress"):
            string_progress = s_league[9:]
            string_progress = string_progress.replace("N", "/")

            if string_type.__contains__("SOLO"):
                string_solo = string_solo + " " + string_progress
            elif string_type.__contains__("FLEX"):
                string_flex = string_flex + " " + string_progress

    # Output for image standard - unranked
    file_src_unranked = "Services/Scripts/League_All-in-One/data/stuff/Images/not_ranked/unranked.png"
    file_src_trim = "Services/Scripts/League_All-in-One/data/stuff/Images/trims/default.png"

    # Output for the text files
    file_path___solo_path = "Services/Scripts/League_All-in-One/data/ranks/solo/solo_duo.txt"
    file_solo = open(file_path___solo_path, "w")

    file_path___flex_path = "Services/Scripts/League_All-in-One/data/ranks/flex/flex.txt"
    file_flex = open(file_path___flex_path, "w")

    # Output for image - if unranked
    if string_solo.__eq__(""):
        string_solo = "SOLO Unranked"
        # tier image
        file_dst_unranked_rank = "Services/Scripts/League_All-in-One/data/ranks/solo/rank.png"
        copy(file_src_unranked, file_dst_unranked_rank)
        # tier trim
        file_dst_unranked_trim = "Services/Scripts/League_All-in-One/data/ranks/solo/trim.png"
        copy(file_src_trim, file_dst_unranked_trim)

    file_solo.write(string_solo)
    file_solo.close()

    # Output for image - if unranked
    if string_flex.__eq__(""):
        string_flex = "FLEX Unranked"
        # tier image
        file_dst_unranked_rank = "Services/Scripts/League_All-in-One/data/ranks/flex/rank.png"
        copy(file_src_unranked, file_dst_unranked_rank)
        # tier trim
        file_dst_unranked_trim = "Services/Scripts/League_All-in-One/data/ranks/flex/trim.png"
        copy(file_src_trim, file_dst_unranked_trim)

    file_flex.write(string_flex)
    file_flex.close()

    # Output for the Chat
    string_out_elo = " ♦ " + string_solo + " ♦ " + string_flex + " ♦ "

    if Usage == "twitch" or Usage == "Chat Both":
        Parent.SendStreamMessage(string_out_elo)
    if Usage == "discord" or Usage == "Chat Both":
        Parent.SendDiscordMessage(string_out_elo)
    return


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def start():
    ELO("")


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
