# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import os
import json

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "Twitch Commands - Counter"
Website = "https://twitch.tv/RzR32"
Description = "Commands - Counter for the Stream - RzR32"
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
            # int
            self.int_Trigger = "!int"
            self.int_Cooldown = 10
            self.int_Permission = "Everyone"
            self.int_Target = "TargetUser"
            self.int_SpecialUser = "RzR32"
            self.int_Output = "ist zum <X> mal die Mitte runtergerannt!"
            # cannon
            self.cannon_Trigger = "!cannon"
            self.cannon_Cooldown = 10
            self.cannon_Permission = "Everyone"
            self.cannon_Target = "TargetUser"
            self.cannon_SpecialUser = "RzR32"
            self.cannon_Output = "hat schon <X> mal den Cannon angetoucht!"
            # ult
            self.ult_Trigger = "!ult"
            self.ult_Cooldown = 10
            self.ult_Permission = "Everyone"
            self.ult_Target = "TargetUser"
            self.ult_SpecialUser = "RzR32"
            self.ult_Output = "hat schon <X> mal kein Zielwasser getrunken!"
            # flash
            self.flash_Trigger = "!flash"
            self.flash_Cooldown = 10
            self.flash_Permission = "Everyone"
            self.flash_Target = "TargetUser"
            self.flash_SpecialUser = "RzR32"
            self.flash_Output = "hat schon <X> mal sein Flash vergessen!"
            # ignite
            self.ignite_Trigger = "!ignite"
            self.ignite_Cooldown = 10
            self.ignite_Permission = "Everyone"
            self.ignite_Target = "TargetUser"
            self.ignite_SpecialUser = "RzR32"
            self.ignite_Output = "hat schon <X> mal nicht genug Feufeu gehabt!"

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

    # if needed, create *int* folder
    directory = os.path.join(os.path.dirname(__file__), "int")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # if needed, create *cannon* folder
    directory = os.path.join(os.path.dirname(__file__), "cannon")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # if needed, create *ult* folder
    directory = os.path.join(os.path.dirname(__file__), "ult")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # if needed, create *flash* folder
    directory = os.path.join(os.path.dirname(__file__), "flash")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # if needed, create *ignite* folder
    directory = os.path.join(os.path.dirname(__file__), "ignite")
    if not os.path.exists(directory):
        os.makedirs(directory)

    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    #
    # int
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.int_Trigger and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.int_Trigger, data.User):
        Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(
            ScriptName, ScriptSettings.int_Trigger, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.int_Trigger and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.int_Trigger, data.User) and Parent.HasPermission(
            data.User, ScriptSettings.int_Permission, data.User):
        if data.IsFromTwitch():
            counter(data, "int", ScriptSettings.int_Trigger, ScriptSettings.int_Cooldown,
                    ScriptSettings.int_Target, ScriptSettings.int_SpecialUser, ScriptSettings.int_Output)
    #
    # cannon
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.cannon_Trigger and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.cannon_Trigger, data.User):
        Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(
            ScriptName, ScriptSettings.cannon_Trigger, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.cannon_Trigger and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.cannon_Trigger, data.User) and Parent.HasPermission(
            data.User, ScriptSettings.cannon_Permission, data.User):
        if data.IsFromTwitch():
            counter(data, "cannon", ScriptSettings.cannon_Trigger, ScriptSettings.cannon_Cooldown,
                ScriptSettings.cannon_Target, ScriptSettings.cannon_SpecialUser, ScriptSettings.cannon_Output)
    #
    # ult
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.ult_Trigger and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.ult_Trigger, data.User):
        Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(
            ScriptName, ScriptSettings.ult_Trigger, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.ult_Trigger and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.ult_Trigger, data.User) and Parent.HasPermission(
            data.User, ScriptSettings.ult_Permission, data.User):
        if data.IsFromTwitch():
            counter(data, "ult", ScriptSettings.ult_Trigger, ScriptSettings.ult_Cooldown,
                    ScriptSettings.ult_Target, ScriptSettings.ult_SpecialUser, ScriptSettings.ult_Output)
    #
    # flash
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.flash_Trigger and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.flash_Trigger, data.User):
        Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(
            ScriptName, ScriptSettings.flash_Trigger, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.flash_Trigger and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.flash_Trigger, data.User) and Parent.HasPermission(
            data.User, ScriptSettings.flash_Permission, data.User):
        if data.IsFromTwitch():
            counter(data, "flash", ScriptSettings.flash_Trigger, ScriptSettings.flash_Cooldown,
                    ScriptSettings.flash_Target, ScriptSettings.flash_SpecialUser, ScriptSettings.flash_Output)

    # ignite
    # if the cmd is on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.ignite_Trigger and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.ignite_Trigger, data.User):
        Parent.SendStreamMessage("Time Remaining " + str(Parent.GetUserCooldownDuration(
            ScriptName, ScriptSettings.ignite_Trigger, data.User)))
    # make the cmd, if not on cool down
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.ignite_Trigger and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.ignite_Trigger, data.User) and Parent.HasPermission(
            data.User, ScriptSettings.ignite_Permission, data.User):
        if data.IsFromTwitch():
            counter(data, "ignite", ScriptSettings.ignite_Trigger, ScriptSettings.ignite_Cooldown,
                    ScriptSettings.ignite_Target, ScriptSettings.ignite_SpecialUser, ScriptSettings.ignite_Output)

    return


# ---------------------------------------
# counter - all - functions
# ---------------------------------------
def counter(data, folder, Trigger, Cooldown, Target, SpecialUser, Output):
    username = data.GetParam(1)
    name = ""
    
    # get target - name
    if Target.__eq__("TargetUser"):
        if not username.__eq__(""):
            if not username.startswith("@"):
                Parent.SendStreamMessage("Bitte gib ein Twitch Namen an! (mit @)")
                return
            else:
                name = username
        else:
            Parent.SendStreamMessage("Bitte gib ein Twitch Namen an!")
            return

    elif Target.__eq__("StreamUser"):
        name = "@" + Parent.GetChannelName()
    elif Target.__eq__("SpecialUser"):
        name = "@" + SpecialUser

    # get current ignite from file
    file_path___counter = "Services/Scripts/Counter/" + folder + "/" + name + ".txt"

    # check if file exists - if not create
    if not os.path.exists(file_path___counter):
        with open(file_path___counter, 'w') as my_file:
            my_file.write("0")
            pass

    # read line from the file
    file_counter = open(file_path___counter, "r")
    i_counter = file_counter.readline()
    file_counter.close()

    # add one
    i_counter = int(i_counter) + 1

    # write line to the file
    file_counter = open(file_path___counter, "w")
    file_counter.write(i_counter.__str__())
    file_counter.close()

    # get the output, replace the var with the new ignite
    text = Output
    text = text.replace("<X>", i_counter.__str__())
    text = name + " " + text

    # send the message
    Parent.SendStreamMessage(text)
    # set the cool down
    Parent.AddUserCooldown(ScriptName, Trigger, data.User, Cooldown)
    return


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
