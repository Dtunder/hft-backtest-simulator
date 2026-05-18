class MarketImpactModel:
    """
    Non-linear market impact model that degrades fill price based on order size.
    Based on a standard power-law impact model: impact = alpha * size^beta.
    """
    def __init__(self, alpha=0.0005, beta=0.5):
        self.alpha = alpha
        self.beta = beta

    def get_fill_price(self, base_price, order_size, is_buy):
        """
        Calculates the fill price given a base price and order size.

        :param base_price: The mid-price or base price of the asset.
        :param order_size: The quantity of the order.
        :param is_buy: Boolean, True if buying, False if selling.
        :return: The adjusted fill price.
        """
        if order_size <= 0:
            return base_price

        impact = self.alpha * (order_size ** self.beta)

        if is_buy:
            # Buying pushes the price up (worse fill price)
            return base_price * (1 + impact)
        else:
            # Selling pushes the price down (worse fill price)
            return base_price * (1 - impact)
