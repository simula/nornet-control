#############################################################################
# CONFIGURATION FILES
#############################################################################

FILE(GLOB NorNetMonitor_files "*.cfg")

INSTALL(FILES ${NorNetMonitor_files} DESTINATION ${CMAKE_INSTALL_FULL_SYSCONFDIR}/nornet)
