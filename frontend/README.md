# Frontend

## Getting Started

First, install the dependencies:

```bash
npm i
```

Second, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

## Local Tunnel

```
npm install -g localtunnel
lt --port 3000
```

## Dockerfile - Building and running the docker image

```
#Build the docker image
docker build --no-cache -t frontend -f docker/development/Dockerfile .

#Run the docker image
docker run -it -p 3000:3000 --env-file .env frontend
```