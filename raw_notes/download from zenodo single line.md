---
raw_tags:
  - url
  - name
  - curl
  - links
  - json
  - key
  - dwnload
  - ifs
word_count: 79
char_count: 466
processed: false
---

curl https://zenodo.org/api/records/10229555 | jq -j '.files[] | "\(.key);\(.links[])\n"' | while IFS=";" read -r name url; do  wget -O $name $url; done

curl <your file link> : get the json
jq -j '.files[] | "\(.key);\(.links[])\n"' : parse the json to get the name and dwnload url of the file and 
while ... loop through all