from source import Parser

# parser = Parser('source/rosters/Death Guard - 50PL.html')
parser = Parser('source/rosters/Space Wolves - 20PL.html')
abilities = parser.constructor.getCoreAbilities()
parser.constructor.addAbilityMan()
squads = parser.constructor.getSquads()
abilities = parser.constructor.getAbilities()
weapons = parser.constructor.getWeapons()
f = 0
