```
  _____               _     _ 
  \_   \___ ___  ___ (_) __| |
   / /\/ __/ _ \/ _ \| |/ _` |
/\/ /_| (_|  __/ (_) | | (_| |
\____/ \___\___|\___/|_|\__,_|
```

# Terraria vanilla server
.

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

### *Important: if you want the server to start automatically, you need to provide a world path by defining the environment variable `world` as shown bellow.*
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
      - world=/root/.local/share/Terraria/Worlds/newworld.wld
      - maxplayers=8
      - port=7777
      - password=newworld
```


### environment variables (case-sensitive!):
| Env variable | Default value | Description | Example |
| :------------- | :----------: | :----------- | :----------- |
| `world` | (*empty*) | Path to your world. _You need to provide a world for the server to start automatically_ | `world=/root/.local/share/Terraria/Worlds/My_World.wld` |
| `autocreate` | `2` | Creates a world if none is found in the path specified by -world. World size is specified by: 1(small), 2(medium), and 3(large). | `autocreate=2` |
| `seed` | (*empty*) | Specifies the world seed when using -autocreate | `seed=someseed123` |
| `worldname` | (*empty*) | Sets the name of the world when using -autocreate. | `worldname=world1` |
| `difficulty` | `0` | Sets world difficulty when using `autocreate`. Options: 0(normal), 1(expert), 2(master), 3(journey) | `difficulty=1` |
| `maxplayers` | `16` | The maximum number of players allowed |  `maxplayers=8` |
| `port` | `7777` | Port used internally by the terraria server. _You should not change this._ | `port=8123` |
| `password` | (*empty*)  | Set a password for the server | `password=serverpassword` |
| `motd` | (*empty*) | Set the server motto of the day text. | `motd=Welcome to my private server! :)` |
| `worldpath` | `/root/.local/share/Terraria/Worlds` | Sets the folder where world files will be stored | `worldpath=/root/.local/share/Terraria/Worlds` |
| `banlist` | `banlist.txt` | The location of the banlist. Defaults to "banlist.txt" in the working directory. | `banlist=/configs/banlist.txt` -> this would imply that you mount your banlist.txt file in the container's path `/configs/banlist.txt` |
| `secure` | `1` | Option to prevent cheats. (1: no cheats or 0: cheats allowed) | `secure=0` |
| `language` | `en/US` | Sets the server language from its language code. Available codes:  `en/US = English` `de/DE = German` `it/IT = Italian` `fr/FR = French` `es/ES = Spanish` `ru/RU = Russian` `zh/Hans = Chinese` `pt/BR = Portuguese` `pl/PL = Polish` | `language=fr/FR` |
| `upnp` | `0` | Enables/disables automatic universal plug and play. | `upnp=1` |
| `npcstream` | `0` | Reduces enemy skipping but increases bandwidth usage. The lower the number the less skipping will happen, but more data is sent. 0 is off. | `npcstream=60` |
| `priority` | (*empty*) | Sets the process priority | `priority=1` |




### Important!
If the `world` variable is left empty or not included, the server will need to be initialized manually after the container is spun up. You will need to attach to the container and select/create a world and set the players number, port and password manually. If you create a new world, it will be saved in the path defined by the environment variable `worldpath`.

1. `docker attach <container name>`
2. press _*enter*_
3. Go through the options
4. Detach from the container by pressing `ctrl+p` + `ctrl+q`


### List of server-side console commands from the [official documentation](https://terraria.fandom.com/wiki/Server#Server_files)

Once a dedicated server is running, the following commands can be run.\
First, attach to the container with `docker attach <container name>`.
```

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

Banning and un-banning
The command ban <player> will ban the indicated player from the server. A banned player, when they try to login, will be displayed the message:You are banned for [duration]: [reason]- [modname]. A banned player may then be un-banned by editing the file "banlist.txt," which is located in the Terraria folder. This document contains a list of all currently banned players. To un-ban a player, delete the player's name and IP address from the list.

```
Note: no forward-slash `/` is needed before the command, as some command interfaces require.




