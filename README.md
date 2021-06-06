# Terraria vanilla server


### General Config
- Have a `worlds` folder at the root of your directory structure (you can have it anywhere, but change the volume binds accordingly)
- Put your worlds in the worlds folder
- When you create a container, map the port to 7777 internally, ie.: 1234:7777 (then forward port to 1234 in this case)
- Add a volume for the worlds mounted inside the container:
`./worlds:/root/.local/share/Terraria/Worlds/`\
- You can create a new world or select different world (located in the world folder above) by starting a container and attaching to it
`docker attach <container-name>`
- press enter
- choose the options you wish

To dettach without stopping the container:
`ctrl+p ctrl+q`


### docker-compose.yml exemple:
```
version: '3'
services:
  terraria-server:
    image: iceoid/terraria-server:1.4.2.2
    container_name: terraria-server
    restart: unless-stopped
    stdin_open: true
    tty: true
    ports:
      - 7779:7777
    volumes:
      - ./worlds:/root/.local/share/Terraria/Worlds/
    environment:
      - world=/root/.local/share/Terraria/Worlds/newworld.wld # Default is empty, so no world is loaded
      - maxplayers=8 # Default is 16
      - port=7777 # Default is 7777
      - password=newworld # Default is passworld
```


### environment variables (case-sensitive!):
| Env variable | Possible values (Default value) | Description | Example |
| :------------- | :----------: | :----------- | :----------- |
|  `world` | (*empty*) | Absolute path to your world | `world=/path/to/world_dir/` |
| `maxplayers` | 16 | The maximum number of players allowed |  `maxplayers=8` |
| `port` | 7777 | Port used internally by the terraria server | `port=8123` |
| `password` | *empty*  | Set a password for the server | `password=serverpassword` |
| `secure` | 1 | Option to prevent cheats. (1: no cheats or 0: cheats allowed) | `secure=0` |
|`motd` | (*empty*) | Set the server motto of the day text. | `motd=Welcome to my private server! :)` |
|`autocreate` | (*empty*) | Creates a world if none is found in the path specified by -world. World size is specified by: 1(small), 2(medium), and 3(large). | `autocreate=2` |
| `banlist` | (*empty*) | Specifies the location of the banlist. Defaults to "banlist.txt" in the working directory. (You need to add a volume bind accordingly) | `banlist=./banlist.txt ` |
-worldname <world name> - Sets the name of the world when using -autocreate.
-secure - Adds additional cheat protection to the server.
-noupnp - Disables automatic universal plug and play.
-steam - Enables Steam support.
-lobby friends / -lobby private - Allows only friends to join the server or sets it to private if Steam is enabled.
-ip <ip address> - Sets the IP address for the server to listen on
-forcepriority <priority> - Sets the process priority for this task. If this is used the "priority" setting below will be ignored.
-disableannouncementbox - Disables the text announcements Announcement Box makes when pulsed from wire.
-announcementboxrange <number> - Sets the announcement box text messaging range in pixels, -1 for serverwide announcements.
-seed <seed> - Specifies the world seed when using -autocreate



### Important!
If the `world` variable is left empty or not included, the server will need to be initialized manually after the container is spun up. You will need to attach to the container and select/create a world and set the players number, port and password manually.

1. `docker attach <container name>`
2. press _*enter*_
3. Go through the options
4. Detach from the container by pressing _*ctrl+p*_ _*ctrl+q*_


