# Practicing building an E-commerce Platform API on Django REST Framework

## Key Areas Explored:

### Requests/Parsers

- Handling requests containing serialized data and media files e.g. using JSON/MultiPartParser.

### Models/Admin/Serializers

- Implementing custom object managers, extending object-model methods.
- Registering/customizing models on the admin interface, automatically populating slug fields based on corresponding name fields.
- Serializing/Deserializing objects, handling many-to-many-field in creation and updates.

### Caching/Sessions

- Implementing and handling per-view caching on object retrieval, updates, and deletion.
- Setting up appropriate session storage, CRUD operations on request session data (cart data and refresh tokens are currently stored in session).

### Versioning

- Properly leveraging app names and namespaces for Namespace versioning.

### Media Handling

- Configuration for media uploads in settings.
- Setting up cloudinary for image uploads and handling related operations e.g. image deletion from database.

### Custom exception handling

- Understanding and extending rest_framework's exception handlers to customize error responses.

### Testing

- Understanding and implementing tests using django/drf test suite to ensure endpoints work as intended.

### Custom Middleware

- Understanding and customizing django's middleware to handle manually blacklisted simple_JWT access tokens.

### Token/Stateless Authentication

- Understanding the usage of [Knox](https://github.com/jazzband/django-rest-knox) and [simple_jwt](https://github.com/jazzband/djangorestframework-simplejwt) for user authentication and customizing them as needed.
