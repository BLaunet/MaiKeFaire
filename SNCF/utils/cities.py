ANNECY = {"code": "FRNCY"}
PARIS = {"code": "FRPAR"}
MARSEILLE = {"code": "FRMRS"}
AURAY = {"code": "FRXUY"}
RENNES = {"code": "FRRNS"}
TOULOUSE = {"code": "FRTLS"}
BAYONNE = {"code": "FRXBY"}
MONTPELLIER = {"code": "FRMPT"}
LORIENT = {"code": "FRLRT"}
CLERMONT_FERRAND = {"code": "FRCFE"}
LYON = {"code": "FRLYS"}
BIARRITZ = {"code": "FRBIQ"}
NANTES = {"code": "FRTNE"}


def _generateCityCodes():
    import requests
    CITIES = ['Annecy',
              'Paris',
              'Marseille',
              'Auray',
              'Rennes',
              'Toulouse',
              'Bayonne',
              'Montpellier',
              'Lorient',
              'Clermont_Ferrand',
              'Lyon',
              'Biarritz',
              'Nantes'
             ]
    for city in CITIES:
        r = requests.get('https://www.oui.sncf/booking/autocomplete-d2d?uc=fr-FR&searchField=origin&searchTerm={}'.format(city))
        print(city.upper()+' = {"code": "%s"}'%r.json()[0]['id'])
