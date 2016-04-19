22 * * * *   root   if [ -e /etc/nornet/hipercontracer-database-configuration ] ; then /usr/bin/Random-Sleep 0 3200 -quiet && flock -x -n /var/lock/nornet-trace-import.lock -c "/usr/bin/tracedataimporter /etc/nornet/hipercontracer-database-configuration >>/var/log/nornet-trace-import.log 2>&1" ; fi
01 * * * *   root   service nornet-trace-service start >/dev/null 2>&1
