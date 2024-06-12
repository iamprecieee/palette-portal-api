from django.conf import settings

from .serializers import Artwork, ArtworkSerializer

from decimal import Decimal


# Class for oprating shopping carts in the request session
class Cart:
    def __init__(self, request):
        self.session = request.session

        """
        Retrieve and initialize an existing cart from session or create a new one.
        Cart is saved in session as a dict.
        """
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
            
        self.cart = cart

    # Alternative to this is assigning SESSION_SAVE_EVERY_REQUEST=True in the `settings` file
    def save(self):
        self.session.modified = True

    # Increments value of artwork `quantity` in cart
    def add(self, artwork, quantity=1):
        """
        Retrieve an existing nested artwork dict from the cart or create a new one.
        The `key` is the artwork.id; the `value` is a dict of the artwork.price and quantity(defaults to 0).
        """
        artwork_id = str(artwork.id)
        if artwork_id not in self.cart:
            self.cart[artwork_id] = {"price": str(artwork.price), "quantity": 0}

        self.cart[artwork_id]["quantity"] += quantity
        self.save()

    # Similar to add(), but is used to override `quantity` value of existing artwork dict
    def update(self, artwork, quantity=1):
        artwork_id = str(artwork.id)
        if artwork_id in self.cart:
            self.cart[artwork_id]["quantity"] = quantity
            self.save()

    # Removes artwork from cart
    def remove(self, artwork):
        artwork_id = str(artwork.id)
        if artwork_id in self.cart:
            del self.cart[artwork_id]
            self.save()

    # Removes cart from session
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    # Handles the `iter` attribute of cart
    def __iter__(self):
        # Create a copy of existing cart for every iteration
        cart = self.cart.copy()

        # Retrieves all `keys` in cart and adds serialized artwork data for each key
        artwork_ids = self.cart.keys()
        artworks = Artwork.objects.filter(id__in=artwork_ids)
        for artwork in artworks:
            artwork_data = ArtworkSerializer(
                artwork
            ).data  # `artwork` on its own is not JSON-serializable
            cart[str(artwork.id)]["artwork"] = artwork_data

        # Calculates and sets a total price for each items in cart
        for item in cart.values():
            item["total_price"] = str(
                Decimal(item["price"]) * item["quantity"]
            )  # Decimal() is not JSON-serializable
            yield item

    # Calculates the total number of individual items in cart
    def __len__(self):
        return sum(item["quantity"] for item in self.cart.value())

    # Calculates the total price of all cart items
    def get_total_price(self):
        return sum(Decimal(item["total_price"]) for item in self.cart.values())
