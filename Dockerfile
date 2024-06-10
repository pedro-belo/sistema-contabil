# Utiliza a imagem bullseye (deb) como base.
FROM python:3.10-bullseye

# Sinaliza que não há interatividade
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza os pacotes
RUN apt-get update

# Necessário para instalações subsequentes.
RUN apt-get install -y apt-utils

# Instalação de Dependências para o psycopg.
RUN apt-get install -y python3-dev libpq-dev

# Setup nginx
RUN apt-get install -y nginx
COPY ./setup/nginx.conf /etc/nginx/sites-enabled/default
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Criação de Usuário
RUN adduser --group --system --no-create-home --disabled-login equibook

RUN mkdir /app
RUN chown equibook app
RUN chgrp equibook app

# Setando o usuário equibook na sessão atual
USER equibook:equibook


# Altera o diretório corrente para o diretório que contém o app
WORKDIR /app

# Criando ambiente virtual
RUN python -m venv .venv

# Copia os arquivos da aplicação para a imagem
COPY --chown=equibook:equibook ./equibook/ ./equibook
COPY --chown=equibook:equibook ./equibook/core/static/ /var/www/html/static/

COPY --chown=equibook:equibook .prod.env ./.env
COPY --chown=equibook:equibook manage.py requirements.txt ./setup/entrypoint.sh ./

ENV PATH="/app/.venv/bin:$PATH"

# Instalação de Dependências do projeto
RUN pip --cache-dir ./.cache --disable-pip-version-check install wheel
RUN pip --cache-dir ./.cache --disable-pip-version-check install -r ./requirements.txt

# Escutando requisições na porta 8000
EXPOSE 8000

ENTRYPOINT /app/entrypoint.sh
