# Use the bookworm-slim image
FROM debian:bookworm-slim

# Set the working directory in the container to /cve_updater
RUN mkdir /cve_updater
WORKDIR /cve_updater

# Add the current directory contents into the container at /cve_updater
ADD . /cve_updater

# Update the system and install cron python3 python3-venv openssh-client git
RUN apt-get update && apt-get install -y cron python3 python3-venv openssh-client git

# Create a Python virtual environment and install the required packages
RUN python3 -m venv /cve_updater/venv
RUN /cve_updater/venv/bin/pip install --no-cache-dir -r requirements.txt

# Set up SSH for git
ARG GIT_USERNAME
ARG GIT_EMAIL
COPY .ssh/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN git config --global user.name "${GIT_USERNAME}"
RUN git config --global user.email "${GIT_EMAIL}"

# Add a cron job to run main.py every 12 hours
RUN (crontab -l ; echo "0 */12 * * * . /cve_updater/venv/bin/activate && python3 /cve_updater/main.py") | crontab

# Start cron in the foreground
CMD ["cron", "-f"]