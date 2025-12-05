test_record_type = 'digital_objects'
test_object_id = 1250203
test_object_repo_uri = '/repositories/11'
test_object_user_identifier = 'NMAI.AC.066.ref21.1'

test_digital_object_dates = {'lock_version': 1,
                             'digital_object_id': 'NMAI.AC.066.ref20',
                             'title': 'Articles of Agreement',
                             'publish': True,
                             'restrictions': False,
                             'created_by': 'admin',
                             'last_modified_by': 'admin',
                             'create_time': '2017-11-17T22:54:57Z',
                             'system_mtime': '2023-05-06T13:20:17Z',
                             'user_mtime': '2017-11-17T22:54:57Z',
                             'suppressed': False,
                             'is_slug_auto': False,
                             'jsonmodel_type': 'digital_object',
                             'external_ids': [
                                 {'external_id': '47780', 'source': 'Archivists Toolkit Database::DIGITAL_OBJECT',
                                  'created_by': 'admin', 'last_modified_by': 'admin',
                                  'create_time': '2017-11-17T22:54:57Z', 'system_mtime': '2017-11-17T22:54:57Z',
                                  'user_mtime': '2017-11-17T22:54:57Z', 'jsonmodel_type': 'external_id'}],
                             'subjects': [],
                             'linked_events': [],
                             'extents': [],
                             'lang_materials': [],
                             'dates': [
                                 {'lock_version': 0, 'expression': '1871', 'begin': '1871', 'end': '1871',
                                  'created_by': 'admin',
                                  'last_modified_by': 'admin', 'create_time': '2017-11-17T22:54:57Z',
                                  'system_mtime': '2017-11-17T22:54:57Z',
                                  'user_mtime': '2017-11-17T22:54:57Z', 'date_type': 'inclusive', 'label': 'creation',
                                  'jsonmodel_type': 'date'},
                                 {'lock_version': 0, 'expression': '2024', 'begin': '2024',
                                  'created_by': 'admin',
                                  'last_modified_by': 'admin', 'create_time': '2024-11-13T08:30:57Z',
                                  'system_mtime': '2024-11-13T08:30:57Z',
                                  'user_mtime': '2024-11-13T08:30:57Z', 'date_type': 'single', 'label': 'digitized',
                                  'jsonmodel_type': 'date'}],
                             'external_documents': [],
                             'rights_statements': [],
                             'linked_agents': [],
                             'file_versions': [{'lock_version': 0,
                                                'file_uri': 'https://edan.si.edu/slideshow/slideshowViewer.htm?damspath=/Public_Sets/NMAI/NMAI-AO-Assets-and-Operations/NMAI-AO-Archives/NMAI_AC066/Box_001/Folder_01',
                                                'publish': True, 'created_by': 'admin', 'last_modified_by': 'admin',
                                                'create_time': '2017-11-17T22:54:57Z',
                                                'system_mtime': '2021-08-15T18:47:25Z',
                                                'user_mtime': '2017-11-17T22:54:57Z', 'use_statement': 'image-service',
                                                'jsonmodel_type': 'file_version', 'is_representative': False,
                                                'identifier': '18'}],
                             'classifications': [],
                             'notes': [],
                             'linked_instances': [{'ref': '/repositories/12/archival_objects/65739'}],
                             'metadata_rights_declarations': [],
                             'content_warnings': [],
                             'uri': '/repositories/12/digital_objects/18',
                             'repository': {'ref': '/repositories/12'},
                             'tree': {'ref': '/repositories/12/digital_objects/18/tree'}}

