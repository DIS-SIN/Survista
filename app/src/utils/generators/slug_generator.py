from neomodel import StructuredNode
import random
SLUG_ANIMALS = [
    "alligator","ant",
    "bear",
    "bee",
    "bird","camel","cat","cheetah","chicken",
    "chimpanzee","cow","crocodile","deer","dog"
    ,"dolphin","duck","eagle","elephant","fish","fly"
    ,"fox","frog","giraffe","goat","goldfish","hamster",
    "hippopotamus","horse","kangaroo","kitten","lion","lobster","monkey",
    "octopus","owl","panda","pig","puppy","rabbit",
    "rat","scorpion","seal","shark","sheep","snail","snake","spider","squirrel","tiger",
    "turtle","wolf","zebra"
]
SLUG_ANIMALS_LEN = len(SLUG_ANIMALS)
SLUG_COLOURS = [
"black","blue","brown","gray","green","orange","pink","purple","red","white","yellow"
]
SLUG_COLOURS_LEN = len(SLUG_COLOURS)
SLUG_JOBS = [
"accountant","actor","actress","athlete","author","baker",
"banker","barber","beautician","broker","burglar","butcher",
"carpenter","chauffeur","chef","clerk","coach","craftsman",
"criminal","crook","dentist","doctor","editor","engineer",
"farmer","fire-fighter","fisherman","judge","lawyer","magician",
"mechanic","musician","nurse","pharmacist","pilot","poet","policeman",
"politician","printer","professor","rabbi","priest","pastor","sailor",
"salesman","shoemaker","soldier","tailor","teacher","veterinarian","waiter",
"waitress","watchmaker"
]
SLUG_JOBS_LEN = len(SLUG_JOBS)
def generate_slug(suffix: str, model: StructuredNode) -> str:
    unique = False
    while unique is False:
        colour = SLUG_COLOURS[random.randint(0, SLUG_COLOURS_LEN)]
        animal_1 = SLUG_ANIMALS[random.randint(0, SLUG_ANIMALS_LEN)]
        animal_2 = SLUG_ANIMALS[random.randint(0, SLUG_ANIMALS_LEN)]
        job = SLUG_JOBS[random.randint(0, SLUG_ANIMALS_LEN)]
        slug = "_".join([colour,animal_1,animal_2,job,suffix])

        node_with_slug = model.nodes.get_or_none(
            slug = slug
        )
        if node_with_slug is None:
            unique = True
    return slug   





