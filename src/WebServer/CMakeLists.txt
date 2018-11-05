#############################################################################
# CONFIGURATION FILES
#############################################################################

FILE(GLOB NorNetWebSrv_files "*.config" "*.conf" "favicon.ico" "get-pin256" "make-cipher-suites" "make-certificate" "sign-certificate")

INSTALL(FILES ${NorNetWebSrv_files} DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet-websrv)
