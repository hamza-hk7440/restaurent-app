from uuid import UUID
from datetime import date
from typing import List, Optional
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.exceptions.domain_exceptions import MenuNotFoundException
from reservation.application.dtos.catalog_and_menu_dtos import GetDailyMenuQuery,DailyMenuResponseDTO,MealResponseDTO

class GetDailyMenuUseCase:
    def __init__(self, daily_menu_repository: IDailyMenuRepository):
        self._daily_menu_repo = daily_menu_repository

    async def execute(self, query: GetDailyMenuQuery) -> DailyMenuResponseDTO:
        daily_menu = await self._get_menu_or_raise(
            restaurent_id=query.restaurent_id,
            date=query.date
        )
        filtered_meals = self._filter_meals(daily_menu.meals, query.category, query.search_query)
        return DailyMenuResponseDTO.from_entity(daily_menu, filtered_meals)
    async def _get_menu_or_raise(self, restaurent_id: str, date: date):
        daily_menu = await self._daily_menu_repo.get_by_restaurent_by_date(
            restaurent_id=restaurent_id,
            date=date
        )
        if not daily_menu:
            raise MenuNotFoundException("Daily menu not found")
        return daily_menu
    @classmethod
    def _filter_meals(cls, meals: list, category: Optional[str], search_query: Optional[str]) -> list:
        return [
            meal for meal in meals
            if cls._matches_category(meal, category) and cls._matches_search(meal, search_query)
        ]
    @staticmethod
    def _matches_category(meal, category: Optional[str]) -> bool:
        if not category:
            return True
        return str(meal.category).lower() == category.lower()
    @staticmethod
    def _matches_search(meal, search_query: Optional[str]) -> bool:
        if not search_query:
            return True
        return search_query.lower() in meal.name.lower() or search_query.lower() in meal.description.lower()
    @staticmethod
    def _map_to_meal_response_dto(meal) -> MealResponseDTO:
        return MealResponseDTO(
            id=meal.id,
            name=meal.name,
            description=meal.description,
            price=meal.price,
            category=meal.category
        )