FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl git python3-pip
RUN curl -sfL https://direnv.net/install.sh | bash
RUN echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
# Optionally, ensure that .bashrc is sourced in non-interactive shells
RUN echo 'source ~/.bashrc' >> ~/.bash_profile

RUN curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
	| tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
	&& echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
	| tee /etc/apt/sources.list.d/ngrok.list \
	&& apt update \
	&& apt install ngrok

RUN git clone https://github.com/ingydotnet/git-subrepo /git-subrepo
RUN echo 'source /git-subrepo/.rc' >> ~/.bashrc

RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
# Expose Docker socket to allow Docker-in-Docker to work
VOLUME /var/run/docker.sock:/var/run/docker.sock
# Set working directory inside the container
WORKDIR /workspace

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1
