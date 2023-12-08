#############################################################################
#### FILES                                                               ####
#############################################################################

FILE(GLOB NorNetWebSrv_files "*.config" "*.conf" "favicon.ico")

INSTALL(FILES ${NorNetWebSrv_files} DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet-websrv)


LIST(APPEND NorNetWebSrv_scripts
   get-pin256
   make-cipher-suites
   make-certificate
   sign-certificate
)

INSTALL(PROGRAMS ${NorNetWebSrv_scripts} DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet-websrv)
