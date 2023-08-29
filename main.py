import time

from kg_gen import *


def main(text: str):

    entities = entity_extract(text)
    # print(entities)
    # entities = {
    #     "Barbara Wilson": {
    #         "description": "Barbara Wilson is the Chancellor of UIUC at 2015-2016.",
    #         "types": ["person"]
    #     },
    #     "UIUC": {
    #         "description": "UIUC is an abbreviation for the University of Illinois at Urbana-Champaign.",
    #         "types": ["organization", "place"]
    #     }
    # }
    kg, predicates = predicate_extract(text=text, entities=entities)
    print(kg)
    print(predicates)


if __name__ == '__main__':
    start_time = time.time()

    t = 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.'
    main(t)



    end_time = time.time()
    print(f"Time elapsed: {end_time - start_time} seconds")