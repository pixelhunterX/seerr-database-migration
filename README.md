# Migrate Overseerr settings and database to Jellyseerr

This script migrates the settings and database from Overseerr to Jellyseerr. It is intended for users who have been using Overseerr and want to switch to Jellyseerr without losing data. As the database structure of Overseerr and Jellyseerr are a bit different, it is unfortunately not possible to simply copy the database file from Overseerr to Jellyseerr. This script will migrate your settings, media, users and requests from Overseerr to the Jellyseerr.

1. Clone this repository or set up the the directory structure manually as shown below.
2. Install Jellyseerr. You don't need to configure it.
3. Stop Jellyseerr and Overseerr.
4. Copy your Overseerr and Jellyseerr `db` folders and `settings.json` files to `./overseerr` and `./jellyseerr` respectively. The structure should look like this:
```bash
.
├── database-migration.py
├── jellyseerr
│   ├── db
│   │   ├── db.sqlite3
│   │   ├── db.sqlite3-shm # May or may not exist.
│   │   └── db.sqlite3-wal # Please copy the -shm and -wal files if they exist.
│   └── settings.json
└── overseerr
    ├── db
    │   ├── db.sqlite3
    │   ├── db.sqlite3-shm # Same as above.
    │   └── db.sqlite3-wal #
    └── settings.json
```
4. Run the following command to migrate the database:
```bash
python3 database-migration.py
```
6. Copy the Jellyseerr `db.sqlite3` database file back to the Jellyseerr database directory. Delete `db.sqlite3-shm` and `db.sqlite3-wal` files if they exist. Also copy the `settings.json` file back to the config directory.
7. Start Jellyseerr and verify that everything is working as expected.

In case of any issues, there are copies of the original Overseerr and Jellyseerr database and settings files in the `./backup` directory.

