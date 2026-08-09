from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.application.dtos.catalog_and_menu_dtos import RestaurentResponseDTO, GetRestaurentDetailsQuery
from reservation.domain.exceptions.domain_exceptions import RestaurantNotFoundException

class GetRestaurentDetailsUseCase:
    def __init__(self, restaurent_repository: IRestaurentRepository):
        self.restaurent_repository = restaurent_repository

    async def execute(self, query: GetRestaurentDetailsQuery) -> RestaurentResponseDTO:
        restaurent = await self.restaurent_repository.get_by_id(query.restaurent_id)
        if not restaurent:
            raise RestaurantNotFoundException(f"Restaurant with ID {query.restaurent_id} not found.")
        return RestaurentResponseDTO.from_entity(restaurent)