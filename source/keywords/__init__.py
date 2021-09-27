phases = {
    # Restrictive
    'fight': 'combat',
    'melee': 'combat',
    'blast': 'shooting',
    'ranged attack': 'shooting',
    'command phase': 'command',
    'movement': 'movement',
    'deployment': 'before',
    'morale': 'morale',
    'attrition': 'morale',


    # Not restrictive
    'invulnerable save': ['psychic', 'shooting', 'combat'],
    'wound': ['movement', 'psychic', 'shooting', 'combat'],
    'attack': ['combat', 'shooting'],
    'hit roll': ['combat', 'shooting'],
}