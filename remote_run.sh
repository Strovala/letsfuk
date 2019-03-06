ssh root@euve258483.serverprofi24.net /bin/bash << EOF
    source ~/envs/letsfuk/bin/activate
    cd letsfuk
    git fetch
    git pull
    pip install -U -r requirements.txt
    export APP_SETTINGS="config.DevelopmentConfig"
    export DATABASE_URL="postgresql://letsfuk:root@localhost/letsfuk"
    FLASK_APP=app.py flask run -h 0.0.0.0 -p 5001
EOF
