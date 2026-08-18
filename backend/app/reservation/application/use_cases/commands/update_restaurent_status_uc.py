import logging
from reservation.application.dtos.catalog_and_menu_dtos import (UpdateRestaurantStatusResponseDTO,UpdateRestaurantStatusRequest)
from reservation.domain.interfaces.restaurent_repo import IRestaurentRepository


logger = logging.getLogger(__name__)

class UpdateRestaurantStatusUseCase:
    def __init__(self, restaurant_repository: IRestaurentRepository):
        self._restaurant_repo = restaurant_repository
    def execute(self, command: UpdateRestaurantStatusRequest) -> UpdateRestaurantStatusResponseDTO:
        logger.info(f"Executing UpdateRestaurantStatusUseCase for restaurant_id: {command.restaurant_id} with new status: {command.new_status}")
        restaurant = self._restaurant_repo.get_by_id(command.restaurant_id)
        if not restaurant:
            logger.error(f"Restaurant with ID '{command.restaurant_id}' not found.")
            raise ValueError(f"Restaurant with ID '{command.restaurant_id}' not found.")
        current_status = restaurant.get("status")
        if current_status == command.new_status.value:
            logger.warning(f"Restaurant '{command.restaurant_id}' is already in status '{command.new_status.value}'. No update performed.")
            return UpdateRestaurantStatusResponseDTO(
                restaurant_id=command.restaurant_id,
                previous_status=current_status,
                new_status=current_status,
                message="No update performed. Status is already the same.",
                success=True
            )
        updated_status = self._restaurant_repo.update_status(command.restaurant_id, command.new_status)
        logger.info(f"Restaurant '{command.restaurant_id}' status updated from '{current_status}' to '{updated_status}'.")
        if not updated_status:
            logger.error(f"Failed to update status for restaurant '{command.restaurant_id}'.")
            raise ValueError(f"Failed to update status for restaurant '{command.restaurant_id}'.")
        return UpdateRestaurantStatusResponseDTO(
            restaurant_id=command.restaurant_id,
            previous_status=current_status,
            new_status=updated_status,
            message=f"Status updated successfully for restaurant '{command.restaurant_id}'.",
            success=True
        )