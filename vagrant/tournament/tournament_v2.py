import psycopg2


DRAW_SCORE = 1
WIN_SCORE = 3
BYE_SCORE = WIN_SCORE

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament_v2")

#Delete Methods

def deleteTournaments():
    """Remove all the match records from the database.
       Will also cascadely del all the Tournament_Player references"""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM Tournament CASCADE")
    DB.commit()
    DB.close()

def deletePlayers():
    """Remove all the player records from the database.
       Will also cascadely del all the Tournament_Player references"""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM Player CASCADE")
    DB.commit()
    DB.close()

def deleteMatchesByTournament(tid):
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE * FROM match where tid = %s", (tid,))
    DB.commit()
    DB.close()

def clearAll():
    deleteTournaments()
    deletePlayers()

#Register Methods:

def registerTournament(name):
    """Return a tournament id newly added to the tournament database.

    The database assigns a unique serial id number for the tournament,
    also init the size of people entering the tournament as zero.

    Args:
      name: the tournament's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO tournament (name, size) values (%s, 0) RETURNING id", (name,))
    DB.commit()
    tid = c.fetchone()[0]
    DB.close()
    return tid


def registerPlayer(name):
    """Return a player id newly added to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO player (name) values (%s) RETURNING id", (name,))
    DB.commit()
    pid = c.fetchone()[0]
    DB.close()
    return pid

#Count Methods:

def countTournament_Player():
    """For testing purpose
       Return number of tournament_player connection numbers.
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) from Tournament_Player")
    return c.fetchone()[0]


def countTournament():
    """Return number of tournament
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) from tournament")
    return c.fetchone()[0]


def countPlayerInTournament(tid):
    """For testing purpose
       Should equal to tournament size field.
       Return how many players in this tournament.

    Args:
      tid: unique tournament id.
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) from tournament_player where tid= %s", (tid,))
    return c.fetchone()[0]

def returnSizeOfTournament(tid):
    """Return number of player in given tournament
    Args:
      tid: unique tournament id.
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT size from tournament where id= %s", (tid,))
    return c.fetchone()[0]

def countPlayer():
    """ Count all registered Player"""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) from Player")
    return c.fetchone()[0]

def countMatch():
    """ Count all registered Matches """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) from Match")
    return c.fetchone()[0]

#Actions

def entersTournament(pid, tid):
    """Adds a player to a particular tournament.
       Cannot enter if pid and tid doesnt exist in Player and Tournament table.
    Args:
      pid: player id,
      tid: tournament id
    """
    DB = connect()
    c = DB.cursor()
    try:
        c.execute("INSERT INTO Tournament_Player (pid, tid, matches, score, bye) values (%s, %s, 0, 0, 0)", (pid, tid,))
        c.execute("UPDATE Tournament set size = size +1")
    except psycopg2.Error, e:
        #print e #commented out for testing purpose
        pass
    DB.commit()
    DB.close()

def playerStandings(tid):
    """Returns a list of the players and their win records, sorted by scores in a tournament.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        score: the score players have
        name: the player's full name (as registered)
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT pid, score, Player.name FROM Tournament_Player join Player on Player.id = Tournament_Player.pid where tid =%s ORDER BY score DESC  ", (tid,))
    players = [(row[0], row[1], row[2]) for row in c.fetchall()]
    DB.close()
    return players


def reportMatch(draw, tid, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      draw: draw = true: both winner and lose get 1 point
            draw = false: winner + 3, loser + 0
      tid: specific tournament id
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    #insert into match table

    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO match (draw, tid, winner, loser) values (%s, %s, %s, %s)", (draw, tid, winner, loser))

    #update column wins and matches  player table
    if draw:

        c.execute("UPDATE Tournament_Player SET score = score + %s, matches = matches + %s WHERE pid = %s and tid = %s", (DRAW_SCORE,1,  winner,tid))
        c.execute("UPDATE Tournament_Player SET score = score + %s, matches = matches +%s WHERE pid = %s and tid = %s", (DRAW_SCORE,1,  loser,tid))
    else:
        c.execute("UPDATE Tournament_Player SET score = score +%s, matches = matches +%s WHERE pid = %s and tid = %s", (WIN_SCORE, 1, winner,tid))
        c.execute("UPDATE Tournament_Player SET matches = matches +%s WHERE pid = %s and tid = %s", (1, loser,tid))

    DB.commit()
    DB.close()

def setBye(pid, tid):
    """Assign bye to a player who has not been assigned bye before
       if pid, tid's bye is already 1 , skip, else set it to 0 and give 3 point as score.

    Args:
      pid : potential player id
      tid : tournament id
    Returns:
      True: means setBye is successful, this pid has bye this time
      False: means didn't setBye on this pid, tid, because it has already got bye
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT bye from Tournament_Player where tid=%s and pid = %s", (tid, pid, ))
    bye = c.fetchone()[0]
    if bye == 1:
        DB.close()
        return False
    else:
        c.execute("UPDATE Tournament_Player SET bye = 1, score =score + %s where tid=%s and pid = %s", (BYE_SCORE, tid, pid, ))
        DB.commit()
        DB.close()
        return True

def removeByePlayer(tid):
    """Remove the player who has been assigned bye from the standing list
       if there are odd player numbers .

    Args:
      tid : tournament id
    Returns:
      The player list that has even number.
    """
    tsize = returnSizeOfTournament(tid)
    players = playerStandings(tid)
    if (tsize %2 == 1):
        index = 0
        for (pid, score, pname) in players:
            if setBye(pid, tid):
                # pid is selected for bye this time.
                break
            index = index +1
        del players[index]
    return players

def tryPairing(tid, pid1, pid2):
    """Try to pair pid1 and pid2 in tournament tid without rematching
    Args:
      tid : tournament id
      pid1: player1 id
      pid2: player2 id
    Returns:
      True: pair successfully
      False: cannot pair, has been paired before.
    """
    DB = connect()
    c = DB.cursor()
    try:
        c.execute("INSERT INTO Pairs (tid, player1, player2) values (%s, %s, %s)", (tid, pid1, pid2))
        DB.commit()
        DB.close()
        return True
    except psycopg2.Error, e:
        DB.close()
        return False


def swissPairings(tid):
    """Returns a list of pairs of players for the next round of a match.

    1. If there are odd number of players, one player in the front of the
    standing will be assign bye if he hasnt been assigned bye before.

    2. Each player is paired with anotherplayer with an equal or nearly-equal
     win record, also prevent rematch with players that have been paired before.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    evenStandings = removeByePlayer(tid)
    pairs = []
    #prevent rematch:
    #try pairing up adjacent players, psycopg2.Error, then retry with next one.
    while len(evenStandings)> 0:
        #Step1: confirm player1
        player1 = evenStandings.pop(0)
        #Step2: find a pairing for player1
        success = False
        index = 0
        while  not success:
            candidate = evenStandings[index]
            success = tryPairing(tid, player1[0], candidate[0])
            index = index + 1
        evenStandings.remove(candidate)
        pairs.append((player1[0], player1[2], candidate[0], candidate[2]))
    return pairs



