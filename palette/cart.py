from django.conf import settings
from .models import Artwork
from decimal import Decimal


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
    def save(self):
        self.session.modified = True
            
    def add(self, artwork, quantity=1, override_quantity=False):
        artwork_id = str(artwork.id)
        if artwork_id not in self.cart:
            self.cart[artwork_id] = {"price": artwork.price,
                                        "quantity": 0}
            
        if override_quantity:
            self.cart[artwork_id]["quantity"] = quantity
        else:
            self.cart[artwork_id]["quantity"] += quantity
            
        self.save()
            
    def remove(self, artwork):
        artwork_id = str(artwork_id)
        if artwork_id in self.cart:
            del self.cart[artwork_id]
            
            self.save()
        
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
        
    def __iter__(self):
        artwork_ids = self.cart.keys()
        artworks = Artwork.objects.filter(id__in=artwork_ids)
        
        cart =self.cart.copy()
        
        for artwork in artworks:
            cart[str(artwork.id)]["artwork"] = artwork
            
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item
            
    def __len__(self):
        return sum(item["quantity"] for item in self.cart.value())
    
    def get_total_price(self):
        return sum(item["total_price"] for item in self.cart.values())
        