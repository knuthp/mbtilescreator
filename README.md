# mbtilescreator
A Web application to create MBTiles files from map data.



## Dev
Pre-requisites:
- uv
- tippecanoe

```bash
sudo apt-get install build-essential libsqlite3-dev zlib1g-dev
git clone https://github.com/felt/tippecanoe.git
cd tippecanoe
make
sudo make install
```

To run the application in development mode, use the following command:

```bash
uv run streamlit run src/mbtilescreator/app.py
```
[app](http://localhost:8501)