FROM postgres:16

RUN apt update -y && apt upgrade -y && apt install -y libpq-dev make git gcc postgresql-server-dev-16

RUN git clone https://github.com/keithf4/pg_partman \
    && cd pg_partman \
    && make install \
    && make NO_BGW=1 install
