# Use the official uv base image with Python 3.12 on Debian Bookworm slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Required for transferring stdout/stderr from uv to Docker logs
ARG APP_HOME=/app
ENV PYTHONUNBUFFERED=1

# Create a non-root user and ensure /app ownership
# RUN mkdir -p ${APP_HOME} \
#  && groupadd -r nonrootgroup -g 1000 \
#  && useradd -r -u 1000 -g nonrootgroup nonroot \
#  && chown nonroot:nonrootgroup ${APP_HOME} \
#  && chmod 777 ${APP_HOME}

# ENV XDG_CACHE_HOME=/app/.cache
# RUN mkdir -p /app/.cache && chown -R nonroot:nonrootgroup /app/.cache

# Set a working directory
WORKDIR ${APP_HOME}

# Copy the metadata files first to leverage layer caching for dependency installs
COPY pyproject.toml .python-version uv.lock ./

# Install project dependencies using uv (reads uv.lock / pyproject)
RUN uv sync

# Copy the rest of the project and keep file ownership for the non-root user
COPY . /app

# Expose the port the app runs on
EXPOSE 8011

# Switch to the non-root user
#USER nonroot

# Run the Shiny app with uv; entrypoint is `app.py`
CMD ["uv", "run", "shiny", "run", "app.py", "-h", "0.0.0.0", "-p", "8011"]
