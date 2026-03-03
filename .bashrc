# If we're on prod, make the terminal red
if [ "$DEPLOY_ENVIRONMENT" == "prod" ]; then 
    export PS1="\[\e[31m\]\u@\h:\w\$ \[\e[0m\]"
fi

alias djm="uv run manage.py"
