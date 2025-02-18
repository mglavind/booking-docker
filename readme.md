# Booking App

Denne app er en simpel booking-applikation, der tillader brugere at reservere tidspunkter til forskellige tjenester. Applikationen består af en frontend bygget med React og en backend bygget med Django.

![Django Tests](https://github.com/mglavind/booking-docker/actions/workflows/django.yml/badge.svg)
![Node.js Tests](https://github.com/mglavind/booking-docker/actions/workflows/node.js.yml/badge.svg)


## Kom i gang med Docker

For at sætte applikationen i gang med Docker, følg disse trin:

1. **Klon repositoryet:**
    ```sh
    git clone <repository-url>
    cd booking-docker
    ```

2. **Byg Docker-billederne:**
    ```sh
    docker compose build
    ```

3. **Start containerne:**
    ```sh
    docker compose up
    ```

4. **Adgang til applikationen:**
    Åbn din browser og gå til `http://localhost:8000` for at få adgang til frontend