test_digital_object_dates_deleted = {"lock_version": 1,
                                     "digital_object_id": "NMAI.AC.066.ref20",
                                     "title": "Articles of Agreement",
                                     "publish": True,
                                     "restrictions": False,
                                     "created_by": "admin",
                                     "last_modified_by": "admin",
                                     "create_time": "2017-11-17T22:54:57Z",
                                     "system_mtime": "2023-05-06T13:20:17Z",
                                     "user_mtime": "2017-11-17T22:54:57Z",
                                     "suppressed": False,
                                     "is_slug_auto": False,
                                     "jsonmodel_type": "digital_object",
                                     "external_ids": [
                                         {"external_id": "47780",
                                          "source": "Archivists Toolkit Database::DIGITAL_OBJECT",
                                          "created_by": "admin",
                                          "last_modified_by": "admin",
                                          "create_time": "2017-11-17T22:54:57Z",
                                          "system_mtime": "2017-11-17T22:54:57Z",
                                          "user_mtime": "2017-11-17T22:54:57Z",
                                          "jsonmodel_type": "external_id"}],
                             "subjects": [],
                             "linked_events": [],
                             "extents": [],
                             "lang_materials": [],
                             "dates": [],
                             "external_documents": [],
                             "rights_statements": [],
                             "linked_agents": [],
                             "file_versions": [
                                 {"lock_version": 0,
                                  "file_uri": "https://edan.si.edu/slideshow/slideshowViewer.htm?damspath=/Public_Sets/NMAI/NMAI-AO-Assets-and-Operations/NMAI-AO-Archives/NMAI_AC066/Box_001/Folder_01",
                                  "publish": True,
                                  "created_by": "admin",
                                  "last_modified_by": "admin",
                                  "create_time": "2017-11-17T22:54:57Z",
                                  "system_mtime": "2021-08-15T18:47:25Z",
                                  "user_mtime": "2017-11-17T22:54:57Z",
                                  "use_statement": "image-service",
                                  "jsonmodel_type": "file_version",
                                  "is_representative": False,
                                  "identifier": "18"}],
                             "classifications": [],
                             "notes": [],
                             "linked_instances": [{"ref": "/repositories/12/archival_objects/65739"}],
                             "metadata_rights_declarations": [],
                             "content_warnings": [],
                             "uri": "/repositories/12/digital_objects/18",
                             "repository": {"ref": "/repositories/12"},
                             "tree": {"ref": "/repositories/12/digital_objects/18/tree"}}

