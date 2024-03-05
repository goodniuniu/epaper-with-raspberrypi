version: '3'

services:
  homeassistant:
    container_name: homeassistant
    image: "homeassistant/home-assistant"
    privileged: true
    network_mode: host
    restart: always
    healthcheck:
      test: ["CMD", "wget", "-q","--spider", "http://localhost:8123"]
      interval: 15s
      timeout: 10s
      retries: 3
      start_period: 90s
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "./config:/config"