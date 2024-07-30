from django.core.cache import cache

from .models import Artwork, Genre

from celery import shared_task
import pickle


@shared_task
def update_palette_cache_details(slug, object_type, is_delete=False, object_id=None):
    """
    Updates genre/artworks cache when an object is created, updated, or deleted.
    """
    objects_cache_ids = []
    object_model = Genre if object_type == "genre" else Artwork
    item = object_model.objects.filter(slug=slug).first()
        
    if is_delete:
        cache.delete(f"{object_type}_{slug}")
    elif object_id is not None:
        cache.set(f"{object_type}_{object_id}", pickle.dumps(item))
    else:
        cache.set(f"{object_type}_{slug}", pickle.dumps(item))
        
    objects_cache = cache.get(f"{object_type}_list")
    if objects_cache is not None:
        objects_cache = pickle.loads(objects_cache)
        objects_cache_ids = [i.id for i in objects_cache if i.slug != slug]
        
    if not is_delete:
        objects_cache_ids.append(item.id)
        
    object_list = object_model.objects.filter(id__in=objects_cache_ids)
    cache.set(f"{object_type}_list", pickle.dumps(object_list))

    