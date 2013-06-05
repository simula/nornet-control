# Automatic SSH key update
1,16,36,46 * * * *   root  /usr/bin/Auto-Update-Keys >/var/log/nornet-auto-update-keys 2>&1
# Daily backup between 2:00 and 5:00
0 2 * * *            root  if [ -d /nfs/node ] ; then mkdir -p /nfs/node/backup && System-Backup /nfs/node/backup daily  7 10800 >>/var/log/nornet-backup.log 2>&1 ; fi
# Weekly backup on Sunday between 5:00 and 7:00
0 5 * * 0            root  if [ -d /nfs/node ] ; then mkdir -p /nfs/node/backup && System-Backup /nfs/node/backup weekly 7 10800 >>/var/log/nornet-backup.log 2>&1 ; fi
# Monthly backup on first day of month between 23:00 and 2:00
0 23 1 * *           root  if [ -d /nfs/node ] ; then mkdir -p /nfs/node/backup && System-Backup /nfs/node/backup monthly 7 10800 >>/var/log/nornet-backup.log 2>&1 ; fi
