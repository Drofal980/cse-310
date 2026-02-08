# Lightcycle

A terminal-based multiplayer lightcycle game based on the TRON movies.

## Instructions for Build and Use

Steps to build and/or run the software:

1. Download Python 3.10 or higher from [python.org](https://www.python.org/downloads/).
2. Create a virtual environment of your Python instance.
3. run `pip install requirements.txt` in your virtual environment.
4. Save both the lightcycle_client and lightcycle_server files. If wanting to play with more people, have them download the lightcycle_client.
5. The host computer should run:

```bash
   python3 PATH_TO_DIRECTORY/lightcycle_server.py
```

Instructions for using the software:

1. Each client that wants to connect should open the lightcycle_client.py file then edit line 8 to enter the ip of the host's computer.
2. Each client then opens Command Prompt and enter this command

```bash
   python3 PATH_TO_DIRECTORY/lightcycle_client.py "<Optional Username>"
```

## Development Environment

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Python 3.10 or higher
* Visual Studio Code

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [Socket Programming in Python (Guide)](https://realpython.com/python-sockets/)
* [Terminal Handling for Characters](https://docs.python.org/3/library/curses.html)
* [Reading json in python separated by newlines](https://stackoverflow.com/questions/58880619/reading-json-in-python-separated-by-newlines)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Make the paths go away
* [ ] Add a rejoin or rety button
* [ ] Add a scoreboard for "Kills"
