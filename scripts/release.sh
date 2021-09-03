#!/usr/bin/env bash
#=======================================================================
#
#          FILE: release.sh
#
#         USAGE:  To be called upon deployment
#
#   DESCRIPTION:  Release script for app deployment
#
#        AUTHOR:  Stephen Whitlock (jshwi), stephen@jshwisolutions.com
#       CREATED:  22/09/21 15:59:44
#      REVISION:  0.1.0
#=======================================================================
set -o errexit
set -o nounset

flask db upgrade
