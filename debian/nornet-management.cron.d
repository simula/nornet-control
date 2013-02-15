0 2 * * *  root  if [ -d /nfs/node ] ; then mkdir -p /nfs/node/backup && System-Backup /nfs/node/backup daily 7 10800 >>/var/log/nornet-backup.log 2>&1 ; fi
