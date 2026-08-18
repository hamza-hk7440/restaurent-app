from datetime import date, timedelta
from typing import List, Set, Optional
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository
from reservation.domain.interfaces.daily_menu_repo import IDailyMenuRepository
from reservation.domain.exceptions.domain_exceptions import RestaurantNotFoundException
from reservation.application.dtos.availability_dtos import GetAvailbleDaysQuery, AvailbleDaysResponseDTO
from reservation.domain.value_objects.restaurent_status import RestaurentStatus


class GetAvailableDaysUseCase:
    def __init__(
        self,
        restaurant_repository: IRestaurentRepository,
        daily_menu_repository: IDailyMenuRepository,
    ):
        self._restaurant_repo = restaurant_repository
        self._daily_menu_repo = daily_menu_repository

    async def execute(self, query: GetAvailbleDaysQuery) -> List[AvailbleDaysResponseDTO]:
        restaurant = await self._get_restaurant_or_raise(query.restaurant_id)
        start = self._resolve_start_date(query.start_date)
        end = start + timedelta(days=query.days_ahead - 1)

        existing_menus = await self._daily_menu_repo.get_by_restaurent_and_date_range(
            restaurant_id=query.restaurant_id,
            start_date=start,
            end_date=end,
        )

        active_dates = {menu.date for menu in existing_menus if menu.is_available}
        is_open = restaurant.status == RestaurentStatus.OPEN

        return self._build_days_schedule(start, query.days_ahead, is_open, active_dates)

    async def _get_restaurant_or_raise(self, restaurant_id):
        restaurant = await self._restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise RestaurantNotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return restaurant

    @staticmethod
    def _resolve_start_date(start_date: Optional[date]) -> date:
        if start_date is not None:
            return start_date.date() if hasattr(start_date, "date") else start_date
        return date.today()

    @classmethod
    def _build_days_schedule(
        cls,
        start: date,
        days_ahead: int,
        is_open: bool,
        active_dates: Set[date],
    ) -> List[AvailbleDaysResponseDTO]:
        today = date.today()
        result: List[AvailbleDaysResponseDTO] = []

        for i in range(days_ahead):
            current_date = start + timedelta(days=i)
            is_avail = is_open and current_date >= today and current_date in active_dates

            result.append(
                AvailbleDaysResponseDTO(
                    date=current_date,
                    day_name=current_date.strftime("%A"),
                    is_available=is_avail,
                    is_operating_day=is_open,
                )
            )

        return result
