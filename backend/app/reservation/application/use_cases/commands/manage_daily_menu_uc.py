from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from reservation.domain.entities.daily_menu_entity import DailyMenu
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.domain.exceptions.domain_exceptions import (
    RestaurantNotFoundException,
    InvalidMenuDataException,
)
from reservation.application.dtos.catalog_and_menu_dtos import (
    ManageDailyMenuCommand,
    MenuItemInputDTO,
    MenuItemResponseDTO,
    DailyMenuResponseDTO,
)

class ManageDailyMenuUseCase:
    def __init__(
        self,
        daily_menu_repository: IDailyMenuRepository,
        restaurant_repository: IRestaurentRepository,
    ):
        self._daily_menu_repo = daily_menu_repository
        self._restaurant_repo = restaurant_repository

    async def execute(self, command: ManageDailyMenuCommand) -> DailyMenuResponseDTO:
        await self._verify_restaurant_exists(command.restaurant_id)
        self._validate_menu_items(command.items)

        existing_menu = await self._daily_menu_repo.get_by_restaurent_by_date(
            restaurant_id=command.restaurant_id,
            date=command.target_date,
        
        )

        menu_entity = self._build_or_update_entity(existing_menu, command)
        saved_menu = await self._daily_menu_repo.create(menu_entity)

        return self._map_to_response_dto(saved_menu)

    async def _verify_restaurant_exists(self, restaurant_id: UUID) -> None:
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(
                f"Restaurant with ID '{restaurant_id}' does not exist."
            )

    @staticmethod
    def _validate_menu_items(items: List[MenuItemInputDTO]) -> None:
        if not items:
            raise InvalidMenuDataException("Daily menu must contain at least one item.")

    def _build_or_update_entity(
        self, existing_menu: Optional[DailyMenu], command: ManageDailyMenuCommand
    ) -> DailyMenu:
        
        # Convert Pydantic DTOs directly to dictionaries to be stored as JSON/dicts in the entity
        raw_items: List[Dict[str, Any]] = [
            item.model_dump() for item in command.items
        ]

        if existing_menu:
            existing_menu.items = raw_items
            existing_menu.is_active = command.is_active
            existing_menu.updated_at = datetime.now(timezone.utc)
            return existing_menu

        return DailyMenu(
            id=uuid4(),
            restaurant_id=command.restaurant_id,
            target_date=command.target_date,
            meal_type=command.meal_type,
            is_active=command.is_active,
            items=raw_items,
            updated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def _map_to_response_dto(cls, menu: DailyMenu) -> DailyMenuResponseDTO:
        item_dtos = [cls._map_dict_to_dto(item) for item in menu.items]

        return DailyMenuResponseDTO(
            id=menu.id,
            restaurant_id=menu.restaurant_id,
            target_date=menu.target_date,
            meal_type=menu.meal_type,
            is_active=menu.is_active,
            items=item_dtos,
            updated_at=menu.updated_at or datetime.now(timezone.utc),
        )

    @staticmethod
    def _map_dict_to_dto(item: Dict[str, Any]) -> MenuItemResponseDTO:
        return MenuItemResponseDTO(
            name=item.get("name", ""),
            category=item.get("category", ""),
            description=item.get("description"),
            calories=item.get("calories"),
            allergens=item.get("allergens", []),
        )