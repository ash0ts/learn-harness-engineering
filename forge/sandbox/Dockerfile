FROM node:22.19.0-bookworm@sha256:afff6d8c97964a438d2e6a9c96509367e45d8bf93f790ad561a1eaea926303d9
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 xvfb xauth libgtk-3-0 libnss3 libasound2 libxss1 libgbm1 \
    libatk-bridge2.0-0 libdrm2 libxkbcommon0 ripgrep \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/app
COPY package.json package-lock.json ./
RUN npm ci && npm cache clean --force
RUN mkdir -p /workspace/task && chown -R node:node /workspace /opt/app
ENV PATH="/opt/app/node_modules/.bin:${PATH}"
WORKDIR /workspace/task
USER node
CMD ["sleep", "infinity"]
