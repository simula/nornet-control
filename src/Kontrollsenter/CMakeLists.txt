#############################################################################
#### FILES                                                               ####
#############################################################################

FILE(GLOB Kontrollsenter_files "NorNet-*.css" "NorNet-*.js" "NorNet-*.php" "NorNet-*.html" "Forward-*.html")

INSTALL(FILES ${NorNetWebSrv_files}                           DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter)

INSTALL(FILES Clock/station-clock.svg                         DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/Clock)
INSTALL(FILES Clock/License.pdf                               DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/Clock)

INSTALL(FILES ol3-layerswitcher/src/ol3-layerswitcher.js      DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/ol3-layerswitcher/src)
INSTALL(FILES ol3-layerswitcher/src/ol3-layerswitcher.css     DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/ol3-layerswitcher/src)

INSTALL(FILES UnifrakturCook/FontLog.txt                      DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook)
INSTALL(FILES UnifrakturCook/OFL-FAQ.txt                      DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook)
INSTALL(FILES UnifrakturCook/OFL.txt                          DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook)
INSTALL(FILES UnifrakturCook/UnifrakturCook-Light.ttf         DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook)
INSTALL(FILES UnifrakturCook/UnifrakturCook.ttf               DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook)
INSTALL(FILES UnifrakturCook/sources/UnifrakturCook-Light.sfd DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook/sources)
INSTALL(FILES UnifrakturCook/sources/UnifrakturCook.sfd       DESTINATION ${CMAKE_INSTALL_LOCALSTATEDIR}/www/Kontrollsenter/UnifrakturCook/sources)
