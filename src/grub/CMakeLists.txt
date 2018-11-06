#############################################################################
# BOOTLOADER CONFIGURATION FILES
#############################################################################

FILE(GLOB themeFiles  "[0-9][0-9]_*_theme")

INSTALL(FILES ${themeFiles} DESTINATION ${CMAKE_INSTALL_SYSCONFDIR}/grub.d)
INSTALL(FILES grub-defaults DESTINATION ${CMAKE_INSTALL_DATADIR}/nornet)
