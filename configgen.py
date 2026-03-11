import json
import sys

if "-d" in sys.argv and len(sys.argv) - (sys.argv.index("-d") + 1) >= 1:
    spotify_dir = sys.argv[sys.argv.index("-d") + 1]
else:
    print("Missing required argument: -s. Type --help for more info.")
    quit()

config = {"spotify-save-location": spotify_dir}
with open(".config.json", "w") as f:
    f.write(json.dumps(config, ensure_ascii=False, indent=4))
