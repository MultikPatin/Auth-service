export PYTHONPATH=$SRC_PATH
poetry run alembic upgrade head
cd "$APP_DIR" || exit
rm Dockerfile
