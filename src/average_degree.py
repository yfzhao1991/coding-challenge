import sys
import os
import argparse
import re
import time
import json
import networkx as nx

def compute_average_degree(G):
    if len(G.nodes()) == 0:
        return 0
    return sum(list(G.degree().values()))*1.0/len(G.nodes())  
def extract_format(s):
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
            cur_tweet = json.loads(line)
            cur_tweet_text = cur_tweet.get("text", "")
            cur_tweet_time = cur_tweet.get("created_at", "")
            if cur_tweet_time == "":
                continue      
            cleaned_tweet = extract_format(cur_tweet_text)
            hashtag_set = set(str(part[1:]) for part in cleaned_tweet.split() if part.startswith('#'))
            cur_tags = list(hashtag_set)
            len_cur_tags = len(cur_tags)
            time_struct = time.strptime(cur_tweet_time, "%a %b %d %H:%M:%S +0000 %Y")
            cur_tweet_time_epoch = int(time.mktime(time_struct))
            if len_cur_tags>1:
                for t1 in xrange(len_cur_tags):
                    for t2 in xrange(t1+1, len_cur_tags):
                        G.add_edge(cur_tags[t1],cur_tags[t2])
                        if cur_tweet_time_epoch in hashtag_dict.keys():
                            hashtag_dict[cur_tweet_time_epoch].append((cur_tags[t1],cur_tags[t2]))
                        else:
                            hashtag_dict[cur_tweet_time_epoch] = [(cur_tags[t1],cur_tags[t2])]       
            for k in hashtag_dict.keys():
                if (cur_tweet_time_epoch - k) > 60:
                    for (n1,n2) in hashtag_dict[k]:
                        if (n1,n2) in G.edges():
                            G.remove_edge(n1,n2)
                    hashtag_dict.pop(k, None)           
            outfile.write("{0:.2f}\n".format(compute_average_degree(G)))                         
    outfile.close()
    return counter
def main() :
    usage='python average_degree.py -options <addtional parameters>'
    description='Calculate the average degree of a vertex in a Twitter hashtag graph for the last 60 seconds, and update this each time a new tweet appears.'
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument("-i", "--input", action="store", nargs=1, dest="input", 
                        metavar=("input"), help="Input file name.")
    parser.add_argument("-o", "--output", action="store", nargs=1, dest="output", 
                        metavar=("output"), help="Output file name.")
    args = parser.parse_args()
    if args.input and args.output :
        if not os.path.isfile(args.input[0]) :
            print 'Error! Input file "%s" does not exist.'%args.input[0]
            sys.exit(1)          
    else :
        print 'Error! Check the path to files.'
        sys.exit(1)

    start_time = time.time()
    counter= process_file(args.input[0], args.output[0])
if __name__ == '__main__':
    main()
