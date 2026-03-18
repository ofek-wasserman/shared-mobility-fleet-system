from datetime import datetime


class BillingService:
    """Simple billing service with a fixed ride price."""

    FIXED_PRICE = 15.0

    def calculate_price(
        self, start_time: datetime, end_time: datetime, reported_degraded: bool
    ) -> float:
        """
        Calculate ride price.
        Uses a fixed price and returns free for reported degraded rides.
        """
        if reported_degraded:
            return 0.0
        return self.FIXED_PRICE

    def process_payment(self, user_payment_token: str, amount: float) -> bool:
        """Mock payment processing that always succeeds."""
        return True
