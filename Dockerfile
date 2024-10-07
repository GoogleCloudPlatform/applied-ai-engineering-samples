FROM python:3-slim as mkdocs

# Copy the entire project
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Make the bash script executable
RUN chmod +x mkdocs.sh

# Copy assets to docs folder
RUN mkdir -p docs/assets && cp -r assets/* docs/assets/

# Run the bash script to build the site
RUN ./mkdocs.sh build

FROM caddy:alpine
COPY --from=mkdocs ./site/ /usr/share/caddy/