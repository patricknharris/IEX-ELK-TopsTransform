# IEX-ELK-TopsTransform
Transform IEX ( https://api.iextrading.com/1.0/tops ) Tops API endpoint will only work during marketplace trading hours; 
otherwise it returns a 
"[]"
Null List.
Simple curl at a Linux prompt will retrieve the tops endpoint response into the json file.
curl 'https://api.iextrading.com/1.0/tops' >  IEX-ELK-Transform.json

The python code requires the following modules:
import json
import pandas as pd
import pycurl
import requests
import sys
from io import BytesIO

To retrieve these utilize the command:
pip install json pandas pycurl requests

Typing with no command line args, prints the "usage"; also see related screenshot checked in to repo, named iex-elk.py usage.
python iex-elk.py
Usage:
['iex-elk.py']
usage: python iex-elk.py ELK-index_name  
or usage: python iex-elk.py ELK-index_name src_file
or usage: python iex-elk.py ELK-index_name src_file dest_file

The 1st usage example: 
    python iex-elk.py ELK-index_name 
queries and retrieves TOPS endpoint and pushes JSON response into ELK localhost, if ELK not running and exception will return reminder to start ELK

The 2nd usage example: 
    python iex-elk.py ELK-index_name src_file
Reads a previously captured IEX Tops (possibly obtained from curl) 
and pushes IEX JSON response into ELK localhost, if ELK not running and exception will return reminder to start ELK

The 3rd usage example: 
    python iex-elk.py ELK-index_name src_file_name dest_file_name
Reads a previously captured IEX Tops (possibly obtained from curl) 
and pushes IEX JSON response into the dest_file_name

The ELK Mapping is noted below. 
If you push this response without the mapping the "date" fields will be interpreted as "longs", then not suitable for date / timestamp fields.
In Kibana, the Dev Tools ( https://www.elastic.co/guide/en/kibana/current/console-kibana.html ) embedded command console enables creating index and mapping - found on left hand side of Kibana interface, see below screen shot files in github.  The index name below is "stocks1" that must match the index-name utilized in the command line invocation. 
PUT /stocks1
{
  "mappings": {
      "properties": {
        "askPrice": {
          "type": "float"
        },
        "askSize": {
          "type": "long"
        },
        "bidPrice": {
          "type": "float"
        },
        "bidSize": {
          "type": "long"
        },
        "lastSalePrice": {
          "type": "float"
        },
        "lastSaleSize": {
          "type": "long"
        },
        "lastSaleTime": {
          "type": "date",
          "format": "epoch_millis"
        },
        "lastUpdated": {
          "type": "date",
          "format": "epoch_millis"
        },
        "marketPercent": {
          "type": "long"
        },
        "sector": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "securityType": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "symbol": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "volume": {
          "type": "long"
        }
      }
    }
  }

( https://kb.objectrocket.com/elasticsearch/how-to-delete-an-index-in-elasticsearch-using-kibana )
DELETE /stocks1

Tops Json output to ELK Bulk API json. Depending on command lines args get from file, or the endpoing then push to ELK localhost or file.
The various options enables ease of testing without live link.
Currently this endpoint is free without need for an API_Token.  Please review https://iexcloud.io/ ; Please attribute IEX, as it is a condition of use.  

https://iexcloud.io/disclaimers/
https://iexcloud.io/terms/ 
https://intercom.help/iexcloud/en/articles/2956555-what-restrictions-are-placed-on-using-data-from-iex-cloud 

Summary Terms - Copied from IEX Website, Please review URL's above for complete "official terms":

"IEX Cloud Terms of Service – Summary of Key Terms
Please note that the summaries below were created to help IEX Cloud users understand some of the key terms. If you choose to use IEX Cloud, you are bound by the full Terms of Service and not these summaries:

Data Use: There are some important limitations on how you can use IEX Cloud Data:

Paid Tier Plans: You may use IEX Cloud Data for commercial purposes through internal use or by displaying the data to third parties. You may not distribute IEX Cloud Data programmatically as a data feed, an API, or an export file.
Legacy Subscription Tiers
Free Tier Plans: You may use IEX Cloud Data for personal, non-commercial purposes only. You may not display or distribute IEX Cloud Data to third parties in any manner, and you may not use IEX Cloud Data for commercial purposes."


This code pushs to ELK localhost, enabling personal research usage; a paid plan is required before anything further.  ELK timestamps resolve to millisecond accuracy.  InfluxDB's timestamps resolve to nanosecond accuracy.  ELK was chosen as it's visualization capabilities via Kibana are equivalent or surpass other common visualization toolsets.  

Currently this module does not utilize Eland ( https://eland.readthedocs.io/en/7.10.1b1/index.html# ), a well written python api to elasticsearch enabling Gets/Puts by time or other filters, and the possibilty of machine learning processing.  This code contains a "transform" method that generates a Panda DataFrame with comments about TBD data normalization often required before applying ML processing.  Intent is to "normalize" and apply simple ML then add to BULK ELK api stream in order to validate, visualize and predict stock price attributes.  

