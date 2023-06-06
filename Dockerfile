FROM python:3.11 as python
ENV PYTHONUNBUFFERED=true
WORKDIR /app

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN pip3 install poetry
COPY . ./
RUN poetry install --no-interaction --no-ansi --no-dev

FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app
CMD ["python3", "app.py"]