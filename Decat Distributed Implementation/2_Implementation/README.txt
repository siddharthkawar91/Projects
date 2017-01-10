
=======INSTRUCTIONS=======

Project requires the installation of the stable version of DistAlgo.

In order to test if the DistAlgo is present or not run the below command

"python3 -m da" without double quotes.

The display of usage indicated the presence of DistAlgo module.

1) Extract the folder to the directory of your choice.
2) Go to the directory where the project is extracted and run below command
	"python3 -m da main.da"
3) By default this will run the test specified in test1 folder
   In order to run the different testcase replace the test1 in line number 5
   with test file name that you want to run for e.g. You want to run 
   test2 then change the below line to 
	"configFile = open('test1/config.json')" --> "configFile = open('test2/config.json')"
4) When the test are completed a message will be displayed on the console for the same. At that point tester can press "Ctrl-c"
   to terminate the system.

=======MAIN FILES=======

Location of main files 
dalgo is the root directory. It will be present at the location where you have extracted it. 
In dalgo there are files for Client.da, Coordinator.da, Worker.da, Master.da, main.da

"da" modules:

	dalgo/Client.da
	dalgo/Coordinator.da
	dalgo/DatabaseEmulator.da
	dalgo/main.da
	dalgo/Master.da
	dalgo/Worker.da

We have created PolicyEvaluator.py written in python for the evaluation policy.
We have also created our seprate Logger.py python class for logging purposes.
For mimicking cache we have created Cache.py.

python modules:

	dalgo/PolicyEvaluator.py
	dalgo/Logger.py
	dalgo/Cache.py
	dalgo/RandomStringGenerator.py

The root directory also contains the test cases folder.
There are total 8 test cases:
	dalgo/test1
		Normal flow of the algorithm mentioned in the paper using two requests
	
	dalgo/test2
		Abort and restart request due to subject conflict
	
	dalgo/test3
		Abort and restart request due to resource conflict
	
	dalgo/test4
		Abort and restart request due to dependency on tentative update
		that was ultimately aborted due to resource conflict
	
	dalgo/test5
		same as above, but also displays the functionality of delaying a request 
		because it depends on a tentative update made by a request that has neither
		committed nor aborted
		Done using a wait queue (explained in Comments section of this README)
	
	dalgo/test6
		Displays caching and piggybacking recent updates to subject attributes
	
	dalgo/test7
		Displays caching and piggybacking recent updates to resource attributes

	dalgo/test8
		Stress testing by sending random requests generating based on a config file
	

Each test case directory contains config.json, database.xml, policy.json and 
requests.json. After the tests are run, "program.log" will contain the detailed logs of the
activites and messages that has been passed in the system, and "database.txt" contains a dump
of the database after all requests have been evaluated, so that it's consistency can be checked.

=======BUGS AND LIMITATIONS=======

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
	 Worker.da                | Shikhar
	 Coordinator.da           | Shikhar
	 DatabaseEmulator.da      | Siddharth
	 main.da                  | Shikhar
	 PolicyEvaluator.py       | Shikhar
	 Logger.py                | Shikhar
	 RandomStringGenerator.py | Siddharth
	 Cache.py                 | Siddharth
	 mapper.py                | Siddharth

Apart from this in every file there were some code which was written by both
the contributors. To write each function that is written is cumbersome. Therefore the above is rough
divison. 

=======COMMENTS=======
1.
We used our own logger class for logging various send's and receive's of messages.
And to pinpoint various checkpoints in the program like commits, aborts, their reasons, etc.

2.
Also, due to problems with await statement, we used our own wait queue to store requests 
that were dependent on a tentative update by a request that had neither committed nor aborted.
When requests are completed(by either committing or aborting), we check the wait queue for requests
that are waiting on this request, and resume them. 