FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Rasmni kerakli joyga nusxalash (Bot/handlers/1.jpg)
RUN mkdir -p /app/Bot/handlers
CMD ["bash"]
