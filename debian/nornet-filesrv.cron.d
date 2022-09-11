0,15,30,45 * * * *  root  test -x /etc/init.d/nornet-filesrv && /usr/bin/Random-Sleep 0 450 -quiet && service nornet-filesrv check-and-configure
11 11        * * *  root  cd /filesrv/sys && if [ -d .git ] ; then git add * ; git commit -a -m "Configuration update." ; git push && git gc ; fi
