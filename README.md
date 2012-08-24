###STIG Browser Parser###
Instead of just pooping out a TSV, this will be used to create a dynamic web app.
The webapp will format things, and act as a checklist for the public to use.
Comments, tags, annotations, etc.  Social IA!

Coming soon!

* After downloading the STIG Archive ZIP File, unzip everything into a working dir:

```sh
mkdir xmldir
cd xmldir
find /path/to/stig/root/directory -name "*.zip" -print0 | xargs -0 -I zipfile unzip zipfile
```
* Run this again, because there are a few zipfiles inside those:

```sh
find ./ -name "*.zip" -print0 | xargs -0 -I zipfile unzip zipfile
```

* Import all the XML files into the database:

```sh
find ./ -name ".xml" -print0 | xargs -0 -I xccdf python stig-importer.py xccdf
```


The code will be open-source-ish, for folks who'd like to run it on 'offline' networks.

###License###
(c) 2010 Adam Crosby
