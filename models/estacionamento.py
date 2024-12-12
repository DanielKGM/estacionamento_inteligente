from typing import List, Dict, Optional

class Vaga:
    def __init__(self, nome: str, status: Optional[float] = None, date: Optional[str] = None):
        self.nome = nome
        self.status = status
        self.date = date

class Estacionamento:
    def __init__(self, 
                 id: int,
                 created_at: str, 
                 updated_at: str, 
                 lat: float, 
                 lon: float, 
                 status: str, 
                 description: str, 
                 uuid: str, 
                 city: Optional[str], 
                 state: Optional[str], 
                 country: Optional[str], 
                 vagas: Optional[List[Vaga]] = None):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.lat = lat
        self.lon = lon
        self.status = status
        self.description = description
        self.uuid = uuid
        self.city = city
        self.state = state
        self.country = country
        self.vagas = vagas if vagas is not None else []

    @staticmethod
    def from_api_data(data: Dict, vagas: Optional[List[Dict]] = None):
        estacionamentos_data = data['data']
        return Estacionamento(
            id=estacionamentos_data['id'],
            created_at=estacionamentos_data['created_at'],
            updated_at=estacionamentos_data['updated_at'],
            lat=estacionamentos_data['lat'],
            lon=estacionamentos_data['lon'],
            status=estacionamentos_data['status'],
            description=estacionamentos_data['description'],
            uuid=estacionamentos_data['uuid'],
            city=estacionamentos_data.get('city'),
            state=estacionamentos_data.get('state'),
            country=estacionamentos_data.get('country'),
            vagas=[Vaga(nome=v['nome'], status=v.get('status'), date=v.get('date')) for v in vagas] if vagas else []
        )
