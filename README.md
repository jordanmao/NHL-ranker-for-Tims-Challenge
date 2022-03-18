# NHL-ranker-for-Tims-Challenge
The Tim Hortons Hockey Challenge is an app where users are given 3 lists of hockey players everyday, in which they select a player from each list. If a selected player scores, the user earns points, which can be redeemed for Tim Hortons goods!

This objective of this project is to obtain the data about the players playing each day and rank them based on different stats. This gives the user an organized platform to view player stats in order to make the informed selections.

The webscraper.py program uses Selenium to scrape https://timmies.zorbane.com/ to obtain the 3 lists of players available for selection. 

The main.py program parses the NHL API in JSON format to get the stats for all the players in the 3 lists. The data is then organized in classes to use in sorting by different stats. 

References:
The API links used were found in https://github.com/dword4/nhlapi
