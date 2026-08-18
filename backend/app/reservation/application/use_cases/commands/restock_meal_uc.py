from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from reservation.domain.entities.daily_menu_entity import DailyMenu
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.exceptions.domain_exceptions import (
    MenuNotFoundException,
    InvalidMenuStateException,
)
from reservation.application.dtos.catalog_and_menu_dtos import (
    RestockMealCommand,
    RestockMealResponseDTO,
)


class RestockMealUseCase:
    def __init__(self, daily_menu_repository: IDailyMenuRepository):
        self._daily_menu_repo = daily_menu_repository

    async def execute(self, command: RestockMealCommand) -> RestockMealResponseDTO:
        menu = await self._get_menu_or_raise(command.menu_id)

        self._verify_ownership_if_provided(menu, command.restaurant_id)
        
        previous_quantity = getattr(menu, "available_quantity", 0)
        updated_menu = await self._apply_restock(menu, command.quantity_to_add)

        return self._map_to_response_dto(updated_menu, previous_quantity)

    async def _get_menu_or_raise(self, menu_id: UUID) -> DailyMenu:
        menu = await self._daily_menu_repo.get_by_id(menu_id)
        if not menu:
            raise MenuNotFoundException(f"Daily menu with ID '{menu_id}' not found.")
        return menu

    @staticmethod
    def _verify_ownership_if_provided(
        menu: DailyMenu, restaurant_id: Optional[UUID]
    ) -> None:
        if restaurant_id and str(menu.restaurant_id) != str(restaurant_id):
            raise InvalidMenuStateException(
                f"Menu '{menu.id}' does not belong to restaurant '{restaurant_id}'."
            )

    async def _apply_restock(
        self, menu: DailyMenu, quantity_to_add: int
    ) -> DailyMenu:
        current_quantity = getattr(menu, "stored_available_quantity", getattr(menu, "available_quantity", 0))
        menu.stored_available_quantity = current_quantity + quantity_to_add
        menu.updated_at = datetime.now(timezone.utc)
        
        # Depending on the repo design, this could be a partial update (e.g., increment_stock)
        # or a full aggregate save. We use save() here to persist the updated entity.
        return await self._daily_menu_repo.save(menu)

    @staticmethod
    def _map_to_response_dto(
        menu: DailyMenu, previous_quantity: int
    ) -> RestockMealResponseDTO:
        return RestockMealResponseDTO(
            menu_id=menu.id,
            restaurant_id=menu.restaurant_id,
            previous_quantity=previous_quantity,
            new_quantity=getattr(menu, "stored_available_quantity", previous_quantity),
            updated_at=menu.updated_at or datetime.now(timezone.utc),
        )
