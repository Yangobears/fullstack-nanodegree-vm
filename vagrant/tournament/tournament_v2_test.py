from tournament_v2 import *
def testDeleteCascadePlayerTournament():
    tid = registerTournament("1")
    pid = registerPlayer("A")
    entersTournament(pid, tid)
    deleteTournaments()
    deletePlayers()
    c = countTournament_Player()
    if c != 0:
        raise ValueError("Deletion of Player or Tournament didnt del the corresponding T_P")
    print "0. T_P can be cascadely deleted."

def testRegisterTournament():
    deleteTournaments()
    registerTournament("1")
    c = countTournament()
    if c != 1:
        raise ValueError("After one tournament registers, countTournament() should be 1.")
    print "1. Tournament can be created."

def testRegisterPlayer():
    deletePlayers()
    pid = registerPlayer("A")
    c = countPlayer()
    if c != 1:
        raise ValueError("After one player registers,  countPlayer() should be 1.")
    print "2. Player can be created."

def testPlayerEntersTournament():
    clearAll()
    tid = registerTournament("1")
    pid = registerPlayer("A")
    entersTournament(pid, tid)
    tcountplayer = countPlayerInTournament(tid)
    if tcountplayer != 1:
        raise ValueError("Players count in a tournament should equal to tournament size.")
    print "3. Player can enter a tournament."


#Question, how to test exception? Exception code?
def testPlayerEntersTournamentUnregistered():
    clearAll()
    entersTournament(100, 100)

    c= countTournament_Player()
    if c!= 0:
        raise ValueError("Non exisiting player and tournament cannot be used to create a entering event.")
    print "4. Unregistered Player cannot enter an unregistered tournament."

def testPlayerEntersTournamentRepeatly():
    clearAll()
    tid = registerTournament("1")
    pid = registerPlayer("A")
    entersTournament(pid, tid)
    #enters again
    entersTournament(pid, tid)
    c= countTournament_Player()
    if c >1:
        raise ValueError("Player is already entered in tournament cannot again.")
    print "5. Player can enter a tournament only once."


def testStandingsBeforeMatches():
    clearAll()
    pid1= registerPlayer("Melpomene Murray")
    pid2 = registerPlayer("Randy Schwartz")
    pid3= registerPlayer("hi ")
    pid4 = registerPlayer("hey ")
    tid1 = registerTournament("1")
    tid2 = registerTournament("2")
    #tour1
    entersTournament(pid1, tid1)
    entersTournament(pid2, tid1)
    entersTournament(pid3, tid1)
    #tour2
    entersTournament(pid1, tid2)
    entersTournament(pid3, tid2)
    standings_1 = playerStandings(tid1)
    standings_2 = playerStandings(tid2)
    if len(standings_2) != 2 or len(standings_1) != 3:
        raise ValueError("Standing size wrong")
    print "6. Newly registered players appear in their assigned tournament standings with no matches."

def test_report_match():
    clearAll()
    pid1= registerPlayer("Melpomene Murray")
    pid2 = registerPlayer("Randy Schwartz")
    pid3= registerPlayer("hi ")
    pid4 = registerPlayer("hey ")
    tid = registerTournament("1")

    entersTournament(pid1, tid)
    entersTournament(pid2, tid)
    entersTournament(pid3, tid)
    entersTournament(pid4, tid)
    reportMatch(0, tid, pid1, pid2)
    reportMatch(1, tid, pid3, pid4)
    standings = playerStandings(tid)
    for (pid, pscore, pname) in standings:
        if pid == pid1 and pscore != 3:
            raise ValueError("Winner should have +3 score")
        if pid == pid2 and pscore != 0:
            raise ValueError("Loser should have +0 score")
        if pid in (pid3, pid4) and pscore != 1:
            raise ValueError("Draw would give both +1 score")
    print "7. After a match, players have updated scores."

def test_try_pairing_no_rematch():
    clearAll()
    pid1= registerPlayer("Melpomene Murray")
    pid2 = registerPlayer("Randy Schwartz")
    tid = registerTournament("1")

    entersTournament(pid1, tid)
    entersTournament(pid2, tid)

    success = tryPairing(tid, pid1, pid2)
    fail = tryPairing(tid, pid1, pid2)

    if  success != True or fail != False:
        raise ValueError("Cannot rematch")
    print "8. Rematch cannot happen during pairing."


