# Pull docker image
FROM python:3.12-slim-bullseye

# Set environmental variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a group "palette", a non-root user "artist", assign the user to the group, and set its home directory "/home/portal"
# /sbin/nologin specifies no login shell
RUN groupadd -r palette && useradd -r -g palette -d /home/portal -s  /sbin/nologin -c "docker image user" artist

# Create the home directory for the user "artist", changes ownership of the directory to user and group
RUN mkdir /home/portal && chown -R artist:palette /home/portal

# Set working directory
WORKDIR /home/portal

# Copy requirements.txt and installer file to the container
# Doing these before copying other files/dirs to cache the requirements for subsequent builds
COPY ./requirements.txt ./requirements.txt
COPY ./install_requirements.py ./install_requirements.py

# Install dependencies
RUN python install_requirements.py

# Copy entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

# Give execute permissions for entrypoint
RUN chmod +x entrypoint.sh

# Copy redis conf file
COPY ./redis.conf ./redis.conf

# Copy the current project directory's contents into the container at "/home/portal"
COPY . .

# Ensure all files are owned by the new user "artist"
# This is because files are copied as root user by default
RUN chown -R artist:palette /home/portal

# Collect static files
RUN python manage.py collectstatic --no-input

# Change user to non-root user "artist"
USER artist

# Specify the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]