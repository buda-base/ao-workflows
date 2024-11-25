#!/usr/bin/env bash
# Shorthand to control airflow
#
# airflow short control panel. Runs airflow locally in ~/airflow.
# Requires you to install airflow in ~/airflow (which is the default for pip install.
# You should be familiar with https://airflow.apache.org/docs/apache-airflow/2.8.4/start.html
# especially https://airflow.apache.org/docs/apache-airflow/2.8.4/installation/index.html
#

USAGE="${0} -[ [ w[ebserver]| s[cheduler]] [ u[p]| d[own]]  ] | r[eset] | a[dmin] admin_username admin_password admin_email"
PORT=8090 # Get out of way of other things. Docker uses 8089, so you can test in parallel

while getopts ":wsudriha" opt; do
    case ${opt} in
	w)
	    mode="webserver"
	    ;;
	s)
	    mode="scheduler"
	    ;;
	u)
	    action="up"
	    ;;
	d)
	    action="down"
	    ;;
	r)
	    # reset the db
	    mode="reset"
	    ;;
	a)
	    # Create the admin user
	    mode="admin"
	    ;;
	\?)
	    echo "Invalid option: -${OPTARG}" >&2
	    echo $USAGE
	    exit 1
	    ;;
	\h)
	    echo $USAGE
	    exit 0
	    ;;
	:)
	    echo "Option -${OPTARG} requires an argument." >&2
	    echo $USAGE
	    exit 1
	    ;;
    esac
done

shift $((OPTIND -1))

_=${mode?$USAGE}

if [[ $mode == w* ]] ; then
    if [[ $action  == u* ]] ;then
        airflow webserver -D --port $PORT -l ~/airflow/log/webserver.log
    elif [[ $action  == d* ]] ;then
	eval pkill -TERM "airflow webserver"
    else
	echo $USAGE
    fi
elif [[ $mode == s* ]] ; then
    if [[ $action  == u* ]] ;then
	airflow scheduler -D  -l ~/airflow/log/scheduler.log
    elif [[ $action  == d* ]] ;then
	eval pkill -TERM "airflow scheduler"
    else
	echo $USAGE
    fi
elif [[ $mode == r* ]] ; then
    airflow db reset --yes
elif [[ $mode == i* ]] ; then
    airflow db init
elif [[ $mode == a* ]] ; then
    af_email=${3?$USAGE}
    af_user=$1
    af_pass=$2
    airflow users create --username $af_user --password $af_pass --firstname Anonymous --lastname Admin --role Admin --email $af_email
fi
