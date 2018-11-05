# ###### Create unique target name from file name ###########################
FUNCTION(makeUniqueTarget target fileName)
   # STRING(MAKE_C_IDENTIFIER ${fileName} result)
   SET(result ${fileName})
   STRING(REGEX REPLACE "[/\\ ]" "-"  result ${result})
   STRING(REPLACE "ä" "ae" result ${result})
   STRING(REPLACE "ö" "oe" result ${result})
   STRING(REPLACE "ü" "ue" result ${result})
   STRING(REPLACE "ß" "ss" result ${result})
   STRING(REPLACE "Ä" "AE" result ${result})
   STRING(REPLACE "Ö" "OE" result ${result})
   STRING(REPLACE "Ü" "UE" result ${result})
   STRING(REPLACE "æ" "ae" result ${result})
   STRING(REPLACE "ø" "oe" result ${result})
   STRING(REPLACE "å" "aa" result ${result})
   STRING(REPLACE "Æ" "AE" result ${result})
   STRING(REPLACE "Ø" "OE" result ${result})
   STRING(REPLACE "Å" "AA" result ${result})
   STRING(REGEX REPLACE "[áàǎã]" "a" result ${result})
   STRING(REGEX REPLACE "[ÁÀǍÃ]" "A" result ${result})
   STRING(REGEX REPLACE "[éèê]"  "e" result ${result})
   STRING(REGEX REPLACE "[ÉÈÊ]"  "E" result ${result})
   STRING(REGEX REPLACE "[^a-zA-Z0-9\\.@_+-]" "_X_" result ${result})
   SET(${target} ${result} PARENT_SCOPE)
ENDFUNCTION()


#############################################################################
# GRAPHICS FILES
#############################################################################

# ====== Install graphics files =============================================
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


# ====== Create site images =================================================
FIND_PROGRAM(MAKE_CROPPED "${CMAKE_CURRENT_SOURCE_DIR}/../background/gimp-scripts/Resize-with-Cropping")
IF(NOT MAKE_CROPPED)
   MESSAGE(FATAL_ERROR "Resize-with-Cropping not found!")
ENDIF()

# ------ Parameters ---------------------------------------
SET(WIDTH_LARGE  1980)
SET(WIDTH_SMALL  512)
SET(ASPECT_RATIO "4:3")
SET(JPEG_QUALITY 92.5)
# ---------------------------------------------------------


FILE(GLOB siteImages "Sites/Original/*.jpeg")

FILE(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/Sites/Small")
FILE(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/Sites/Large")
FOREACH(siteImage ${siteImages})
   GET_FILENAME_COMPONENT(siteImageWithoutPath ${siteImage} NAME)
   SET(smallImage "${CMAKE_CURRENT_BINARY_DIR}/Sites/Small/${siteImageWithoutPath}")
   SET(largeImage "${CMAKE_CURRENT_BINARY_DIR}/Sites/Large/${siteImageWithoutPath}")
   makeUniqueTarget(generate_smallImage ${smallImage})
   makeUniqueTarget(generate_largeImage ${largeImage})

   ADD_CUSTOM_COMMAND(OUTPUT  ${smallImage}
                      COMMAND ${MAKE_CROPPED} ${siteImage} ${smallImage} ${ASPECT_RATIO} ${WIDTH_LARGE}
                      DEPENDS ${siteImage})
   ADD_CUSTOM_TARGET(${generate_smallImage} ALL DEPENDS ${smallImage})
   INSTALL(FILES ${smallImage} DESTINATION ${CMAKE_INSTALL_PREFIX}/var/www/Artwork/Sites/Small)

   ADD_CUSTOM_COMMAND(OUTPUT  ${largeImage}
                      COMMAND ${MAKE_CROPPED} ${siteImage} ${largeImage} ${ASPECT_RATIO} ${WIDTH_LARGE}
                      DEPENDS ${siteImage})
   ADD_CUSTOM_TARGET(${generate_largeImage} ALL DEPENDS ${largeImage})
   INSTALL(FILES ${largeImage} DESTINATION ${CMAKE_INSTALL_PREFIX}/var/www/Artwork/Sites/Large)
ENDFOREACH()
