# pyDemonlistAPI
An python library that simply provides Global List API to your code

Developed by Karelskiy127 and [AdderTeam](https://t.me/adderteam)

## Requirements
You need requests, countryflag and logging libraries for correct lib work

And, of course you need good internet connection

## Documentation
### Player class
You can get any information about player in global by using this class:
```
from demonlist import Player
```
You can contact a specific user by their Global List nickname or by their id
```
player = Player('w3rty') # By nickname (only string)
player = Player(3641) # By id (only integer)
```
Values that you can get:
> id, place, score, country, username, hardest, badge, flag

For example:
```
print(player.place)
```
For 'w3rty' it returns 16

Also, you can get all records of player, or records in specific category, use this:
```
print(player.records(levelType='basic') # levelType here is records category, if you want get ALL records do not write this value
```
All level types:
> 'main', 'basic', 'extended', 'beyond', 'verified', 'progress'

### Country class
With this class you also can get some values, but for start you need to import it:
```
from demonlist import Country
```
And now you can get any information about country
```
country = Country('Venezuela') # ONLY string value
print(country.place)
```
You can get:
> flag, place, score

Also you can get every player in country by
```
country.players(display_mode='default')
```
display_mode is a setting that displays what you will receive.

'default' (or just ()) returns an string with all players

'list' returns a list object with all players and infomation about them

### Level class
You can get any level information using this class:
```
from demonlist import Level
level = Level('Acheron') # ONLY string value
```
Values that you can get:
> place, video, verifier, score, list_percent, creator, id

For example
```
print(level.creator)
```
For Acheron it returns 'Riot, Ryamu and more'

Also, you can get all records on specific level, by using this:
```
print(level.records(amount=True)) # For the total count of all records
print(level.records()) # For the string of 50 records
print(level.records(display_mode='list)) # For list-object of 50 records
```
**Warning**: Global List limits do not allow to display all records at once, therefore to display something from a certain offset there is an offset value

For example:
```
count = level.records(amount=True)
if count > 50:
 print(level.records())
 print(level.records(offset=50))
```
This simple code returns 100 records (or less, but more than 50) on level. You can edit it how you need

And you can get level position history by using level.history() func:
```
print(level.history(display_mode='list')) # If you want get a list obj of all changes
print(level.history()) # Returns default string
```

### Top functions (players and future/classics lists)
You can get top of players and levels lists by using this:
```
from demonlist import level_list, players_ranking
```
Let's start with level_list:
```
print(level_list(display_mode='list', offset=50)) # Returns a list obj of 51-100 levels in top.
# If you want string do not write display_mode value, if you want 50 levels from the beginning of the top do not write offset.
# You can change offset how you want (for example: offset=100 returns 101-150 levels)
print(level_list(as_names=True)) # Returns list obj with levels names. You can only specify offset along with this value.
print(level_list(type='future')) # Returns future list as a string. If you want list object, add display_mode='list'. THIS PARAMETER DO NOT SUPPORT OFFSET/AS_NAMES!!!
```
And now, players_ranking:
```
print(players_ranking(display_mode='list', offset=50)) # Returns a list obj with 51-100 players in top.
# If you want string do not write display_mode value, if you want 50 players from the beginning of the top do not write offset.
```

## That's all!
At the moment these are all the functions present in the library. The library is still raw, but you can already use it. About bugs, write to me in telegram: @karelskiy127, or discord: karjalan
