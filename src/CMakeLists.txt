#############################################################################
# PYTHON LIBRARIES
#############################################################################

# Help:
# https://bloerg.net/2012/11/10/cmake-and-distutils.html

# NOTE: setup.py must *not* be packaged, since it is automatically generated!
# It has to be added to CPACK_SOURCE_IGNORE_FILES (i.e. "setup.py$")!

SET(SETUP_PY_IN "${CMAKE_CURRENT_SOURCE_DIR}/setup.py.in")
SET(SETUP_PY    "${CMAKE_CURRENT_BINARY_DIR}/setup.py")
# SET(DEPS        "${CMAKE_CURRENT_SOURCE_DIR}/module/__init__.py")
SET(OUTPUT      "${CMAKE_CURRENT_BINARY_DIR}/build/timestamp")

CONFIGURE_FILE(${SETUP_PY_IN} ${SETUP_PY})

ADD_CUSTOM_COMMAND(OUTPUT ${OUTPUT}
                   COMMAND ${PYTHON_EXECUTABLE} ${SETUP_PY} build && touch ${OUTPUT})
ADD_CUSTOM_TARGET(target ALL DEPENDS ${OUTPUT})

INSTALL(CODE "EXECUTE_PROCESS(COMMAND ${PYTHON_EXECUTABLE} ${SETUP_PY} install ${PYTHON_SETUP_OPTS} --prefix=${PYTHON_LIBRARY_PREFIX})")


#############################################################################
# PROGRAMS
#############################################################################

INSTALL(PROGRAMS cls                          DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES cls.1                           DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Auto-Update-BootCD           DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Auto-Update-BootCD.1            DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Auto-Update-Keys             DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Auto-Update-Keys.1              DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Backup-All-VSystems          DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Backup-All-VSystems.1           DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Backup-VSystem               DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Backup-VSystem.1                DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Change-VSystem-CDImage       DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Change-VSystem-CDImage.1        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Check-Nodes                  DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Check-Nodes.1                   DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Check-Nodes-Loop             DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Check-Nodes-Loop.1              DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Check-Research-Node          DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Check-Research-Node.1           DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS check_site                   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES check_site.1                    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS check_tunnel                 DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES check_tunnel.1                  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Check-VSystem                DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Check-VSystem.1                 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Clear-SSH-Node-Key           DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Clear-SSH-Node-Key.1            DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Convert-HDD-Images           DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Convert-HDD-Images.1            DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Create-New-SSH-Node-Keys     DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Create-New-SSH-Node-Keys.1      DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Fingerprint-SSH-Node-Keys    DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Fingerprint-SSH-Node-Keys.1     DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Flush-Squid-Cache            DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Flush-Squid-Cache.1             DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-Nodes                    DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-Nodes.1                     DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-NorNet-Configuration     DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-NorNet-Configuration.1      DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-Sites                    DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-Sites.1                     DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-Slice-Nodes              DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-Slice-Nodes.1               DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-Slices                   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-Slices.1                    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Get-Users                    DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Get-Users.1                     DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Interface-Setup              DESTINATION ${CMAKE_INSTALL_SBINDIR})
INSTALL(FILES Interface-Setup.8               DESTINATION ${CMAKE_INSTALL_MANDIR}/man8)

INSTALL(PROGRAMS Make-FileSrv-Configuration   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-FileSrv-Configuration.1    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Make-Monitor-Configuration   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-Monitor-Configuration.1    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Make-Node-Configuration      DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-Node-Configuration.1       DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Make-Server-Configuration    DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-Server-Configuration.1     DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Make-Tunnelbox-Configuration DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-Tunnelbox-Configuration.1  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Make-VSystem-Template        DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Make-VSystem-Template.1         DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Node-Setup                   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Node-Setup.1                    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Probe-Endpoint-Setup         DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Probe-Endpoint-Setup.1          DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Probe-Interface-Setup        DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Probe-Interface-Setup.1         DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Random-Sleep                 DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Random-Sleep.1                  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Reset-Networking             DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Reset-Networking.1              DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Reset-VSystem                DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Reset-VSystem.1                 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Routing-Rule-Setup           DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Routing-Rule-Setup.1            DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Server-Setup                 DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Server-Setup.1                  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Server-Watchdog              DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Server-Watchdog.1               DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Set-OVF-Type                 DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Set-OVF-Type.1                  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Show-VSystems                DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Show-VSystems.1                 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Start-VSystem                DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Start-VSystem.1                 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Stop-VSystem                 DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Stop-VSystem.1                  DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS System-Backup                DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES System-Backup.1                 DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Test-NTP-Configuration       DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Test-NTP-Configuration.1        DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Tunnelbox-Bootstrap-Helper   DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Tunnelbox-Bootstrap-Helper.1    DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Tunnelbox-NAT-Helper         DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Tunnelbox-NAT-Helper.1          DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Tunnelbox-Setup              DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Tunnelbox-Setup.1               DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)

INSTALL(PROGRAMS Watchdog                     DESTINATION ${CMAKE_INSTALL_BINDIR})
INSTALL(FILES Watchdog.1                      DESTINATION ${CMAKE_INSTALL_MANDIR}/man1)


#############################################################################
# CONFIGURATION FILES
#############################################################################

INSTALL(PROGRAMS system-info.d/10-nornet DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/system-info.d)

INSTALL(PROGRAMS system-maintenance.d/10-nornet DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/system-maintenance.d)

INSTALL(FILES nornet-authorized_keys  DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/nornet)

INSTALL(FILES watchdog-config.example DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet-server)


#############################################################################
# EXAMPLES
#############################################################################

SET(nornet_api_configuration
   nornetapi-config.full
   nornetapi-config.simple
   nornetapi-constants
)

INSTALL(FILES ${nornet_api_configuration} DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet-api)


#############################################################################
# SOURCE DIRECTORIES
#############################################################################

ADD_SUBDIRECTORY(background)
ADD_SUBDIRECTORY(cron-apt)
ADD_SUBDIRECTORY(grub)
ADD_SUBDIRECTORY(pbuilder)
ADD_SUBDIRECTORY(vsystems)

ADD_SUBDIRECTORY(Artwork)
ADD_SUBDIRECTORY(Kontrollsenter)
ADD_SUBDIRECTORY(Monitor)
ADD_SUBDIRECTORY(WebServer)
ADD_SUBDIRECTORY(XDM)
