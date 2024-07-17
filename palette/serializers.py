from django.utils.text import slugify
from rest_framework.fields import empty

from .models import Genre, Artwork, Artist

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ListField,
    SerializerMethodField,
    Serializer,
    ChoiceField,
    ValidationError
)


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "created"]
        read_only_fields = ["id", "created"]

    def create(self, validated_data):
        name = validated_data["name"]
        return Genre.objects.create(name=name, slug=slugify(name))
    
    def update(self, instance, validated_data):
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])  
        elif "slug" in validated_data:
            raise ValidationError({"update": "You can only update the Name field. Slug field updates automatically."}, code="invalid")
            
        return super().update(instance, validated_data)


class ArtworkSerializer(ModelSerializer):
    artist = SerializerMethodField()
    genre = SerializerMethodField()
    genres = ListField(
        write_only=True,
        allow_empty=True,
        child=CharField(),
    )

    class Meta:
        model = Artwork
        fields = "__all__"
        read_only_fields = ["id", "artist", "created", "updated"]
        
    def get_artist(self, obj):
        return obj.artist.user.username

    def get_genre(self, obj):
        genres = obj.genre.all()
        return [genre.name for genre in genres]

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        if "is_available" not in self.context["data"]:
            validated_data["is_available"] = True
            
        user = self.context["user"]
        artist = Artist.objects.filter(user=user).first()
        validated_data["artist"] = artist
            
        genre_data = validated_data.pop("genres", [])
        artwork = Artwork.objects.create(**validated_data)

        """
        Handles logic for `many-to-many` fields.
        This requires a list containing the name of each genre to be added in the `ManyToManyField`, seperated by commas.
        For each name in the list, the ids of corresponding genre objects are added to the artwork object if existing.
        """
        new_genre_list = []
        for genre_name in genre_data:
            genre = Genre.objects.filter(slug=slugify(genre_name)).first()
            if genre:
                new_genre_list.append(genre)

        new_genre_ids = [genre.id for genre in new_genre_list]
        if new_genre_ids:
            artwork.genre.add(*new_genre_ids)

        return artwork

    def update(self, instance, validated_data):
        excluded = ["name", "slug", "image", "artist", "instagram"]
        
        error_list = []
        for x in excluded:
            if x in validated_data:
                error_list.append(x)
                
        if len(error_list) == 1:
            raise ValidationError({"update": f"You cannot edit the value of {error_list}."})
        elif len(error_list) > 1:
            raise ValidationError({"update": f"You cannot edit the values of {', '.join(error_list)}."})
        
        new_genre_data = validated_data.pop("genres", [])
        instance = super().update(instance, validated_data)

        # Similar functionality to create()
        new_genre_list = []
        for genre_name in new_genre_data:
            new_genre = Genre.objects.filter(slug=slugify(genre_name)).first()
            if not new_genre:
                raise ValidationError({"slug": "Genre does not match existing genre data."}, code="invalid")
            new_genre_list.append(new_genre)

        new_genre_ids = [genre.id for genre in new_genre_list]
        if new_genre_ids:
            instance.genre.add(*new_genre_ids)

        return instance


class CartUpdateSerializer(Serializer):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]
    quantity = ChoiceField(choices=QUANTITY_CHOICES, required=False)
    
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        
        from .cart import Cart
        
        self.cart = Cart
    
    def create(self, validated_data):
        request = self.context["request"]
        artwork = self.context["artwork"]
        cart = self.cart(request)
        if "quantity" in validated_data:  
            cart.add(artwork, validated_data["quantity"])
        else:
            cart.add(artwork)
            
        return cart
    
    def update(self, instance, validated_data):
        request = self.context["request"]
        cart = self.cart(request)
        if "quantity" in validated_data:  
            cart.add(instance, validated_data["quantity"], override=True)
        else:
            cart.add(instance, override=True)
            
        return cart
