#!/usr/bin/python3
'''Milestone_A_who_and_what.py
This runnable file will provide a representation of
answers to key questions about your project in CSE 415.

'''

# DO NOT EDIT THE BOILERPLATE PART OF THIS FILE HERE:

CATEGORIES=['Baroque Chess Agent','Feature-Based Reinforcement Learning for the Rubik Cube Puzzle',\
  'Hidden Markov Models: Algorithms and Applications']

class Partner():
  def __init__(self, lastname, firstname, uwnetid):
    self.uwnetid=uwnetid
    self.lastname=lastname
    self.firstname=firstname

  def __lt__(self, other):
    return (self.lastname+","+self.firstname).__lt__(other.lastname+","+other.firstname)

  def __str__(self):
    return self.lastname+", "+self.firstname+" ("+self.uwnetid+")"

class Who_and_what():
  def __init__(self, team, option, title, approach, workload_distribution, references):
    self.team=team
    self.option=option
    self.title=title
    self.approach = approach
    self.workload_distribution = workload_distribution
    self.references = references

  def report(self):
    rpt = 80*"#"+"\n"
    rpt += '''The Who and What for This Submission

Project in CSE 415, University of Washington, Winter, 2019
Milestone A

Team: 
'''
    team_sorted = sorted(self.team)
    # Note that the partner whose name comes first alphabetically
    # must do the turn-in.
    # The other partner(s) should NOT turn anything in.
    rpt += "    "+ str(team_sorted[0])+" (the partner who must turn in all files in Catalyst)\n"
    for p in team_sorted[1:]:
      rpt += "    "+str(p) + " (partner who should NOT turn anything in)\n\n"

    rpt += "Option: "+str(self.option)+"\n\n"
    rpt += "Title: "+self.title + "\n\n"
    rpt += "Approach: "+self.approach + "\n\n"
    rpt += "Workload Distribution: "+self.workload_distribution+"\n\n"
    rpt += "References: \n"
    for i in range(len(self.references)):
      rpt += "  Ref. "+str(i+1)+": "+self.references[i] + "\n"

    rpt += "\n\nThe information here indicates that the following file will need\n"+\
     "to be submitted (in addition to code and possible data files):\n"
    rpt += "    "+\
     {'1':"Baroque_Chess_Agent_Report",'2':"Rubik_Cube_Solver_Report",\
      '3':"Hidden_Markov_Models_Report"}\
        [self.option]+".pdf\n"

    rpt += "\n"+80*"#"+"\n"
    return rpt

# END OF BOILERPLATE.

# Change the following to represent your own information:

iqra = Partner("Imtiaz", "Iqra", "iqra0908@uw.edu")
matt = Partner("Vaughn", "Matt", "mpvaughn@uw.edu")
team = [iqra, matt]

OPTION = '1'
# Legal options are 1, 2, and 3.

title = "A Blustering Baroque Chess Player"

approach = '''Our approach is to first understand the rules of Baroque chess.
Next we will look up some open source intelligent evalautions to get the ideas
how to create a static evaluation fot our agent. Alongside, we will implement
minimax with alpha-beta pruning in the algorithm. We are also planning to play
with expectimax in this agent and will look up on negamax and other advanced
forms to improve alpha beta pruning further. In the end we will implement the
personality of our agent.'''

workload_distribution = '''We will mostly try to do pair programming but just
for the sake of records, Iqra will take the responsibility of implementing
aplhabeta pruning and integrating expectimax or negamax to see the results,
and Matt will work on static evaluatio function and other ways to make our
agent unbeatable. Both partners expect to be closely involved in writing 
the move-generation code and defining the personality of the agent.'''

reference1 = '''Baroque Chess, by Chad W Smith;
    URL: https://www.scribd.com/document/312467727/Baroque-Chess (accessed March. 01, 2019)'''

reference2 = '''Ultima - The Chess Variant Pages,
    available online at: https://www.chessvariants.com/other.dir/ultima.html'''

our_submission = Who_and_what([iqra, matt], OPTION, title, approach, workload_distribution, [reference1, reference2])

# You can run this file from the command line by typing:
# python3 who_and_what.py

# Running this file by itself should produce a report that seems correct to you.
if __name__ == '__main__':
  print(our_submission.report())
