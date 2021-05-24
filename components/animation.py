import pygame as pg

# ? Animations !

# ? La base de données d'animations s'occupe de répertorier les images des animations,
# * Format : {'path': Surface}
# * Exemple : {'./assets/textures/player/idle/idle_0': <Surface(32x40x32 SW)>}
global animation_database
animation_database = {}

# ? La base de données supérieure s'occupe de répertorier les séquences d'un type d'animation, qui peut être composé de plusieurs ensembles d'animations
# ? Pour l'animation "idle" du joueur, la base de données stocke les surfaces de animation_database
# ? Et les répète le nombre de fois qu'une frame dans un type d'animation doit être affichée
# ? (Renseigné dans assets/textures/animations.txt)
# * Format : {'entity': {'animation_type': [[set1_animations1, ...], [set1_tag1] ...]}}
# * Exemple : {'player': {'idle': [['./assets/textures/player/idle/idle_0', ...], ['loop'] ...]}}
global animation_higher_database
animation_higher_database = {}


def animation_sequence(sequence, base_path):
    global animation_database
    result = []
    for frame in sequence:
        image_id = "{}/{}_{}".format(base_path,
                                     base_path.split("/")[-1], frame[0])
        # * Exemple : ./assets/textures/player/idle/idle_0
        image = pg.image.load(image_id + '.png')

        animation_database[image_id] = image.copy()
        for i in range(frame[1]):
            result.append(image_id)
    return result


def get_frame(ID):
    global animation_database
    return animation_database[ID]


def load_animations(path):
    """
    ### Description
    Charge les animations spécifiés par le fichier animations.txt

    ### Arguments
    - path: `str` Chemin d'accès au fichier animations.txt 

    ### Fichier `animations.txt`
    `Format` : entity_type/animation_type sequence tags

    `Exemple` : player/idle 10,10,10,10 loop 
    """
    global animation_higher_database
    f = open(path + 'animations.txt', 'r')
    data = f.read()
    f.close()

    for animation in data.split('\n'):
        sections = animation.split(' ')
        animation_path = sections[0]
        entity_info = animation_path.split('/')
        entity_type = entity_info[0]
        animation_id = entity_info[1]

        timings = sections[1].split(",")
        tags = sections[2].split(",")

        sequence = []
        n = 0
        for timing in timings:
            sequence.append([n, int(timing)])
            n += 1

        anim_sequence = animation_sequence(sequence, path + animation_path)

        if entity_type not in animation_higher_database:
            animation_higher_database[entity_type] = {}

        animation_higher_database[entity_type][animation_id] = [
            anim_sequence.copy(), tags]