from typing import List
from reservation.domain.entities.restaurents_entity import Restaurent
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.application.dtos.catalog_and_menu_dtos import RestaurentResponseDTO,GetRestaurentsQuery

class GetRestaurentsUseCase:
    def __init__(self, restaurent_repository: IRestaurentRepository):
        self.restaurent_repository = restaurent_repository
    async def execute(self, query: GetRestaurentsQuery) -> List[RestaurentResponseDTO]:
        restaurents = await self.restaurent_repository.get_by_establishment(query.establishment_id, query.status)
        return [RestaurentResponseDTO.from_entity(restaurent) for restaurent in restaurents]
