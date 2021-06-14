# monolithic simple module to convert IEX json to ELK json format
# IEX Attribution: 
# https://iextrading.com/trading/market-data/
# in middle of this module within transform function
# simple convervsion to DF - DataFrame
# TBD DataFrame Normalization and Naive Correlation functions TBD
# Within ELK this enables seeing stocks within same context -1,0,+1 std. deviations
#!/usr/bin/env python

import json
import pandas as pd
import pycurl
import requests
import sys
from io import BytesIO

# global variables for now
#debug = 1 # if 1 then print to stdout 
debug = 0 # if 0 then no print

def usage(nargs):
    # of if not at least 2 then exit
    print(nargs)
    print(sys.argv)
    print('usage: ')
    print('python iex-elk.py  ELK-index_name')
    print('or usage: python iex-elk.py  ELK-index_name src_file')
    print('or usage: python iex-elk.py  ELK-index_name src_file dest_file')
    quit()

def init_context():

    # use command line args
    # since python doesn't have a switch statement and nargs is unique use if's
    nargs=len(sys.argv)
    if nargs ==  1:
        # of if not at least 2 then exit
        usage(nargs)
        return_tuple = ("blank", "blank", "blank")
        return return_tuple

    if nargs ==  2:
        # of if 2 then get from curl
        index_name = sys.argv[1] ## index name for ELK
        lines = get_tops_curl_lines()

        # return lines
        return_tuple = (lines,index_name,"blank_dest_file")
        x, y, z = return_tuple
        if debug == 1:
            print(x)
            print(y)
            print(z)

        return return_tuple

    if nargs ==  3:
        # if 3 then get from saved tops src_file obtained from curl
        # of if not at least 2 then exit
        index_name = sys.argv[1] ## index name for ELK
        src_file = sys.argv[2]   ## get from IEX tops endpoint
        if debug == 1:
            print("Src_file=" + src_file)

        lines = get_tops_file_lines(src_file)

        # return lines 
        return_tuple = (lines, index_name, "blank_dest_file")
        return return_tuple
    
    if nargs ==  4:
        # if 4 then get from saved tops src_file obtained from curl
        index_name = sys.argv[1] ## index name for ELK
        src_file = sys.argv[2]   ## get from IEX tops file 
        dest_file = sys.argv[3]   ## get from IEX tops endpoint

        if debug == 1:
            print("Src_file=" + src_file)
            print("Dest_file=" + dest_file)

        lines = get_tops_file_lines(src_file)

        # return lines and dest_file
        return_tuple = (lines, index_name, dest_file)
        return return_tuple
    
    # TBD extend to streaming api or zmq topic
    if nargs >=  4:
        # of if at greater than  4 then exit
        usage(nargs);
        return_tuple = ("blank", "blank", "blank")
        return return_tuple

    return_tuple = ("blank", "blank", "blank")
    return return_tuple
    



# curl https://api.iextrading.com/1.0/tops
def get_tops_curl_lines():
    buffer = BytesIO()
    cg = pycurl.Curl()
    cg.setopt(cg.URL, 'https://api.iextrading.com/1.0/tops')
    cg.setopt(cg.WRITEDATA, buffer)
    cg.perform()

    lines = buffer.getvalue()
    if debug == 1:
        print(lines)
    cg.close() # close connection
    return lines

def get_tops_file_lines(src_file):
    with open(src_file) as open_file:
        lines = open_file.readlines()
    if debug == 1:
        print(lines)
    return lines


# below is command line ; makes assumption that previous curl from IEX Tops endpoint in tops.json
# curl -H 'Content-Type: application/x-ndjson' -XPOST 'localhost:9200/stocks1/_bulk?pretty' --data-binary @ptop1.json 
def post_tops_elk(lines,index_name):

    # specify URL for ELK localhost
    _url = 'http://localhost:9200/' + index_name + '/_bulk?pretty'
    _headers = {'Content-Type':'application/x-ndjson'}


    # POST
    try:
        r = requests.post(_url, headers=_headers, data=lines)

        # Print Response and Code
        if debug == 1:
            print(r.text)
            print(r.status_code)

    except requests.exceptions.Timeout:
        print("elasticsearch not running(?) error")
        print("Attempted to post to url:", _url)
        quit()

    # Maybe set up for a retry, or continue in a retry loop
    except requests.exceptions.TooManyRedirects:
        print("elasticsearch not running(?) error")
        print("Attempted to post to url:", _url)
        quit()

    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        print("elasticsearch not running(?) error")
        print("Attempted to post to url:", _url)
        quit()



