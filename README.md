Requirement : docker installed and callable using the docker-compose up command 

To get more information about the pipeline and how to run it we invite you to read the implementation setup of the project report availible as a pdf on the git : 

A first try run may be done using : python3 main_one_run.py -tm apt -nr 10 , you may need to adapt the command python3 to your local python installation

To get the artifact for the dependencies you should uncomment the line 49 in file trace_analyzer_5.py and run the program as normal.
After the run output.txt will have, as shown in the report, in the first section a list of "missing resource dependencies".
This is the result of the addition of the faulty dependency accessed-accessed dependency which is not a correct dependency, and this test shows
that it can detect dependencies that are not in the catalog graph already and that if there is a dependency not accounted for
the program will find it.

For the second artefact for state inconsistencies uncomment lines 183, 184, 185 in file run_docker_puppet.py. 
After the run output.txt will have, as shown in the report, in the second section a missing directory-file edge. 
This edge is generated as a result of randomly adding a new file after the runs and the program detecting this inconsistency.
This test shows that the program can detect inconsistencies between the states and will output them.