test_error_json = {
    "lock_version": 19,
    "digital_object_id": "NMAH.AC.0509.01",
    "title": "Brownie Wise Papers",
    "publish": True,
    "restrictions": False,
    "created_by": "admin",
    "last_modified_by": "oswalda",
    "create_time": "2017-11-17T22:58:34Z",
    "system_mtime": "2024-01-29T16:20:00Z",
    "user_mtime": "2020-06-04T11:33:21Z",
    "suppressed": False,
    "is_slug_auto": False,
    "jsonmodel_type": "digital_object",
    "external_ids": [
        {
            "external_id": "63919",
            "source": "Archivists Toolkit Database::DIGITAL_OBJECT",
            "created_by": "oswalda",
            "last_modified_by": "oswalda",
            "create_time": "2020-06-04T11:33:21Z",
            "system_mtime": "2020-06-04T11:33:21Z",
            "user_mtime": "2020-06-04T11:33:21Z",
            "jsonmodel_type": "external_id"
        }
    ],
    "subjects": [
        {"ref": "/subjects/10335"},
        {"ref": "/subjects/10365"},
        {"ref": "/subjects/41595"},
        {"ref": "/subjects/3103"},
        {"ref": "/subjects/2793"},
        {"ref": "/subjects/186"},
        {"ref": "/subjects/2016"},
        {"ref": "/subjects/3402"},
        {"ref": "/subjects/243"},
        {"ref": "/subjects/5181"}
    ],
    "linked_events": [],
    "extents": [],
    "lang_materials": [
        {
            "lock_version": 0,
            "create_time": "2017-11-17T22:58:34Z",
            "system_mtime": "2020-10-22T11:34:12Z",
            "user_mtime": "2020-06-04T11:33:21Z",
            "jsonmodel_type": "lang_material",
            "notes": [],
            "language_and_script": {
                "lock_version": 0,
                "create_time": "2017-11-17T22:58:34Z",
                "system_mtime": "2020-10-22T11:34:12Z",
                "user_mtime": "2020-06-04T11:33:21Z",
                "language": "eng",
                "jsonmodel_type": "language_and_script"
            }
        },
        {
            "lock_version": 0,
            "create_time": "2020-06-04T11:33:21Z",
            "system_mtime": "2020-06-04T11:33:21Z",
            "user_mtime": "2020-06-04T11:33:21Z",
            "jsonmodel_type": "lang_material",
            "notes": [
                {
                    "jsonmodel_type": "note_digital_object",
                    "persistent_id": "a96896bc835da8a795b39de086abb73b",
                    "type": "langmaterial",
                    "content": ["Collection is in English."],
                    "publish": True
                }
            ]
        }
    ],
    "dates": [
        {
            "lock_version": 0,
            "expression": "circa 1938-1968",
            "begin": "1938",
            "end": "1968",
            "created_by": "oswalda",
            "last_modified_by": "oswalda",
            "create_time": "2020-06-04T11:33:21Z",
            "system_mtime": "2020-06-04T11:33:21Z",
            "user_mtime": "2020-06-04T11:33:21Z",
            "date_type": "inclusive",
            "label": "creation",
            "jsonmodel_type": "date"
        }
    ],
    "external_documents": [],
    "rights_statements": [],
    "linked_agents": [
        {
            "role": "subject",
            "terms": [],
            "ref": "/agents/corporate_entities/3012"
        },
        {
            "role": "subject",
            "terms": [],
            "ref": "/agents/corporate_entities/60959"
        },
        {
            "role": "creator",
            "relator": "inv",
            "terms": [],
            "ref": "/agents/people/49791"
        },
        {
            "role": "subject",
            "terms": [],
            "ref": "/agents/corporate_entities/28856"
        }
    ],
    "file_versions": [
        {
            "lock_version": 0,
            "file_uri": "https://ids.si.edu/ids/deliveryService?id=NMAH-AC0509-0000084",
            "publish": True,
            "created_by": "oswalda",
            "last_modified_by": "oswalda",
            "create_time": "2020-06-04T11:33:21Z",
            "system_mtime": "2020-06-04T11:33:21Z",
            "user_mtime": "2020-06-04T11:33:21Z",
            "use_statement": "representative-image",
            "jsonmodel_type": "file_version",
            "is_representative": False,
            "identifier": "812351"
        }
    ],
    "classifications": [],
    "notes": [
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "a6d1cdc1b8dcfe069005a23f8c0a32a4",
            "type": "prefercite",
            "content": ["Brownie Wise Papers, 1938-1968, Archives Center, National Museum of American History"],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "2063276b00f7eeab912b999768845257",
            "type": "acqinfo",
            "content": ["The collection was donated to the Archives Center, National Museum of American History in March 1994 by Brownie Wise's son, Jerry Wise, of Kissimmee, Florida."],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "1f481257cd49eb87cb05770fb4248e0b",
            "type": "processinfo",
            "content": ["Processed by Mimi Minnick, July 1995.\n"],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "4be4bad59a2a5963080644cbcc6002a1",
            "label": "Biographical Note",
            "type": "bioghist",
            "content": ["Brownie Humphrey was born in Buford, Georgia in 1913, the daughter of Rosabelle Stroud Humphrey and Jerome Humphrey, a plumber.   According to longtime friend Kay Robinson, Brownie knew that there were few business opportunities for women in the South, and that \"unless she wanted to work in sales, she would have to leave the South.\"  After meeting Robert Wise at the Texas Centennial in 1936, where the couple saw an exhibition highlighting a bright future at Ford Motors, Brownie and Robert married and moved to the Detroit area where he worked as a machinist, later opening a small machine shop. The couple divorced in 1941, about three years after the birth of their only child, Jerry. Brownie Wise never remarried.\n\nDuring the late 1930s and early 1940s, Brownie contributed to a correspondence column of the Detroit News under the pen name \"Hibiscus.\"  Her columns were largely autobiographical, but used elements of fantasy and romance to address a uniquely female urban community.  In  Detroit, Wise worked briefly at an ad agency and in a millinery shop.  During World War II, Wise got a job as an executive secretary at Bendix.  After the war, Brownie and her mother, Rose Stroud Humphrey, began selling Stanley Home Products.  When Jerry became ill in 1949, they followed a doctor's advice and moved to Miami where they began a direct selling business they called Patio Parties. Through this  business, the mother daughter team distributed Poly-T (Tupperware), Stanley Home Products, West Bend, and other household goods through an innovative home party plan adopted by Brownie.  \n\nThomas Damigella in Massachusetts, and Brownie Wise in South Florida, quickly became among the fastest movers of Tupperware products, attracting the attention of Earl Tupper, who was still searching for a profitable outlet for his plastic containers.  Because Americans were still skeptical of plastics and because the Tupper seal required demonstration, early attempts at department store sales had been unsuccessful.  Some independent dealers had more success selling through demonstrations at state fairs or door-to-door, but sales and distribution remained low.  The experiences of Damigella and Wise convinced Tupper to offer the products on a home party plan.  He partnered with Norman Squires, the originator of Hostess Home Parties, to pursue this strategy. \n\nIn 1951, Tupper recruited Brownie to develop the Hostess party plan for Tupperware, and named her vice president of the company.   She is credited with developing the party plan and sales organization, and with creating the annual Jubilee, a pep-rally and awards ceremony for dealers and distributors; it was her idea to locate company headquarters in Kissimmee, and she oversaw the design and construction of the campus.  With the company's meteoric success came national recognition. Her public role was all the greater because Earl Tupper shunned all public exposure; Wise was the public head of the company throughout the 1950s.  She was both honored guest and invited speaker at national sales and marketing conferences, where she was often the only woman in attendance.  Scores of laudatory articles about her appeared in the sales industry and general business press, and she became the darling of the women's magazines, including features in McCalls, Charm and Companion.\n\nTupper and Wise clashed over the management and direction of the business in late 1957 and the board of directors forced her out in January, 1958.  She filed a $1,600,000 suit against the company for conspiracy and breach of contract, but settled out of court for a year's salary -- about $30,000.  Shortly thereafter, Tupper sold the company to Dart/Rexall and relinquished all involvement with it. \n\nBeginning in 1958 and through the 1960s, Brownie co-founded three direct sales cosmetics companies, Cinderella (1958-59), Carissa (1963) and Sovera/Trivera (1966-69).  She also was president of Viviane Woodard Cosmetics (1960-62), and consulted for Artex and others.  In addition, she undertook a real estate development venture in Kissimmee with Charles McBurney and George Reynolds (both former Tupperware executives).  She seems never to have achieved the same level of success in these later business ventures. Wise continued to live in the Kissimmee area, moving from Waters' Edge, the spectacular 1920s mansion she occupied during the Tupperware years, to a home George Reynolds designed for her in.  She was active in her church and as an artist, working in clay and textiles.  During the last eight years of her life she was in declining health. She died in December 1992."],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "32cf1ecd924b7130aabdbe2f86f4ad57",
            "type": "note",
            "content": ["The papers consist of business records documenting the history of Tupperware from 1951-1958, during which Brownie Wise served as vice president of the Tupperware Company. Also, personal papers and business records documenting her marketing activities for Stanley Home Products, Vivian Woodard Cosmetics, and others."],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "fb9b886b249a1d25ec7c4e40c066cfe3",
            "type": "note",
            "content": ["The Brownie Wise Papers constitute an essential complement to the Earl Tupper Papers, acquired in 1992, and to the museum\u2019s rich collections of Tupperware products.  Together these collections document not only the founding and early business history of Tupperware, but also significant areas of American history in which the museum has a demonstrated interest.  The Brownie Wise Papers illuminate aspects of an American consumer culture which achieved its apex in the post-World War II years; in many ways, Tupperware and the Tupperware party reflect the key defining elements of the fifties. Of special significance is the story these papers tell of a successful woman business executive and working mother, in an era whose women have more often been characterized by June Cleaver and Harriet Nelson. The Tupperware story offers rich insights into the society and culture of the era, illuminating issues of gender, consumerism, and technological development. \n\nThere are approximately 15 cubic feet of materials, including photographic and audiovisual materials. The collection is organized into eight series.\n\nSeries 1: Personal Papers, circa 1928-1968. A scrapbook touches on her life as a girl in the 1920s.  Souvenir photographs of the 1936 Texas Centennial Exhibition at which she met her future husband, letterhead of his Detroit business, travel postcards, war ration books, income tax returns and a scrapbook chronicling her writings under the penname Hibiscus for the Detroit News, give a glimpse into her life during the late 1930s and early 1940s.  For the 1950s, there are records of taxes and household expenses.  The collection also includes some of her 1940s and 1950s dress patterns; as a woman in the public eye, Wise's trim figure and fashionable attire were much discussed. \n\nSeries 2: Stanley Home Products, Patio Parties, Poly-T Parties, Hibiscus Sales and Gardenia Sales, circa 1947-1959.  This series includes records of Wise's innovative direct sales businesses for the period before she was recruited by Tupperware.  Files include order forms, correspondence with sales agents, and instructions on sales methods.  There are sales records, invoices, shipping documents, accounting records and sales force newsletters from the Miami Tupperware dealership known as Hibiscus Sales, which Wise opened in 1949 with her mother.  Until her death in 1959, Brownie's mother Rose Humphrey, continued to operate the Miami dealership as well as Gardenia Sales, which supplied Tupperware to Puerto Rico.  There are accounting records and dealer correspondence documenting this enterprise.\n\nSeries 3: Tupperware Home Parties, circa 1951-1959. This series includes files of Wise's business correspondence, notes and memoranda, and speeches. There is some business correspondence with Earl Tupper, who remained at the firm's manufacturing plants in the Northeast. Also included are publicity reprints and news clippings, as well as public relations scrapbooks from 1951 to 1958.  There are nearly complete runs of Tupperware Sparks and the Tupperware Sentinel, company publications prepared for the sales force, as well as catalogs, recruitment publications and other company literature.  The series is divided into six subseries as follows: \n\nSubseries 3.1: Business Files and Correspondence, 1951-1959; 1988-1989\n\nSubseries 3.2: Speeches to Tupperware Sales Force, 1951-1957\n\nSubseries 3.3: Speeches to outside groups and Sales Organizations, 1952-1957\n\nSubseries 3.4: Tupperware publications, 1949-1966 (not inclusive)\n\nSubseries 3.5: Brownie Wise \"Idea\" files, undated\n\nSubseries 3.6: Publicity, 1951-1957\n\nSeries 4: Direct Sales Cosmetics Companies, circa 1958-1969. Wise's business activities in the late 1950s and early 1960s as a co-founder and consultant in direct selling cosmetics enterprises also are well documented.  Companies include Cinderella (1958-59), and Vivian Woodard (1960-1962), Carissa (1963), Aloe Vera (1966-1968), Trivera (1967-1968), and Sovera (1967-1969). Organized files include sales handbooks and dealer/distributor literature written by Wise, correspondence, reports and recommendations for clients, samples of advertising and marketing materials, and sales force newsletters.\n\nSeries 5: Other Direct Sales consulting, circa 1958-1971.  Handbooks, franchise agreements and correspondence document aspects of her work for ABCWare, Vacronware, Artex and others direct sales companies during the 1960s. \n\nSeries 6: Other Business Ventures, circa 1958-1967.  Includes files from several of Wise's late 1950s real estate development ventures, and from the Brownie Wise Sales Success course.\n\nSeries 7: Photographs, circa 1930-1968.\nIncludes personal photographs of Brownie Wise at home, travelling, and with her son, but the bulk of the material is comprised of publicity photographs or people and events, primarily for the Tupperware years, but also including some from Sovera and other cosmetics companies for which she consulted. \n\nSeries 8: Audio Recordings, circa 1953-1957; 1977; undated Includes open reel audiotapes, audio discs (78s and 33 1/3s) and one audio cassette recording of Tupperware Home parties meetings, motivational speeches, and songs.\n"],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "d486c783b2f216599f010cee92fec4f3",
            "type": "accessrestrict",
            "content": ["Collection is open for research."],
            "publish": True
        },
        {
            "jsonmodel_type": "note_digital_object",
            "persistent_id": "cdb746a50c2b15ed31635f11119e8cfe",
            "type": "userestrict",
            "content": ["Collection items available for reproduction, but the Archives Center makes no guarantees concerning copyright restrictions. Other intellectual property rights may apply. Archives Center cost-recovery and use fees may apply when requesting reproductions."],
            "publish": True
        }
    ],
    "linked_instances": [
        {"ref": "/repositories/20/resources/2976"}
    ],
    "metadata_rights_declarations": [],
    "content_warnings": [],
    "uri": "/repositories/20/digital_objects/3819",
    "repository": {"ref": "/repositories/20"},
    "tree": {"ref": "/repositories/20/digital_objects/3819/tree"}
}

test_location_delete = {'building': 'NMAH-SHF',
                        'coordinate_1_label': 'Test Shelf',
                        'coordinate_1_indicator': '602668'}
