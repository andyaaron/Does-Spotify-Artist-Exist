# How to use this script
You need two CSV files
- malicious-artists.csv - this is the list of artists in question we need to check against spotify
- updated-artists.csv - this is the results file that will record if the artist was found

Run the script via your IDE or terminal. While i do have the script output to a csv, i just use the print logs to see the search term used against the Spotify the api, and the artist result that was output. Currently i am only checking the first result, as that is the most likely outcome, but it is possible to retrieve more than 1 result from a search.
