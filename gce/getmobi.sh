#/bin/sh

sudo timedatectl set-timezone Asia/Tokyo

METAURL=http://metadata.google.internal/computeMetadata/v1/instance/attributes/
HEADER="Metadata-Flavor: Google"
FILEDATE=`date "+%Y%m%d"`
EMAIL=`curl "${METAURL}email" -H "${HEADER}"`
PASS=`curl "${METAURL}pass" -H "${HEADER}"`

/opt/calibre/ebook-convert 日本経済新聞（朝刊・夕刊）.recipe /tmp/${FILEDATE}.mobi --dont-download-recipe --username=${EMAIL} --password=${PASS}

gsutil cp /tmp/${FILEDATE}.mobi gs://<BUCKET>/

rm /tmp/${FILEDATE}.mobi
