import copy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from source.orm import *
from source.keywords import phases
import os.path


class Constructor:
    def __init__(self, name):
        self.new = True
        self.overwrite = 'n'
        if os.path.isfile('source/db/{}.db'.format(name)):
            self.new = False
            self.overwrite = input('Database already exists. Overwrite? (y/n)')
            if self.overwrite == 'y':
                os.remove('source/db/{}.db'.format(name))
        if not os.path.isfile('source/db/core.db'.format(name)):
            self.coreEngine = create_engine('sqlite+pysqlite:///source/db/core.db', echo=True)
            Base.metadata.create_all(self.coreEngine)
        else:
            self.coreEngine = create_engine('sqlite+pysqlite:///source/db/core.db', echo=True)
        coreDBSession = sessionmaker(bind=self.coreEngine)
        self.coreSession = coreDBSession()
        self.engine = create_engine('sqlite+pysqlite:///source/db/{}.db'.format(name), echo=True)
        dbSession = sessionmaker(bind=self.engine)
        self.session = dbSession()
        if self.new or self.overwrite == 'y':
            self.createDB()

    def createDB(self):
        Base.metadata.create_all(self.engine)
        self.session.add(Round(name='first'))
        self.session.add(Round(name='second'))
        self.session.add(Round(name='third'))
        self.session.add(Round(name='fourth'))
        self.session.add(Round(name='fifth'))
        self.session.add(Phase(name='command'))
        self.session.add(Phase(name='movement'))
        self.session.add(Phase(name='reserves'))
        self.session.add(Phase(name='psychic'))
        self.session.add(Phase(name='shooting'))
        self.session.add(Phase(name='charge'))
        self.session.add(Phase(name='combat'))
        self.session.add(Phase(name='morale'))
        self.session.add(WeaponType(name='assault', ability='Can shoot it when advanced with -1 to the hit roll'))
        self.session.add(WeaponType(name='rapid fire', ability='If target at half range of the weapon, double shoots'))
        self.session.add(WeaponType(name='heavy', ability='If moved and not vehicle, -1 to hit roll'))
        self.session.add(WeaponType(name='pistol', ability='Can shoot it while in engagement range'))
        self.session.add(WeaponType(name='grenade', ability='Only one model of the unit can shoot it per phase'))
        self.session.add(WeaponType(name='melee', ability='For close combat'))
        self.session.commit()

    def addSquad(self, squad):
        squad_ = Squad(name=squad.h4.text)
        abilities = []
        weapons = []
        modelTypes = []
        unique = False
        categories = [cat.lstrip() for cat in squad.find('p', class_='category-names').text.replace(squad.find('p', class_='category-names').find('span').text, '').replace('\n', '').replace('Faction:', '').split(', ')]
        rules = [rule.lstrip() for rule in squad.find('p', class_='rule-names').text.replace(squad.find('p', class_='rule-names').find('span').text, '').replace('\n', '').split(', ')]
        for table in squad.find_all('table'):
            if table.tr.th.text == 'Abilities':
                abilities = table.find_all('tr')[1:]
            if table.tr.th.text == 'Weapon':
                weapons = table.find_all('tr')[1:]
            if table.tr.th.text == 'Unit':
                modelTypes = table.find_all('tr')[1:]
        if 'selections' in squad.find('p').text.lower():
            unique = True
            models = [uni.lstrip() for uni in squad.find('p', class_='profile-names').find_all('span')[3].text.replace(squad.find('p', class_='profile-names').find('span').text, '').replace('\n', '').split(', ')]
        else:
            models = squad.find('ul').find_all('li') if squad.find('ul') else []
        for ability in abilities:
            ability1_ = self.coreSession.query(Ability).filter_by(name=ability.find_all('td')[0].text.lower()).first()
            if not ability1_:
                ability2_ = self.addAbility(ability=ability)
                squad_.abilities.append(ability2_)
            else:
                squad_.abilities.append(copy.deepcopy(ability1_))
        weapons2_ = []
        for weapon in weapons:
            weapon1_ = self.session.query(Weapon).filter_by(name=weapon.find_all('td')[0].text.lower()).first()
            if not weapon1_:
                weapons2_.append(self.addWeapon(weapon))
            else:
                weapons2_.append(copy.deepcopy(weapon1_))
        modelTypes = [Model(name=model.find_all('td')[0].text,
                            m=model.find_all('td')[1].text,
                            ws=model.find_all('td')[2].text,
                            bs=model.find_all('td')[3].text,
                            f=model.find_all('td')[4].text,
                            t=model.find_all('td')[5].text,
                            w=model.find_all('td')[6].text,
                            a=model.find_all('td')[7].text,
                            ld=model.find_all('td')[8].text,
                            sv=model.find_all('td')[9].text) for model in modelTypes]
        for model in models:
            for modelType in modelTypes:
                if modelType.name in model.h4.text if not unique else model:
                    model_ = self.session.query(Model).filter_by(name=model.h4.text if not unique else model).first()
                    if not model_:
                        model_ = copy.deepcopy(modelType)
                        model_.name = model.h4.text if not unique else model
                    if not unique:
                        selections = model.find('p', class_='profile-names')
                        wpIndex = [i for i, selection in enumerate(selections.find_all('span')) if 'weapon' in selection.text.lower()]
                        weapons = selections.find_all('span')[wpIndex[0] + 1].text.split(', ') if wpIndex else None
                    else:
                        weapons = [uni.lstrip() for uni in squad.find('p', class_='profile-names').find_all('span')[5].text.replace(squad.find('p', class_='profile-names').find('span').text, '').replace('\n', '').split(', ')]
                    if weapons:
                        for weapon in weapons:
                            weapon1_ = self.coreSession.query(Weapon).filter_by(name=weapon.lower()).first()
                            if not weapon1_:
                                weapon2_ = Weapon(name=weapon.lower())
                                model_.weapons.append(weapon2_)
                            else:
                                model_.weapons.append(copy.deepcopy(weapon1_))
                    squad_.models.append(model_)
        self.session.add(copy.deepcopy(squad_))
        self.session.commit()
        return self.session.query(Squad).all()

    def getSquads(self):
        return self.session.query(Squad).all()

    def addWeapon(self, weapon):
        ability_ = self.coreSession.query(Ability).filter_by(name=weapon.find_all('td')[0].text.lower()).first()
        if not ability_:
            ability_ = self.addAbility(abilityOrm=Ability(name=weapon.find_all('td')[0].text.lower(), description=weapon.find_all('td')[6].text.lower()))
        weapon_ = Weapon(name=weapon.find_all('td')[0].text.lower(),
                         r=weapon.find_all('td')[1].text,
                         type=weapon.find_all('td')[2].text,
                         s=weapon.find_all('td')[3].text,
                         ap=weapon.find_all('td')[4].text,
                         d=weapon.find_all('td')[5].text)
        weapon_.abilities.append(ability_)
        self.coreSession.add(weapon_)
        self.coreSession.commit()
        return copy.deepcopy(weapon_)

    def getWeapons(self):
        return self.session.query(Weapon).all()

    def addAbility(self, ability=None, abilityOrm=None):
        if not ability:
            self.coreSession.add(abilityOrm)
            self.coreSession.commit()
            return copy.deepcopy(abilityOrm)
        self.coreSession.add(Ability(name=ability.find_all('td')[0].text.lower(), description=ability.find_all('td')[1].text.lower()))
        self.coreSession.commit()
        return Ability(name=ability.find_all('td')[0].text.lower(), description=ability.find_all('td')[1].text.lower())

    def addAbilityMan(self):
        end = 'y'
        while end != 'n':
            print('Ability: Manual input \n')
            name = input('Name: ')
            if self.session.query(Ability).filter_by(name=name.lower()).first():
                print('The ability already exists')
            else:
                description = input('Description: ')
                phase = input('Phase: ')
                battleRound = input('Round: ')
                if phase == '':
                    phases_ = self.session.query(Phase).all()
                else:
                    phases_ = []
                    for ph in phase.split(', '):
                        phases_.append(self.session.query(Phase).filter_by(name=ph).first())
                if battleRound == '':
                    battleRounds = self.session.query(Round).all()
                else:
                    battleRounds = []
                    for rn in battleRound.split(', '):
                        battleRounds.append(self.session.query(Round).filter_by(name=rn).first())
                if phases_ and battleRounds:
                    ability_ = Ability(name=name, description=description, phases=phases_, rounds=battleRounds)
                    self.session.add(ability_)
                    self.session.commit()
                    print('Added Ability!')
                    end = input('Continue? (y/n):')
                else:
                    print('Bad phase or round')

    def getAbilities(self):
        return self.session.query(Ability).all()

    def getCoreAbilities(self):
        return self.coreSession.query(Ability).all()


class Parser:
    def __init__(self, roster):
        if roster == 'core':
            self.constructor = Constructor(roster)
        else:
            with open(roster) as fp:
                self.soup = BeautifulSoup(fp, 'html.parser')
            title = self.soup.find_all('h1')
            self.constructor = Constructor(title[0].text)
            if self.constructor.new or self.constructor.overwrite == 'y':
                categories = self.soup.find_all('li', class_='category')
                for category in categories:
                    name = category.h3.text
                    if 'Configuration' not in name:
                        squads = category.find_all('li', class_='rootselection')
                        for squad in squads:
                            self.constructor.addSquad(squad)
