#!/usr/bin/env python

'''
This script will grab the leaderboard from Advent of Code and post it to Slack

Kodsnack modified version in swedish

Original here: https://github.com/tomswartz07/AdventOfCodeLeaderboard

'''

import json, requests
from datetime import datetime

# see README for directions on how to fill these variables
# HARDCODED TO KODSNACK BOARD FOR NOW!
LEADERBOARD_ID = "194162"
SESSION_ID = ""
SLACK_WEBHOOK = ""

# these variables do not need edited
PRIVATE_LEADERBOARD_URL = "https://adventofcode.com/2017/leaderboard/private/view/"

def formatLeaderMessage(members):
    message = "Dagens topplista:"

    # add each member to message
    for username, score, stars, id, lastStarDate, diffSignal in members[0:15]:
        message += "\n*{}* {} Poäng, {} :star:{}".format(username, score, stars, diffSignal)

    message += "\n\n<{}{}|Se topplistan online>".format(PRIVATE_LEADERBOARD_URL, LEADERBOARD_ID)

    return message

def parseMembers(members_json):
    # get member name, score and stars
    dateFormat = "%Y-%m-%dT%H:%M:%S-0500"
    members = [[m["name"], m["local_score"], m["stars"], m["id"], datetime.strptime(m["last_star_ts"], dateFormat)] for m in members_json.values()]
    
    # Maintain two orderings, so that we can highlight when our ranking differs from that of the site
    aocOrdering = lambda member: (-member[1], int(member[3]))
    kodsnackOrdering = lambda member: (-member[1], -member[2], member[4])    
    aocMembers = sorted(members, key = aocOrdering)
    kodsnackMembers = sorted(members, key = kodsnackOrdering)
    
    # Get difference between the two lists, and signal it somehow
    for i, m in enumerate(kodsnackMembers):
        id = m[3]
        for j, n in enumerate(aocMembers):
            jd = n[3]
            if id == jd:
                diff = i - j
                diffSignal = '' if diff == 0 else ' :arrow_double_down:' if diff < - 1 else ' :arrow_down:' if diff == -1 else ' :arrow_up:' if diff == 1 else ' :arrow_double_up:'
                kodsnackMembers[i].append(diffSignal)        
                
    return kodsnackMembers

def postMessage(message):
    payload = json.dumps({
        "icon_emoji": ":christmas_tree:",
        "username": "Advent Of Code topplista",
        "text": message
    })

    requests.post(
        SLACK_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

def main():
    # make sure all variables are filled
    if LEADERBOARD_ID == "" or SESSION_ID == "" or SLACK_WEBHOOK == "":
        print("Please update script variables before running script.\nSee README for details on how to do this.")
        exit(1)

    # retrieve leaderboard
    r = requests.get(
        "{}{}.json".format(PRIVATE_LEADERBOARD_URL, LEADERBOARD_ID),
        cookies={"session": SESSION_ID}
    )
    if r.status_code != requests.codes.ok:
        print("Error retrieving leaderboard")
        exit(1)

    # get members from json
    members = parseMembers(r.json()["members"])

    # generate message to send to slack
    message = formatLeaderMessage(members)

    # send message to slack
    postMessage(message)

if __name__ == "__main__":
    main()