### List of server-side console commands from the [official documentation](https://terraria.fandom.com/wiki/Server#Server_files)
```
Once a dedicated server is running, the following commands can be run:

help - Displays a list of commands.
playing - Shows the list of players. This can be used in-game by typing /playing into the chat.
clear - Clear the console window.
exit - Shutdown the server and save.
exit-nosave - Shutdown the server without saving.
save - Save the game world.
kick <player name> - Kicks a player from the server.
ban <player name> - Bans a player from the server.
password - Show password.
password <pass> - Change password.
version - Print version number.
time - Display game time.
port - Print the listening port.
maxplayers - Print the max number of players.
say <message> - Send a message to all players. They will see the message in yellow prefixed with <server> in the chat.
motd - Print MOTD.
motd <message> - Change MOTD.
dawn - Change time to dawn (4:30 AM).
noon - Change time to noon (12:00 PM).
dusk - Change time to dusk (7:30 PM).
midnight - Change time to midnight (12:00 AM).
settle - Settle all water.
Note that a forward-slash / is not required to precede the command, as some command interfaces require. For a list of Tshock commands, refer to the TShock readme.

Command line parameters
The following is a list of parameters that can be entered when running TerrariaServer initially:

-config <file path> - Specifies a configuration file to use (see Server config file below).
-port <number> - Specifies the port to listen on.
-players <number> / -maxplayers <number> - Sets the max number of players.
-pass <password> / -password <password> - Sets the server password.
-motd <text> - Set the server motto of the day text.
-world <file path> - Load a world and automatically start the server.
-autocreate <number> - Creates a world if none is found in the path specified by -world. World size is specified by: 1(small), 2(medium), and 3(large).
-banlist <file path> - Specifies the location of the banlist. Defaults to "banlist.txt" in the working directory.
-worldname <world name> - Sets the name of the world when using -autocreate.
-secure - Adds additional cheat protection to the server.
-noupnp - Disables automatic universal plug and play.
-steam - Enables Steam support.
-lobby friends / -lobby private - Allows only friends to join the server or sets it to private if Steam is enabled.
-ip <ip address> - Sets the IP address for the server to listen on
-forcepriority <priority> - Sets the process priority for this task. If this is used the "priority" setting below will be ignored.
-disableannouncementbox - Disables the text announcements Announcement Box makes when pulsed from wire.
-announcementboxrange <number> - Sets the announcement box text messaging range in pixels, -1 for serverwide announcements.
-seed <seed> - Specifies the world seed when using -autocreate
Server config file
It is possible to start the dedicated server using a configuration file that enters the above parameters automatically. The config file must be called using the -config parameter. The file can have any name, but must be in the same folder as TerrariaServer.exe. If a server config file is defined and the file is not located during the server boot, then the server will ask the user to input the parameters as it would if run without a defined config file.

The following is a list of available config commands:

world=C:\Users\Defaults\My Documents\My Games\Terraria\Worlds\world1.wld - Load a world and automatically start the server.
autocreate=3 - Creates a new world if none is found. World size is specified by: 1(small), 2(medium), and 3(large).
seed=AwesomeSeed - Sets the world seed when using autocreate
worldname=World - Sets the name of the world when using autocreate
difficulty=0 - Sets world difficulty when using -autocreate. Options: 1(normal), 2(expert), 3(master), 4(journey)
maxplayers=8 - Sets the max number of players allowed on a server. Value must be between 1 and 255
port=7777 - Set the port number
password=p@55w0rd* - Set the server password
motd=Please don’t cut the purple trees! - Set the message of the day
worldpath=C:\Users\Defaults\My Documents\My Games\Terraria\Worlds\ - Sets the folder where world files will be stored
banlist=banlist.txt - The location of the banlist. Defaults to "banlist.txt" in the working directory.
secure=1 - Adds additional cheat protection.
language - Sets the server language from its language code. Available codes:
en/US = English
de/DE = German
it/IT = Italian
fr/FR = French
es/ES = Spanish
ru/RU = Russian
zh/Hans = Chinese
pt/BR = Portuguese
pl/PL = Polish
upnp=1 - Automatically forward ports with uPNP.
npcstream=60 - Reduces enemy skipping but increases bandwidth usage. The lower the number the less skipping will happen, but more data is sent. 0 is off.
priority=1 - Default system priority 0:Realtime, 1:High, 2:AboveNormal, 3:Normal, 4:BelowNormal, 5:Idle
Journey Mode power permissions for every individual power. 0: Locked for everyone, 1: Can only be changed by host, 2: Can be changed by everyone
journeypermission_time_setfrozen=2
journeypermission_time_setdawn=2
journeypermission_time_setnoon=2
journeypermission_time_setdusk=2
journeypermission_time_setmidnight=2
journeypermission_godmode=2
journeypermission_wind_setstrength=2
journeypermission_rain_setstrength=2
journeypermission_time_setspeed=2
journeypermission_rain_setfrozen=2
journeypermission_wind_setfrozen=2
journeypermission_increaseplacementrange=2
journeypermission_setdifficulty=2
journeypermission_biomespread_setfrozen=2
journeypermission_setspawnrate=2
Comment lines can be included using the hash symbol (#). Lines that begin with # will be skipped entirely.

Banning and un-banning
The command ban <player> will ban the indicated player from the server. A banned player, when they try to login, will be displayed the message:You are banned for [duration]: [reason]- [modname]. A banned player may then be un-banned by editing the file "banlist.txt," which is located in the Terraria folder. This document contains a list of all currently banned players. To un-ban a player, delete the player's name and IP address from the list.

```





