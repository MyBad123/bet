FROM postgres:15
ENV POSTGRES_USER gena
ENV POSTGRES_PASSWORD 123456
ENV POSTGRES_DB bet
ENV PGDATA /var/lib/postgresql/data/pgdata
COPY scripts.sql /docker-entrypoint-initdb.d