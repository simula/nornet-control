# Watchdog and Server-Watchdog calls every 4 minutes
0,4,8,12,16,20,24,28,32,36,40,44,48,52,56 * * * *   root   /usr/bin/Watchdog /etc/nornet/watchdog-config >>/var/log/nornet-watchdog.log 2>&1 ; /usr/bin/Server-Watchdog >>/var/log/nornet-watchdog.log 2>&1
# Boot-CD update check between 22:00 and 6:00
0 22 * * *                                          root   /usr/bin/Auto-Update-BootCD 28800 >>/var/log/nornet-auto-update-bootcd.log 2>&1
