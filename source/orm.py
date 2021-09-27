from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Relationships:
    model_weapon = Table(
        'model_weapon',
        Base.metadata,
        Column('model_id', Integer, ForeignKey('model.id')),
        Column('weapon_id', Integer, ForeignKey('weapon.id')),
    )
    model_squad = Table(
        'model_squad',
        Base.metadata,
        Column('model_id', Integer, ForeignKey('model.id')),
        Column('squad_id', Integer, ForeignKey('squad.id')),
    )
    squad_ability = Table(
        'squad_ability',
        Base.metadata,
        Column('squad_id', Integer, ForeignKey('squad.id')),
        Column('ability_id', Integer, ForeignKey('ability.id')),
    )
    weapon_ability = Table(
        'weapon_ability',
        Base.metadata,
        Column('weapon_id', Integer, ForeignKey('weapon.id')),
        Column('ability_id', Integer, ForeignKey('ability.id')),
    )
    ability_phase = Table(
        'ability_phase',
        Base.metadata,
        Column('ability_id', Integer, ForeignKey('ability.id')),
        Column('phase_id', Integer, ForeignKey('phase.id')),
    )
    ability_round = Table(
        'ability_round',
        Base.metadata,
        Column('ability_id', Integer, ForeignKey('ability.id')),
        Column('round_id', Integer, ForeignKey('round.id')),
    )
    rule_phase = Table(
        'rule_phase',
        Base.metadata,
        Column('rule_id', Integer, ForeignKey('rule.id')),
        Column('phase_id', Integer, ForeignKey('phase.id')),
    )
    rule_round = Table(
        'rule_round',
        Base.metadata,
        Column('rule_id', Integer, ForeignKey('rule.id')),
        Column('round_id', Integer, ForeignKey('round.id')),
    )
    army_squad = Table(
        'army_squad',
        Base.metadata,
        Column('army_id', Integer, ForeignKey('army.id')),
        Column('squad_id', Integer, ForeignKey('squad.id')),
    )
    keyword_squad = Table(
        'keyword_squad',
        Base.metadata,
        Column('keyword_id', Integer, ForeignKey('keyword.id')),
        Column('squad_id', Integer, ForeignKey('squad.id')),
    )
    army_rule = Table(
        'army_rule',
        Base.metadata,
        Column('army_id', Integer, ForeignKey('army.id')),
        Column('rule_id', Integer, ForeignKey('rule.id')),
    )
    army_ability = Table(
        'army_ability',
        Base.metadata,
        Column('army_id', Integer, ForeignKey('army.id')),
        Column('ability_id', Integer, ForeignKey('ability.id')),
    )


class Phase(Base):
    __tablename__ = 'phase'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abilities = relationship("Ability", secondary=Relationships.ability_phase, back_populates='phases')
    rules = relationship("Rule", secondary=Relationships.rule_phase, back_populates='phases')


class Round(Base):
    __tablename__ = 'round'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    abilities = relationship("Ability", secondary=Relationships.ability_round, back_populates='rounds')
    rules = relationship("Rule", secondary=Relationships.rule_round, back_populates='rounds')


class WeaponType(Base):
    __tablename__ = 'weaponType'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ability = Column(String)


class Faction(Base):
    __tablename__ = 'faction'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    squads = relationship('Squad', secondary=Relationships.keyword_squad, back_populates='keywords')


class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    m = Column(String)
    ws = Column(String)
    bs = Column(String)
    f = Column(String)
    t = Column(String)
    w = Column(String)
    a = Column(String)
    ld = Column(String)
    sv = Column(String)
    squads = relationship('Squad', secondary=Relationships.model_squad, back_populates='models')
    weapons = relationship('Weapon', secondary=Relationships.model_weapon, back_populates='models')


class Weapon(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    r = Column(String)
    s = Column(String)
    ap = Column(String)
    d = Column(String)
    type = Column(String, ForeignKey('weaponType.id'))
    abilities = relationship("Ability", secondary=Relationships.weapon_ability, back_populates='weapons')
    models = relationship("Model", secondary=Relationships.model_weapon, back_populates='weapons')


class Ability(Base):
    __tablename__ = 'ability'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    phases = relationship('Phase', secondary=Relationships.ability_phase, back_populates='abilities')
    rounds = relationship('Round', secondary=Relationships.ability_round, back_populates='abilities')
    squads = relationship('Squad', secondary=Relationships.squad_ability, back_populates='abilities')
    weapons = relationship('Weapon', secondary=Relationships.weapon_ability, back_populates='abilities')
    armies = relationship('Army', secondary=Relationships.army_ability, back_populates='abilities')


class Rule(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    phases = relationship('Phase', secondary=Relationships.rule_phase, back_populates='rules')
    rounds = relationship('Round', secondary=Relationships.rule_round, back_populates='rules')
    armies = relationship('Army', secondary=Relationships.army_rule, back_populates='rules')


class Squad(Base):
    __tablename__ = 'squad'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    keywords = relationship('Keyword', secondary=Relationships.keyword_squad, back_populates='squads')
    armies = relationship('Army', secondary=Relationships.army_squad, back_populates='squads')
    models = relationship('Model', secondary=Relationships.model_squad, back_populates='squads')
    abilities = relationship('Ability', secondary=Relationships.squad_ability, back_populates='squads')


class Army(Base):
    __tablename__ = 'army'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cp = Column(String)
    faction = Column(Integer, ForeignKey('faction.id'))
    rules = relationship('Rule', secondary=Relationships.army_rule, back_populates='armies')
    squads = relationship('Squad', secondary=Relationships.army_squad, back_populates='armies')
    abilities = relationship('Ability', secondary=Relationships.army_ability, back_populates='armies')
