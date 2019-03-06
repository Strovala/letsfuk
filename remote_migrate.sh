ssh root@euve258483.serverprofi24.net /bin/bash << EOF
    source ~/envs/letsfuk/bin/activate
    cd letsfuk
    git fetch
    git pull
    pip install -U -r requirements.txt
    export APP_SETTINGS="config.DevelopmentConfig"
    export DATABASE_URL="postgresql://letsfuk:root@localhost/letsfuk"
    python manage.py db upgrade
EOF
