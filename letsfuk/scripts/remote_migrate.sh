ssh root@euve258483.serverprofi24.net /bin/bash << EOF
    source ~/envs/letsfuk/bin/activate
        cd letsfuk
        git fetch
        git pull
        pip install -U -r requirements.txt
        python -m letsfuk --execute migrate
EOF
