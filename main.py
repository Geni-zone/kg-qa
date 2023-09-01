import time

from kg_gen import *
import kglab
import networkx as nx
from pyvis.network import Network
# from pyvis.options import Node
import networkx as nx
# import matplotlib.pyplot as plt
import networkx as nx
import pyvis.network as nt  # Assuming you have pyvis installed
from rdflib import URIRef, Literal, BNode
import PyPDF2


def main(text: str):

    entities = entity_extract(text)
    # print(entities)
    # entities = {'Barbara Wilson': {'description': 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.', 'types': ['person']}, 'UIUC': {'description': 'UIUC is an abbreviation for the University of Illinois at Urbana-Champaign.', 'types': ['organization', 'place']}}
    kg, all_triplets, predicates = predicate_extract(text=text, entities=entities)
    # print('entities: ', entities)
    # print('kg: ', kg)
    # print('all_triplets: ', all_triplets)
    # print('predicates: ', predicates)
    # kg = {'Barbara Wilson': [['Barbara Wilson', 'has/is_Chancellor_of', 'Chancellor_of_Relation'], ['Chancellor_of_Relation', 'has_start_date', '2015'], ['Chancellor_of_Relation', 'has_end_date', '2016'], ['Chancellor_of_Relation', 'has_value', 'UIUC']], 'UIUC': [['UIUC', 'has/is_Chancellor', 'Chancellor_Relation'], ['Chancellor_Relation', 'has_start_date', '2015-2016'], ['Chancellor_Relation', 'has_value', 'Barbara Wilson']]}
    # all_triplets = {'ete_triplets': [['Barbara Wilson', 'has/is_Chancellor_of', 'Chancellor_of_Relation'], ['UIUC', 'has/is_Chancellor', 'Chancellor_Relation']], 'etl_triplets': [['Chancellor_of_Relation', 'has_start_date', '2015'], ['Chancellor_of_Relation', 'has_end_date', '2016'], ['Chancellor_of_Relation', 'has_value', 'UIUC'], ['Chancellor_Relation', 'has_start_date', '2015-2016'], ['Chancellor_Relation', 'has_value', 'Barbara Wilson']]}
    # predicates = {'Chancellor_of_Relation': {'description': 'Barbara Wilson is the Chancellor of UIUC', 'source': 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.', 'data_properties': {'start_date': ['2015', 'date'], 'end_date': ['2016', 'date']}}, 'Chancellor_Relation': {'description': 'The relation "Chancellor" describes the position held by an individual at UIUC.', 'source': 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.', 'data_properties': {'start_date': ['2015-2016', 'string']}}}
    # only_triplets = []
    # for entity_name, entity_triplets in kg.items():
    #     only_triplets += entity_triplets

    # print('only_triplets: ', only_triplets)



    # # Create your Knowledge Graph
    # kg = kglab.KnowledgeGraph()
    # entity_to_entity = [
    #     [URIRef("http://www.examples.com/Barbara Wilson"), URIRef("http://www.examples.com/has/is_Chancellor_of"), URIRef("http://www.examples.com/Chancellor_of_Relation")], 
    #     [URIRef("http://www.examples.com/UIUC"), URIRef("http://www.examples.com/has/is_Chancellor"), URIRef("http://www.examples.com/Chancellor_Relation")]
    # ]
    # for triplet in entity_to_entity:
    #     kg.add(triplet[0], triplet[1], triplet[2])
    # entity_to_literal = [
    #     [URIRef("http://www.examples.com/haha/21/Chancellor_of_Relation"), URIRef("http://www.examples.com/haha/21/has_start_date"), Literal('2015')], 
    #     [URIRef("http://www.examples.com/haha/21/Chancellor_of_Relation"), URIRef("http://www.examples.com/haha/21/has_end_date"), Literal('2016')], 
    #     [URIRef("http://www.examples.com/haha/21/Chancellor_of_Relation"), URIRef("http://www.examples.com/haha/21/has_value"), URIRef("http://www.examples.com/haha/21/UIUC")], 
    #     [URIRef("http://www.examples.com/haha/21/UIUC"), URIRef("http://www.examples.com/haha/21/has/is_Chancellor"), URIRef("http://www.examples.com/haha/21/Chancellor_Relation")],     
    #     [URIRef("http://www.examples.com/haha/21/Chancellor_Relation"), URIRef("http://www.examples.com/haha/21/has_start_date"), Literal('2015-2016')], 
    #     [URIRef("http://www.examples.com/haha/21/Chancellor_Relation"), URIRef("http://www.examples.com/haha/21/has_value"), URIRef("http://www.examples.com/haha/21/Barbara Wilson")]
    # ]
    # for triplet in entity_to_literal:
    #     kg.add(triplet[0], triplet[1], triplet[2])








    # # serialize as a Turtle (ttl) file
    # ttl_path = "kg.ttl"
    # kg.save_ttl(ttl_path)


