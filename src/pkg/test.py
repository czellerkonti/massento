from classes import CodecTemplate

codecs = [] 
codecs.append(CodecTemplate("mp3","-c:v copy -c:a libmp3lame -q:a 5 -movflags +faststart","mp4"))
codecs.append(CodecTemplate("x264","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a copy -movflags +faststart","mp4"))
codecs.append(CodecTemplate("x264","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a copy -movflags +faststart","mp4"))
codecs.append(CodecTemplate("x265","-c:v libx265 -preset slow -crf 20 -c:a copy -movflags +faststart","mp4"))
codecs.append(CodecTemplate("x265_aac","-c:v libx265 -preset slow -crf 20 -c:a aac -ab 160k -movflags +faststart","mp4"))
codecs.append(CodecTemplate("x264_aac","-c:v libx264 -preset veryslow -crf 20 -tune film -c:a aac -ab 160k -movflags +faststart","mp4"))

codecs = {codec.name:codec for codec in codecs}

#  for name in [codec.name for codec in codecs]:
 #    print(name)

print(codecs['mp3'].options)
