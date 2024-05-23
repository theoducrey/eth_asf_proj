with open("output/result_dependencies.logs", "r") as f:
    dependencies = f.readlines()

all_dependencies = []
for i in dependencies:
    if "missing dependencies" in i:
        j = i.split("missing dependencies")[1][5:-2]
        j = j.split(", ")
        for k in range(len(j)//2):
            temp = j[k*2][2:-1] + " .-. " + j[k*2+1][1:-2]
            if temp not in all_dependencies:
                all_dependencies.append(temp)
string_to_print = ""
if len(all_dependencies) == 0:
    string_to_print = "In your manifest the no dependencies are missing\n"
else:
    string_to_print = "In your manifest the following dependencies are missing: \n"
    for i in all_dependencies:
        j = i.split(" .-. ")
        string_to_print += j[1] + "  requires that  " + j[0] + "  happens first.\n"

with open("output/result_state.logs", "r") as g:
    state_reconciliation = g.readlines()

all_inconsistencies = []
for i in state_reconciliation:
    if "state differences" in i:
        j = i.split("state differences")[1][2:-2]
        while j[0] != ":":
            j = j[1:]
        j = j[3:0]
        j = j.split(", ")
        for k in range(len(j)//2):
            t1 = j[k*2][2:-1]
            t2 = j[k*2+1][1:-2]
            if t1[0] == "'":
                t1 = t1[1:]
            if t2[-1] == "'":
                t2 = t2[:-1]
            if t1 != "puppetserver" and t1[:5] != "jruby": 
                temp = t1 + " .-. " + t2
                if temp not in all_inconsistencies:
                    all_inconsistencies.append(temp)
string_to_print += "\n"
if len(all_inconsistencies) == 0:
    string_to_print += "Additionally your manifest caused no inconsistencies with these edges to files in the directory graph\n"
else: 
    string_to_print += "Additionally your manifest caused inconsistencies with these edges to files in the directory graph: \n"
    for i in all_inconsistencies:
        j = i.split(" .-. ")
        string_to_print += "edge from  " + j[0] + "  to  " + j[1] + " \n"
#print(string_to_print)
with open("output.txt", "w") as f:
    f.write(string_to_print)
        