def visualize(list1, list2, name):
    import networkx as nx

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges from both lists
    for i in range(len(list2)):
        list2[i][2] = f'l({list2[i][2]})'
    for triplet in list1 + list2:
        node1, label, node2 = triplet
        G.add_edge(node1, node2, label=label)

    # Create a Network instance
    nt_graph = nt.Network(height="1000px", width="100%", bgcolor="#ffffff", font_color="white")

    # Add nodes to the NetworkX graph
    for node in G.nodes():
        label = str(node)
        color = "blue" if label.startswith("l(") else "black"
        shape = "box" if color == "blue" else "ellipse"
        nt_graph.add_node(label, label=label, color=color, shape=shape)

    # Use a different layout algorithm with adjustable parameters
    pos = nx.spring_layout(G, k=0.1)  # Adjust the 'k' parameter to control the force

    # Add edges to the NetworkX graph
    for u, v in G.edges():
        label = G[u][v]['label']
        nt_graph.add_edge(str(u), str(v), title=label)

    # Show the graph in an HTML file
    nt_graph.write_html(name)



if __name__ == '__main__':
    start_time = time.time()
    # text = 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.'
    # list1 = [['Barbara Wilson', 'has/is_Chancellor_of', 'Chancellor_of_Relation'], ['UIUC', 'has/is_Chancellor', 'Chancellor_Relation']]
    # list2 = [['Chancellor_of_Relation', 'has_start_date', 'l(2015)'], ['Chancellor_of_Relation', 'has_end_date', 'l(2016)'], ['Chancellor_of_Relation', 'has_value', 'l(UIUC)'], ['UIUC', 'has/is_Chancellor', 'Chancellor_Relation'], ['Chancellor_Relation', 'has_start_date', 'l(2015-2016)'], ['Chancellor_Relation', 'has_value', 'l(Barbara Wilson)']]

    pdf_path = ['paper/NT/volume_209_2023/issue_1/Explanation of Deep Learning Based Radioisotope Identifier for Plastic Scintillation Detector.pdf', 'paper/NT/volume_209_2023/issue_1/Fuel Melting Simulation with FRAPCON FRAPTRAN Codes for the Power to Melt and Maneuverability Simulation Exercise and Consideration of Model.pdf']
    text = 'Nuclear power is the use of nuclear reactions to produce electricity. Nuclear power can be obtained from nuclear fission, nuclear decay and nuclear fusion reactions. Presently, the vast majority of electricity from nuclear power is produced by nuclear fission of uranium and plutonium in nuclear power plants. Nuclear decay processes are used in niche applications such as radioisotope thermoelectric generators in some space probes such as Voyager 2. Generating electricity from fusion power remains the focus of international research.\n\nMost nuclear power plants use thermal reactors with enriched uranium in a once-through fuel cycle. Fuel is removed when the percentage of neutron absorbing atoms becomes so large that a chain reaction can no longer be sustained, typically three years. It is then cooled for several years in on-site spent fuel pools before being transferred to long term storage. The spent fuel, though low in volume, is high-level radioactive waste. While its radioactivity decreases exponentially it must be isolated from the biosphere for hundreds of thousands of years, though newer technologies (like fast reactors) have the potential to reduce this significantly. Because the spent fuel is still mostly fissionable material, some countries (e.g. France and Russia) reprocess their spent fuel by extracting fissile and fertile elements for fabrication in new fuel, although this process is more expensive than producing new fuel from mined uranium. All reactors breed some plutonium-239, which is found in the spent fuel, and because Pu-239 is the preferred material for nuclear weapons, reprocessing is seen as a weapon proliferation risk.\n\nThe first nuclear power plant was built in the 1950s. The global installed nuclear capacity grew to 100 GW in the late 1970s, and then expanded rapidly during the 1980s, reaching 300 GW by 1990. The 1979 Three Mile Island accident in the United States and the 1986 Chernobyl disaster in the Soviet Union resulted in increased regulation and public opposition to nuclear plants. These factors, along with high cost of construction, resulted in the global installed capacity only increasing to 390 GW by 2022. These plants supplied 2,586 terawatt hours (TWh) of electricity in 2019, equivalent to about 10% of global electricity generation, and were the second-largest low-carbon power source after hydroelectricity. As of August 2023, there are 410 civilian fission reactors in the world, with overall capacity of 369 GW,[1] 57 under construction and 102 planned, with a combined capacity of 59 GW and 96 GW, respectively. The United States has the largest fleet of nuclear reactors, generating almost 800 TWh of low-carbon electricity per year with an average capacity factor of 92%. Average global capacity factor is 89%.[1] Most new reactors under construction are generation III reactors in Asia.'
    # \n\nNuclear power generation causes one of the lowest levels of fatalities per unit of energy generated compared to other energy sources. Coal, petroleum, natural gas and hydroelectricity each have caused more fatalities per unit of energy due to air pollution and accidents. Nuclear power plants emit no greenhouse gases. One of the dangers of nuclear power is the potential for accidents like the Fukushima nuclear disaster in Japan in 2011.\n\nThere is a debate about nuclear power. Proponents contend that nuclear power is a safe, sustainable energy source that reduces carbon emissions. The anti-nuclear movement contends that nuclear power poses many threats to people and the environment and is too expensive and slow to deploy when compared to alternative sustainable energy sources.'
    # \n\nOrigins\n\nThe first light bulbs ever lit by electricity generated by nuclear power at EBR-1 at Argonne National Laboratory-West, December 20, 1951.[2]\n\nThe discovery of nuclear fission occurred in 1938 following over four decades of work on the science of radioactivity and the elaboration of new nuclear physics that described the components of atoms. Soon after the discovery of the fission process, it was realized that a fissioning nucleus can induce further nucleus fissions, thus inducing a self-sustaining chain reaction.[3] Once this was experimentally confirmed in 1939, scientists in many countries petitioned their governments for support of nuclear fission research, just on the cusp of World War II, for the development of a nuclear weapon.[4]\n\nIn the United States, these research efforts led to the creation of the first man-made nuclear reactor, the Chicago Pile-1, which achieved criticality on December 2, 1942. The reactor\'s development was part of the Manhattan Project, the Allied effort to create atomic bombs during World War II. It led to the building of larger single-purpose production reactors for the production of weapons-grade plutonium for use in the first nuclear weapons. The United States tested the first nuclear weapon in July 1945, the Trinity test, with the atomic bombings of Hiroshima and Nagasaki taking place one month later.\n\nThe launching ceremony of the USS Nautilus January 1954. In 1958 it would become the first vessel to reach the North Pole.[5]\n\nThe Calder Hall nuclear power station in the United Kingdom, the world\'s first commercial nuclear power station.\n\nDespite the military nature of the first nuclear devices, the 1940s and 1950s were characterized by strong optimism for the potential of nuclear power to provide cheap and endless energy.[6] Electricity was generated for the first time by a nuclear reactor on December 20, 1951, at the EBR-I experimental station near Arco, Idaho, which initially produced about 100 kW.[7][8] In 1953, American President Dwight Eisenhower gave his "Atoms for Peace" speech at the United Nations, emphasizing the need to develop "peaceful" uses of nuclear power quickly. This was followed by the Atomic Energy Act of 1954 which allowed rapid declassification of U.S. reactor technology and encouraged development by the private sector.\n\nFirst power generation\n\nThe first organization to develop practical nuclear power was the U.S. Navy, with the S1W reactor for the purpose of propelling submarines and aircraft carriers. The first nuclear-powered submarine, USS Nautilus, was put to sea in January 1954.[9][10] The S1W reactor was a pressurized water reactor. This design was chosen because it was simpler, more compact, and easier to operate compared to alternative designs, thus more suitable to be used in submarines. This decision would result in the PWR being the reactor of choice also for power generation, thus having a lasting impact on the civilian electricity market in the years to come.[11]\n\nOn June 27, 1954, the Obninsk Nuclear Power Plant in the USSR became the world\'s first nuclear power plant to generate electricity for a power grid, producing around 5 megawatts of electric power.[12] The world\'s first commercial nuclear power station, Calder Hall at Windscale, England was connected to the national power grid on 27 August 1956. In common with a number of other generation I reactors, the plant had the dual purpose of producing electricity and plutonium-239, the latter for the nascent nuclear weapons program in Britain.[13]'
    # text = 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.'
    # for path in pdf_path:
    #     with open(path, 'rb') as pdf_file:
    #         # Create a PdfReader object
    #         pdf_reader = PyPDF2.PdfReader(pdf_file)

    #         # Loop through each page in the PDF
    #         for page_num in range(len(pdf_reader.pages)):
    #             page = pdf_reader.pages[page_num]
    #             text += page.extract_text()
            
    #         text += '\n\n\n\n'
    print('text length: ', len(text))
    # text_chunks = split_text(text)
    text_chunks = ['Nuclear power is the use of nuclear reactions to produce electricity.', 'Nuclear power can be obtained from nuclear fission, nuclear decay and nuclear fusion reactions.', 'Presently, the vast majority of electricity from nuclear power is produced by nuclear fission of uranium and plutonium in nuclear power plants.', 'Nuclear decay processes are used in niche applications such as radioisotope thermoelectric generators in some space probes such as Voyager 2. Generating electricity from fusion power remains the focus of international research.', 'Most nuclear power plants use thermal reactors with enriched uranium in a once-through fuel cycle.']
    # text_chunks = [text]
    all_kg = {}
    all_entities = {}
    final_all_triplets = {'ete_triplets': [], 'etl_triplets': []}
    all_predicates = {}
    count = 0
    for text_chunk in text_chunks:
        print('count: ', count)
        # try:
        entities, ent_token_used = entity_extract(text_chunk)
        all_entities.update(entities)
        kg, all_triplets, predicates, rel_token_used = predicate_extract(text=text_chunk, entities=entities)
        all_kg.update(kg)
        final_all_triplets['ete_triplets'] += all_triplets['ete_triplets']
        final_all_triplets['etl_triplets'] += all_triplets['etl_triplets']
        all_predicates.update(predicates)
        print('\n\ntotal tokens used: ', ent_token_used + rel_token_used)
        # if count >= 1:
        #     break
        # else:
        #     count += 1
        # except Exception as e:
        #     print(e)
        #     print(f'Error while processing chunk. Skipping...\ntext_chunk: {text_chunk}')
        #     continue
        count += 1
    print('final_all_triplets: ', final_all_triplets)
    visualize(list1=final_all_triplets['ete_triplets'], list2=final_all_triplets['etl_triplets'], name='two_papers.html')





    end_time = time.time()
    print(f"Time elapsed: {end_time - start_time} seconds")