def test_set_bye():
    clearAll()
    tid = registerTournament("1")
    pid1= registerPlayer("Melpomene Murray")
    entersTournament(pid1, tid)
    pid = setBye(tid)
    if pid != pid1:
        raise ValueError()
    pid2= registerPlayer("Mel Murray")
    entersTournament(pid2, tid)
    pid = setBye(tid)
    if pid != pid2:
        raise ValueError()
    print "9. Set Bye works fine."

def test_remove_Bye_Player():
    clearAll()
    pid1= registerPlayer("Melpomene Murray")
    pid2 = registerPlayer("Randy Schwartz")
    pid3= registerPlayer("hi ")
    tid = registerTournament("1")
    entersTournament(pid1, tid)
    entersTournament(pid2, tid)
    entersTournament(pid3, tid)

    even_standing =removeByePlayer(tid)

    if len(even_standing) !=2:
        raise ValueError()
    print "10. Remove Bye Player works fine."

def testPairings():
    clearAll()
    pid1=registerPlayer("Twilight Sparkle")
    pid2= registerPlayer("Fluttershy")
    pid3= registerPlayer("Applejack")
    pid4= registerPlayer("Pinkie Pie")
    tid = registerTournament("1")
    entersTournament(pid1, tid)
    entersTournament(pid2, tid)
    entersTournament(pid3, tid)
    entersTournament(pid4, tid)
    standings = playerStandings(tid)
    #Before match, you have to try pairing
    tryPairing(tid, pid1, pid2)
    tryPairing(tid, pid3, pid4)
    #Report Match result
    reportMatch(0, tid, pid1, pid2)
    reportMatch(0, tid, pid3, pid4)
    #Score:
    #Pid:   1  2  3  4
    #Score: 3, 0, 3, 0
    pairings = swissPairings(tid)

    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")

    [(ppid1, pname1, ppid2, pname2), (ppid3, pname3, ppid4, pname4)] = pairings
    correct_pairs = set([frozenset([pid1, pid3]), frozenset([pid2, pid4])])
    actual_pairs = set([frozenset([ppid1, ppid2]), frozenset([ppid3, ppid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with high score should be paired .")
    #Round2

    reportMatch(1, tid, pid1, pid3)
    reportMatch(0, tid, pid2, pid4)
    #Score:
    #Pid:   1  2  3  4
    #Score: 4, 3, 4, 0
    #So no rematch rule 1-2, 3-4, 1-3, 2-4 already happend:
    #So expected 2-3, 1-4
    pairings = swissPairings(tid)

    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")

    [(ppid1, pname1, ppid2, pname2), (ppid3, pname3, ppid4, pname4)] = pairings
    correct_pairs = set([frozenset([pid3, pid2]), frozenset([pid1, pid4])])
    actual_pairs = set([frozenset([ppid1, ppid2]), frozenset([ppid3, ppid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After another match, players should not be rematched with previously played.")
    print "11. Rematch works."


def testByePairs():
    clearAll()
    pid1=registerPlayer("Twilight Sparkle")
    pid2= registerPlayer("Fluttershy")
    pid3= registerPlayer("Applejack")
    tid = registerTournament("1")
    entersTournament(pid1, tid)
    entersTournament(pid2, tid)
    entersTournament(pid3, tid)
    #first player should be assign bye.
    pairs = swissPairings(tid)
    [(ppid1, pname1, ppid2, pname2)] = pairs
    if ppid1==pid1 or ppid2 == pid1:
        raise ValueError()
    reportMatch(0,tid, pid2,pid3)

    # pid1:3 pid2: 3, pid3:1
    pairs = swissPairings(tid)
    [(ppid1, pname1, ppid2, pname2)] = pairs
    if ppid1==pid2 or ppid2 == pid2:
        raise ValueError()
    print "12. Assign bye to different player every time."


if __name__ == '__main__':
    testDeleteCascadePlayerTournament()
    testRegisterTournament()
    testRegisterPlayer()
    testPlayerEntersTournament()
    testPlayerEntersTournamentUnregistered()
    testPlayerEntersTournamentRepeatly()
    testStandingsBeforeMatches()
    test_report_match()
    test_try_pairing_no_rematch()
    test_set_bye()
    test_remove_Bye_Player()
    testPairings()
    testByePairs()
    print "Success!  All tests pass!"