import psycopg2
from contextlib import contextmanager

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        return psycopg2.connect("dbname=tournament_v2")
    except:
        print ("Connection Failed")

@contextmanager
def get_cursor():
    """Query Helper Function using context lib, Creates a cursor
       from a database connection object, and performs query using
       that cursor.
    """
    DB = connect()
    cursor = DB.cursor()
    try:
        yield cursor
    except:
        raise
    else:
        DB.commit()
    finally:
        cursor.close()
        DB.close()

#Delete Methods

def deleteTournaments():
    """Remove all the match records from the database.
       Will also cascadely del all the Tournament_Player references"""
    with get_cursor() as c:
        c.execute("DELETE FROM Tournament CASCADE")

def deletePlayers():
    """Remove all the player records from the database.
       Will also cascadely del all the Tournament_Player references"""
    with get_cursor() as c:
        c.execute("DELETE FROM Player CASCADE")

def deleteMatchesByTournament(tid):
    """Remove all the match records from the database."""
    with get_cursor() as c:
        c.execute("DELETE * FROM match where tid = %s", (tid,))

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
    with get_cursor() as c:
        c.execute("INSERT INTO tournament (name) values (%s) RETURNING id", (name,))
        return c.fetchone()[0]



def registerPlayer(name):
    """Return a player id newly added to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    with get_cursor() as c:
        c.execute("INSERT INTO player (name) values (%s) RETURNING id", (name,))
        return c.fetchone()[0]


#Count Methods:

def countTournament_Player():
    """For testing purpose
       Return number of tournament_player connection numbers.
    """
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) from Tournament_Player")
        return c.fetchone()[0]

def countTournament():
    """Return number of tournament
    """
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) from tournament")
        return c.fetchone()[0]


def countPlayerInTournament(tid):
    """Return number of player in given tournament

    Args:
      tid: unique tournament id.
    """
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) from tournament_player where tid= %s", (tid,))
        return c.fetchone()[0]

def countPlayer():
    """ Count all registered Player"""
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) from Player")
        return c.fetchone()[0]

def countMatch():
    """ Count all registered Matches """
    with get_cursor() as c:
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
    with get_cursor() as c:
        try:
            c.execute("INSERT INTO Tournament_Player (pid, tid,bye) values (%s, %s,0)", (pid, tid,))
        except psycopg2.Error, e:
            #print e #commented out for testing purpose
            pass

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
    with get_cursor() as c:
        c.execute("SELECT pid, score, name FROM Scores WHERE tid =%s ", (tid,))
        players = [(row[0], row[1], row[2]) for row in c.fetchall()]
        return players


def reportMatch(draw, tid, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      draw: draw = 1: both winner and lose get 1 point
            draw = 0: winner + 3, loser + 0
      tid: specific tournament id
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    #insert into match table

    with get_cursor() as c:
        c.execute("INSERT INTO match (draw, tid, winner, loser) values (%s, %s, %s, %s)", (draw, tid, winner, loser))

def setBye(tid):
    """Assign bye to a player who has not been assigned bye before
       if pid, tid's bye is already 1 , skip, else set it to 0 and give 3 point as score.

    Args:
      tid : tournament id
    Returns:
      pid : the player who assigned bye this time.
    """
    with get_cursor() as c:
        c.execute("SELECT pid from NOT_YET_BYE where tid=%s LIMIT 1", (tid, ))
        pid = c.fetchone()[0]
        c.execute("UPDATE Tournament_Player SET bye = 1 where tid=%s and pid = %s", (tid, pid, ))
        return pid

def removeByePlayer(tid):
    """Remove the player who has been assigned bye from the standing list
       if there are odd player numbers .

    Args:
      tid : tournament id
    Returns:
      The player list that has removed the bye player and has even number size.
    """
    tsize = countPlayerInTournament(tid)
    if (tsize %2 == 1):
        pid = setBye(tid)
        with get_cursor() as c:
            c.execute("SELECT pid, score, name FROM Scores WHERE tid =%s AND pid != %s", (tid, pid))
            players = [(row[0], row[1], row[2]) for row in c.fetchall()]
            return players

    return playerStandings(tid)

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
    with get_cursor() as c:
        try:
            c.execute("INSERT INTO Pairs (tid, player1, player2) values (%s, %s, %s)", (tid, pid1, pid2))
            return True
        except psycopg2.Error, e:
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