# Transform IEX json format to required ELK json bulk api format
def transform(lines, index_name):


    if debug == 1:
        print(type(lines)) # debug to validate that response is correct type

    if isinstance(lines, list):
        if debug == 1:
            print("isList")

        a_string = ' '.join(lines)
        my_json = a_string
        #my_json = a_string.decode('utf8').replace("'", '"')
    else:
        if debug == 1:
            print("NOT LIST")
        my_json = lines

    if debug == 1:
        print(my_json)
        print('- ' * 20)

    # Load the JSON to a Python list & dump it back out as formatted JSON
    data = json.loads(my_json)

    # could add formatting options to generate pretty print
    # don't do that for this application
    #s = json.dumps(data, indent=4, sort_keys=True)

    s = json.dumps(data)
    if debug == 1:
        print("hello json data string")
        print(s)
        print("hello json data string")

    # convert to DataFrame as side effect, of transform 
    # to be used later to normalize values
    # and then add to ELK index stream
    df = pd.DataFrame.from_dict(data)

    # Debug lines, if needed for validation
    if debug == 1:
        print("DF****")
        print(df)
        print("****DF")

    # take out right bracket [
    s1 = s.replace('[', '') 
    if debug == 1:
        print("hello take out left bracket")
        print(s1)
        print("hello take out left bracket")
    
    # take out left bracket [ and add a newline; newline required for post to ELK
    s2 = s1.replace(']', '\n')
    if debug == 1:
        print("hello take out RIGHT bracket")
        print(s2)
        print("hello take out RIGHT bracket")
    
    # Replace index name from arg line into metadata 
    metadata = '\n{"index": {"_index":"' +  index_name + '"}}\n{'
    
    # insert metadata , metadata definition contains a newline
    s3 = s2.replace('{', metadata)
    if debug == 1:
        print("hello insert meta")
        print(s3)
        print("hello insert meta")
    
    # take out spaces ; minify
    s4 = s3.replace(' ', '')
    if debug == 1:
        print("hello remove spaces")
        print(s4)
        print("hello remove spaces")

    # remove comma at end of lines
    s5 = s4.replace('},', '}')
    if debug == 1:
        print("hello remove comma")
        print(s5)
        print("hello remove comma")

    # reassign transform to global lines
    lines = s5
    return lines


# bulk api will fail if there is no newline at end
# you can use curl to push file into elk
# see URL
# https://kb.objectrocket.com/elasticsearch/how-to-bulk-import-into-elasticsearch-using-curl
def post_tops_file(lines,dest_file):
    if debug == 1:
        print("hello write out file")
        print(lines)
        print("hello write out file")
        print(dest_file)

    with open(dest_file, 'w') as f:
        for each_line in lines:
            f.writelines(each_line)
        f.write('\n')

def main():
    # get args, tuple contains lines and either real or blank dest_file name
    lines_tuple = init_context()

    (lines, index_name, dest_file) = lines_tuple
    if debug == 1:
        print(index_name)
        print(dest_file)

    # issue IEX get tops endpoint
    # get_tops() is called inside init_context() now 
    # depending on nargs it either gets from curl IEX endpoint or is blank

    # transform from IEX json to ELK bulk api json format
    nlines = transform(lines,index_name)

    # POST transformed json to ELK localhost 
    if dest_file == "blank_dest_file":
        post_tops_elk(nlines,index_name)

    if dest_file != "blank_dest_file":
        post_tops_file(nlines,dest_file)

# 
# __name__
if __name__ == "__main__":
    main()

