# video-transcoder
## Description
massento is a platform independent script to encode videos written in python. It uses ffmpeg to encode the videos.
As a main input parameter it takes a folder and walks through the folder structure, searching for video files which have not been encoded yet.
Optionally the input parameter can be a single file.

## Configuration
### Environment variables
 - MASSENTO_LOGLEVEL
 - MASSENTO_INPUT
 - MASSENTO_OUTPUT
 - MASSENTO_DELETE_SOURCE
 - MASSENTO_SCAN_DELAY
 - MASSENTO_CODECS

## Memo
Config variable evaluation precedence
 - command line argument
 - env. variable
 - config file
 - hardcoded

 Config file location precedence
 - command line
 - HOME/.massento/config.json
 - on POSIX: /etc/massento/config.json, on Win LOCALDATA/massento/config.json
 

