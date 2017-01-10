=======INSTRUCTIONS=======

Project requires the installation of the stable version of DistAlgo.

In order to test if the DistAlgo is present or not run the below command

"python3 -m da" without double quotes.

The display of usage indicates the presence of DistAlgo module.

1) Extract the folder to a directory of your choice.
2) Go to the src/ directory where the project is extracted and run the following command
	"python3 -m da main.da <testNum>"
3) <testNum> can be any of [1a, 1b, 2, 3, 4, 5, 6, 7] 

4) When the tests are completed, a message will be displayed on the console for the same.
At that point tester can press "Ctrl-c" to terminate the system.

=======MAIN FILES=======

Location of main files 
dalgo is the root directory. It will be present at the location where you have extracted it. 
In dalgo there are files for Client.da, Coordinator.da, Worker.da, Master.da, main.da

"da" modules:

	src/Client.da
	src/Coordinator.da
	src/DatabaseEmulator.da
	src/main.da
	src/Master.da
	src/Worker.da

We have created PolicyEvaluator.py written in python for the evaluation policy.
We have also created our separate Logger.py python class for logging purposes.
We have created a Version class for keeping track of different versions of attributes

python modules:

	src/PolicyEvaluator.py
	src/Logger.py
	src/RandomStringGenerator.py
	src/Version.py

The root directory also contains a config/ directory which contains the configurations
for different test cases.

There are total 8 test cases:
	config/config1a.json
		#TODO: RR

	config/config1b.json
		#TODO: RW

	config/config2.json
		similar to (1), except that the commit of r is delayed, because some of
		the pendingMightRead sets for relevant attributes are non-empty when
		coord(oW) receives the result of r from the worker
	
	config/config3.json
		the coordinator coord(oW) for the object oW written by a read-write 
		request r receives the result of r from the worker, immediately 
		detects a conflict, and re-starts r.
	
	config/config4.json
		the coordinator coord(oW) for the object oW written by a read-write
		request r receives the result of r from the worker, waits for relevant
		pendingMightReads to be resolved, and then detects a conflict and re-starts r
	
	config/config5.json
		similar to (2), except the client incorrectly predicts which object is written
	
	config/config6.json
		similar to (4), except the client incorrectly predicts which object is written
	
	config/config7.json
		a read request is delayed in order to prevent starvation of writes, and later 
		released and processed

# TODO: edit the following
Each test case directory contains config.json, database.xml, policy.json and 
requests.json. After the tests are run, "program.log" will contain the detailed logs of the
activites and messages that has been passed in the system, and "database.txt" contains a dump
of the database after all requests have been evaluated, so that it's consistency can be checked.

=======BUGS AND LIMITATIONS=======
#TODO: edit the following
There are problem at the DatabaseEmulator end for maxDbLatency and minDdLatency.
The problem is introduced because in order to delay the updates we use DistAlgo "await" in database emulator
which is causing problem, then we decided to use python built-in sleep. That is not working properly too.
We have formulated a strategy for the same but due to the extensive code involved, we are planning the
update in phase 4.

Apart from this, problem were also encountered due to the await statement in other places.
In order to tackle this, we had to employ other methods like introducing our own wait queue to mimick the delays. 
There are some places where, using await results in an infinite loop. The nature of this problem is
not predictable. We were not able to pinpoint the exact nature in this phase. But we will soon be updating
it in the next phase.

=======CONTRIBUTIONS=======

CONTRIBUTORS:
	Shikhar Sharma
	Siddharth Rajendra Kawar

The strategy to implement was discussed extensively between both the contributors.
The work was divided per modules basis where we first agreed on the different functionality
that each module should have and what results each class and its subfunctions returns.

Following is the list of main modules and writers:
	-------------------------------------------
	| Modules	              |  Writer       |
	-------------------------------------------
	 Client.da 	              | Siddharth
	 Worker.da                | Siddharth
	 Coordinator.da           | Siddharth + Shikhar
	 DatabaseEmulator.da      | Siddharth + Shikhar
	 main.da                  | Siddharth
	 PolicyEvaluator.py       | Shikhar
	 Logger.py                | Shikhar
	 RandomStringGenerator.py | Shikhar
	 mapper.py                | Shikhar
	 Version.py				  | Siddharth

Apart from this in every file there were some code which was written by both
the contributors. To write each function that is written is cumbersome. Therefore the above is rough
divison. 

=======COMMENTS=======
1.
We used our own logger class for logging various send's and receive's of messages.
And to pinpoint various checkpoints in the program like commits, aborts, their reasons, etc.

2.
Also, due to problems with await statement, we used our own wait queues to store requests 
that were dependent on a tentative update by a request that had neither committed nor aborted.
When requests are completed(by either committing or aborting), we check the wait queue for requests
that are waiting on this request, and resume them. 