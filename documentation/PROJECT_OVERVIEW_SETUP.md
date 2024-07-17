# Overview
Palette Portal is a digital art marketplace where users can sign up as either artists or collectors. Artists can showcase and sell their artwork, while collectors can browse and purchase art. Artists can also chat with collectors and vice-versa in real-time. The project is built using Django and Django REST Framework (DRF), leveraging various technologies such as PostgreSQL, Redis, Docker, SimpleJWT/Knox(DRF) and Cloudinary for different like user, authentication, media file storage/delivery, real-time connection, session/cache setup, and containerization.

## Dependencies
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Docker
- Cloudinary

## Environment Setup (Using Docker)
- Clone the Repository:
```shell
git clone https://github.com/iamprecieee/palette-portal-api.git
cd palette-portal-api
```
- <b>Set Up Environment Variables</b>. Create a `.env` file in the root directory and add the necessary environment variables. Refer to the provided [.env.example](.env.example) for guidance.
- Build necessary docker images and run their corresponding containers:
```shell
 docker-compose up -d --build
```
- Access the application at [localhost](http://127.0.0.1:8001).
- To stop containers, use:
```shell
docker-compose down
```
- To restart containers, use:
```shell
docker-compose restart
```
- To run service-based commands, use:
```shell
docker-compose exec <service> <command>
```

## docker-compose.yml
Key services include:
- <i><b>web</b></i>: The Django application service, which depends on the postgresql(healthcheck included) and redis services.
`.:/home/portal` allows the web container to have access to the project's source code and any changes made to the source code on the host machine to be reflected inside the container without needing to rebuild the image.
- <i><b>palette_db</b></i>: The PostgreSQL database service.
- <i><b>redis</b></i>: The default Redis service for caching.
- <i><b>session_redis</b></i>: A separate Redis service for session management.
- <i><b>chat_redis</b></i>: A Redis service for real-time communication.
Each service has its own configuration, including environment variables, ports, volumes, and dependencies.