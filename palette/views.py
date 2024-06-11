from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser

from .serializers import GenreSerializer, ArtworkSerializer, Genre, Artwork
from .utils import format_error

from django.db.transaction import atomic


class GenreList(APIView):
    throttle_classes = [AnonRateThrottle]
    serializer_class = GenreSerializer
    
    def get(self, request):
        genres = Genre.objects.all()
        data = self.serializer_class(genres, many=True).data
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                with atomic():
                    genre = serializer.save()
                genre_data = self.serializer_class(genre).data
                return Response(genre_data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            error_list = format_error(e)  
            return Response(error_list, status=status.HTTP_400_BAD_REQUEST)
        
        
class GenreDetail(APIView):
    throttle_classes = [AnonRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = GenreSerializer
    
    def get(self, request, slug):
        genre = Genre.objects.filter(slug=slug).first()
        if genre:
            data = self.serializer_class(genre).data
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, slug):
        genre = Genre.objects.filter(slug=slug).first()
        if genre:
            serializer = self.serializer_class(genre, data=request.data, partial=True)
            
            try:
                if serializer.is_valid(raise_exception=True):
                    with atomic():
                        genre = serializer.save()
                    genre_data = self.serializer_class(genre).data
                    return Response(genre_data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                error_list = format_error(e)
                return Response(error_list, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, slug):
        genre = Genre.objects.filter(slug=slug).first()
        if genre:
            with atomic():
                genre.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)
        
        
class ArtworkList(APIView):
    throttle_classes = [AnonRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = ArtworkSerializer
    
    def get(self, request):
        artworks = Artwork.available.all()
        data = self.serializer_class(artworks, many=True).data
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                with atomic():
                    artwork = serializer.save()
                artwork_data = self.serializer_class(artwork).data
                return Response(artwork_data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            error_list = format_error(e)
            return Response(error_list, status=status.HTTP_400_BAD_REQUEST)
        
        
class ArtworkDetail(APIView):
    throttle_classes = [AnonRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = ArtworkSerializer
    
    def get(self, request, slug):
        artwork = Artwork.available.filter(slug=slug).first()
        if artwork:
            data = self.serializer_class(artwork).data
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, slug):
        artwork = Artwork.objects.filter(slug=slug).first()
        if artwork:
            serializer = self.serializer_class(artwork, data=request.data, partial=True)
            
            try:
                if serializer.is_valid(raise_exception=True):
                    with atomic():
                        artwork = serializer.save()
                    artwork_data = self.serializer_class(artwork).data
                    return Response(artwork_data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                error_list = format_error(e)
                return Response(error_list, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, slug):
        artwork = Artwork.objects.filter(slug=slug).first()
        if artwork:
            with atomic():
                artwork.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response("Artwork not found", status=status.HTTP_404_NOT_FOUND)