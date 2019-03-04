# Run at 00:00 and 12:00, random start between 00:00 and 11:30 hours later.
0 0,12 * * *   hipercontracer   if [ -e /etc/nornet/hipercontracer-database-configuration ] ; then /usr/bin/Random-Sleep 0 41400 -quiet && flock -x -n /var/lock/nornet-trace-import.lock -c "/usr/bin/tracedataimporter /etc/nornet/hipercontracer-database-configuration >>/var/log/nornet-trace-import.log 2>&1" ; fi
