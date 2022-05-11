import json
from tkinter.messagebox import NO
from colorama import deinit
from matplotlib import artist
from pymongo import MongoClient
from bson import ObjectId, objectid as bid

# inserire di defolt il prjc dei campi in comune con il ticket
# db.COLLECTION_NAME.find().sort({KEY:1}) da implemetare?


class GestioneConcerti:
    def __init__(self, mongoConnectio="mongodb://localhost:27017", tkt_len=8):
        self.len_ticket = tkt_len
        self.client = MongoClient(mongoConnectio)

    def getConcerto(self, query={}, prjc=None, limiti_=None):
        if limiti_ != None:
            res = self.client['UFS-5']['Concert'].find(
                filter=query, projection=prjc, limit=limiti_)
        else:
            res = self.client['UFS-5']['Concert'].find(
                filter=query, projection=prjc)

        return res

    def nearConcerto(self, pos=[0, 0], max=None, min=None):
        quary = {
            "luogo.posizione": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        'coordinates': pos
                    }
                }
            }
        }
        if(max != None):
            quary["luogo.posizione"]["$near"]['$maxDistance'] = max
        if(min != None):
            quary["luogo.posizione"]["$near"]['$maxDistance'] = min
        temp = self.client['UFS-5']['Concert'].find(quary)
        lista = []
        for e in temp:
            lista.append(e)
        return lista

    def setConcerto(self, mydict, new=False):
        if type(mydict) is dict:
            mydict = [mydict]
        if new:
            return self.client['UFS-5']['Concert'].insert_many(mydict)
        else:
            updated = []
            for e in mydict:
                myquery = {"_id": e.pop('_id')}
                updated.append(
                    self.client['UFS-5']['Concert'].update_one(myquery, {"$set": e}))
                return updated

    def removeConcerto(self, toDelete={'_id': None}):
        delited = []
        if type(toDelete) is dict:
            if toDelete['_id'] == None:
                return self.client['UFS-5']['Concert'].delete_many({})
            toDelete = [toDelete]
        for e in toDelete:
            delited.append(self.client['UFS-5']['Concert'].delete_one(e))
            return delited

    def getTicket(self, query={}, prjc=None, limiti_=None):
        if limiti_ != None:
            res = self.client['UFS-5']['Ticket'].find(
                filter=query, projection=prjc, limit=limiti_)
        else:
            res = self.client['UFS-5']['Ticket'].find(
                filter=query, projection=prjc)
        return res

    # inserire la get del concerto con la query per trovare il concerto desiderato
    # creazione nuovo ticket con formato nserie = ZZ-00000000
    # controllo duplicati posti
    # creazione posto random
    def setTicket(self, mydict, new=False):
        update = []
        if type(mydict) is dict:
            mydict = [mydict]
        self.len_ticket
        if new:
            for i in mydict:
                zona_Posti = self.getConcerto(
                    {"_id": ObjectId(i['concerto'])}, {'posti': 1, 'data': 1})
                for e in zona_Posti[0]['posti']:
                    if e['area'] == i['posti']['area']:
                        prezzo = e['prezzo']
                        area = e['area']
                        nPostorim = e['n_postiRimasti']-1
                        nPostotot = e['n_postiTotali']
                        break

                data = zona_Posti[0]['data']
                print(self.setConcerto({"_id": ObjectId(i['concerto']), 'posto': {
                    'n_postiRimasti': nPostorim}})[0])
                if nPostorim < 0:
                    # ahah, scemo! = errore posti finiti
                    return 'ahah, scemo!'
                nPosto = nPostotot-nPostorim
                nPosto = str(nPosto)
                zeroLen = self.len_ticket-len(nPosto)
                n_serie = area[:2]+'0'*zeroLen+nPosto
                i['nserie'] = n_serie
                i['prezzo'] = prezzo
                i['data'] = data
            print(mydict)
            return self.client['UFS-5']['Ticket'].insert_many(mydict)
        else:
            for i in mydict:
                myquery = {"_id": i.pop('_id')}
                update.append(
                    self.client['UFS-5']['Ticket'].update_one(myquery, {"$set": i}))
                return update

    def removeTicket(self, toDelete={'_id': None}):
        delited = []
        if type(toDelete) is dict:
            if toDelete['_id'] == None:
                return self.client['UFS-5']['Ticket'].delete_many({})
            toDelete = [toDelete]
        for e in toDelete:
            delited.append(self.client['UFS-5']['Ticket'].delete_one(e))
            return delited


if __name__ == "__main__":
    query_delete = {
        '_id': ''
    }

    query_concerto_new = {
        "titolo": "",
        "artisti": [],
        "tour": "",
        "data": "",
        "luogo": {
            "nome": "",
            "via": "",
            "coordinate": ""
        },
        "posti": [
            {
                "area": "a",
                "n_postiRimasti": "10",
                "prezzo": ""
            }
        ]
    }

    query_concerto_find = {
        "titolo": "",
        "artisti": [],
    }

    query_ticket_new = {
        "nserie": "01001",
        "id_concerto": "",
        "nome": "",
        "cognome": "",
        "qrcode": "",
        "aquirente": "",
        "posto": {
            "area": "",
            "numero": "",
            "fila": ""
        },
        "prezzo": "",
        "data": "timestamp"
    }

    query_ticket_find = {
        "nome": "fabio",
        "cognome": "rossi"
    }
    temp = GestioneConcerti()

    with open(r'.\MongoDB\concerti.json') as json_file:
        new_concerto = json.load(json_file)

    temp.removeConcerto()
    temp.removeTicket()

    temp.setConcerto(new_concerto, True)
    found_concert = temp.getConcerto(
        {'titolo': new_concerto[0]['titolo']}, {'artisti': 1, '_id': 1})
    found_concert[0]['tour'] = 'jdsufhfdsldsfkj'
    a = temp.setConcerto(found_concert[0])
    # print(a)
    near = temp.nearConcerto([45.48307873172699, 9.13053663872388])
    # print(near[0]['luogo']['posizione'])
    # print(near[0]['luogo']['citta'])
    # for e in near:
    #     print(e['luogo']['citta'], end=' ')
    #     print(e['luogo']['posizione'])
    print(found_concert[0]['_id'])
    new_ticket = {
        "concerto": str(found_concert[0]['_id']),
        "nome": "Luca",
                "cognome": "Cavioni",
                "aquirente": "sadsadasdsas",
                "posti": {
                    "area": "prato gold",
        }
    }
    # new_ticket = {
    #     "nserie": "",
    #     "id_concerto": id,
    #     "nome": "Luca",
    #             "cognome": "Cavioni",
    #             "aquirente": "sadsadasdsas",
    #             "posti": {
    #                 "area": "PP",
    #                 "numero": 10,
    #                 "fila": 10
    #             }
    # }
    t = []
    for e in new_concerto:
        t.append(new_ticket)
    temp.setTicket(t, True)
    for a in temp.getTicket():
        print(a)

    temp.removeConcerto()
    temp.removeTicket()
