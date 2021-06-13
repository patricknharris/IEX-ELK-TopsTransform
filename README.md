# IEX-ELK-TopsTransform
Transform IEX ( https://api.iextrading.com/1.0/tops ) Tops Json output to ELK Bulk API json. Depending on command lines args push to ELK localhost or file.
Currently this endpoint is free without need for an API_Token.  Please review https://iexcloud.io/ ; Please attribute IEX, as it is a condition of use

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

