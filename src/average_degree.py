import sys
import os
import argparse
import re
import time
import json
import networkx as nx

def calculate_a_degree(G):
    if len(G.nodes()) == 0:
        return 0
    return sum(list(G.degree().values()))*1.0/len(G.nodes())  
def ce_format(s):
    non_ascii = re.compile(r'[^\x20-\x7F]')
    ret = non_ascii.sub('', s)
    ret = re.sub(r'[\n\t]', ' ', ret)
    ret = re.sub(r'\/', '/', ret)
    ret = re.sub(r'\'', '\'', ret)
    ret = re.sub(r'\"', '\"', ret)
    return ret
def process_file(infilename, outfilename) :
    counter = 0
    outfile = open(outfilename, 'w')
    G = nx.Graph()
    hashtag_dict = {}
    with open(infilename, 'rU') as infile:
        for line in infile:
            counter += 1
            currtweet = json.loads(line)
            currtweettext = currtweet.get("text", "")
            currtweettime = currtweet.get("created_at", "")
            if currtweettime == "":
                continue      
            cleanedtweet = ce_format(currtweettext)
            hashtagset = set(str(part[1:]) for part in cleanedtweet.split() if part.startswith('#'))
            curtags = list(hashtagset)
            curtagslen = len(curtags)
            time_struct = time.strptime(currtweettime, "%a %b %d %H:%M:%S +0000 %Y")
            currtweettime_e = int(time.mktime(time_struct))
            if curtagslen>1:
                for t1 in xrange(curtagslen):
                    for t2 in xrange(t1+1, curtagslen):
                        G.add_edge(curtags[t1],curtags[t2])
                        if currtweettime_e in hashtag_dict.keys():
                            hashtag_dict[currtweettime_e].append((curtags[t1],curtags[t2]))
                        else:
                            hashtag_dict[currtweettime_e] = [(curtags[t1],curtags[t2])]       
            for k in hashtag_dict.keys():
                if (currtweettime_e - k) > 60:
                    for (n1,n2) in hashtag_dict[k]:
                        if (n1,n2) in G.edges():
                            G.remove_edge(n1,n2)
                    hashtag_dict.pop(k, None)           
            outfile.write("{0:.2f}\n".format(calculate_a_degree(G)))                         
    outfile.close()
    return counter
def main() :
    usage='python average_degree.py -options <addtional parameters>'
    description='Calculate the average degree of a vertex.'
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument("-i", "--input", action="store", nargs=1, dest="input", 
                        metavar=("input"), help="Input file name.")
    parser.add_argument("-o", "--output", action="store", nargs=1, dest="output", 
                        metavar=("output"), help="Output file name.")
    args = parser.parse_args()
    if args.input and args.output :
        if not os.path.isfile(args.input[0]) :
            print 'Input file "%s" does not exist.'%args.input[0]
            sys.exit(1)          
    else :
        print 'Check the path to files.'
        sys.exit(1)

    start_time = time.time()
    counter= process_file(args.input[0], args.output[0])
if __name__ == '__main__':
    main()
