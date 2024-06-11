from rest_framework.serializers import ModelSerializer, CharField, ListField, SerializerMethodField
from .models import Genre, Artwork
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "created"]
        read_only_fields = ["id", "created"]
        
    def create(self, validated_data):
        name = validated_data["name"]
        return Genre.objects.create(name=name, slug=slugify(name))
    
    
class ArtworkSerializer(ModelSerializer):
    genre = SerializerMethodField()
    genres = ListField(
        write_only=True,
        allow_empty=True,
        child=CharField(),
    )
    
    class Meta:
        model = Artwork
        fields = "__all__"
        read_only_fields = ["id", "genre", "created", "updated"]
        
    def get_genre(self, obj):
        genres = obj.genre.all()
        return [genre.name for genre in genres]
        
    def create(self, validated_data):
        genre_data = validated_data.pop("genres", [])
        
        validated_data["slug"] = slugify(validated_data["name"])
        if "is_available" not in validated_data:
            validated_data["is_available"] = True
            
        artwork = Artwork.objects.create(**validated_data)
        
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
        new_genre_data = validated_data.pop("genres", [])
        
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])
        
        instance = super().update(instance, validated_data)
        
        new_genre_list = []
        for genre_name in new_genre_data:
            new_genre = Genre.objects.filter(slug=slugify(genre_name)).first()
            if new_genre:
                new_genre_list.append(new_genre)
            
        new_genre_ids = [genre.id for genre in new_genre_list]
            
        if new_genre_ids:
            instance.genre.add(*new_genre_ids)
            
        return instance      
            
        
        
    