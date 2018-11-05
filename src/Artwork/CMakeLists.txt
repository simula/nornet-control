#############################################################################
# GRAPHICS FILES
#############################################################################

SET(Artwork_subdirs
   Graphics/Backgrounds
   Graphics/Control
   Graphics/Flags
   Graphics/Icons
   Graphics/Markers
   Sites/Original
)

FOREACH(subdir ${Artwork_subdirs})
   FILE(GLOB files "${subdir}/*.png" "${subdir}/*.svg")
   INSTALL(FILES ${files} DESTINATION  ${CMAKE_INSTALL_PREFIX}/var/www/Artwork/${subdir})
ENDFOREACH()


FILE(GLOB siteImages "Sites/Original/*.jpeg")
FOREACH(siteImage ${siteImages})
 MESSAGE("xx")
ENDFOREACH()
