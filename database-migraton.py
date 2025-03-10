import sqlite3
import json
import shutil
import os

overseerr_config_path = './overseerr'
jellyseerr_config_path = './jellyseerr'

overseerr_db_path = os.path.join(overseerr_config_path, 'db', 'db.sqlite3')
jellyseerr_db_path = os.path.join(jellyseerr_config_path, 'db', 'db.sqlite3')

overseerr_json = os.path.join(overseerr_config_path, 'settings.json')
jellyseerr_json = os.path.join(jellyseerr_config_path, 'settings.json')

tables = ['user', 'media', 'media_request', 'season', 'season_request', 'issue', 'issue_comment', 'user_push_subscription', 'user_settings']

def backup_configs():
    backup_folder = './backup'
    os.makedirs(backup_folder, exist_ok=True)
    
    overseerr_backup_path = os.path.join(backup_folder, 'overseerr_backup')
    jellyseerr_backup_path = os.path.join(backup_folder, 'jellyseerr_backup')
    
    if os.path.exists(overseerr_config_path):
        shutil.copytree(overseerr_config_path, overseerr_backup_path, dirs_exist_ok=True)
    
    if os.path.exists(jellyseerr_config_path):
        shutil.copytree(jellyseerr_config_path, jellyseerr_backup_path, dirs_exist_ok=True)
    print("Backup complete.")

backup_configs()    

# Migrate settings from Overseerr to Jellyseerr.
def recursive_merge(source, dest, exclude_keys=None):
    """
    Recursively update values in dest with those from source if the key exists in dest.
    For nested dictionaries, subkeys from source are added/updated in dest.
    """
    if exclude_keys is None:
        exclude_keys = []

    for key, value in source.items():
        if key in exclude_keys:
            continue
        if key in dest:
            if isinstance(value, dict) and isinstance(dest[key], dict):
                dest[key] = recursive_merge(value, dest[key], exclude_keys)
            else:
                dest[key] = value
        else:
            dest[key] = value
    return dest
with open(overseerr_json, 'r', encoding='utf-8') as overseerr_file:
    overseerr_settings = json.load(overseerr_file)

with open(jellyseerr_json, 'r', encoding='utf-8') as jellyseerr_file:
    jellyseerr_settings = json.load(jellyseerr_file)

exclude_keys = ['applicationTitle', 'applicationUrl']

updated_settings = recursive_merge(overseerr_settings, jellyseerr_settings, exclude_keys)

# Set Jellyseerr media server type to Plex.
updated_settings['main']['mediaServerType'] = 1

with open(jellyseerr_json, 'w', encoding='utf-8') as jellyseerr_file:
    json.dump(updated_settings, jellyseerr_file, indent=2)

print("Settings migration complete.")

# Migrate tables from Overseerr to Jellyseerr.
with sqlite3.connect(overseerr_db_path) as src_conn, sqlite3.connect(jellyseerr_db_path) as dst_conn:
    src_cursor = src_conn.cursor()
    dst_cursor = dst_conn.cursor()
    
    dst_cursor.execute('PRAGMA foreign_keys = OFF')
    
    for table in tables:
        print(f'Migrating table: {table}')
        
        dst_cursor.execute(f'DELETE FROM {table}')
        dst_conn.commit()

        src_cursor.execute(f'SELECT * FROM {table}')
        rows = src_cursor.fetchall()
        
        if not rows:
            print(f'No data in table: {table}')
            continue

        column_names = [description[0] for description in src_cursor.description]
        
        if table == 'user_settings':
            # Handle column mismatches for user_settings
            dst_cursor.execute("PRAGMA table_info(user_settings)")
            dest_cols_info = dst_cursor.fetchall()
            dest_columns = [info[1] for info in dest_cols_info]
            common_columns = [col for col in dest_columns if col in column_names]
            placeholders = ', '.join(['?'] * len(common_columns))
            columns_list = ', '.join(common_columns)
            new_rows = []
            for row in rows:
                row_dict = dict(zip(column_names, row))
                new_row = tuple(row_dict[col] for col in common_columns)
                new_rows.append(new_row)
            insert_query = f'INSERT INTO {table} ({columns_list}) VALUES ({placeholders})'
            dst_cursor.executemany(insert_query, new_rows)
            dst_conn.commit()
            print(f'Migrated {len(new_rows)} data records in table {table}.')
        else:
            placeholders = ', '.join(['?'] * len(column_names))
            columns = ', '.join(column_names)
            insert_query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            dst_cursor.executemany(insert_query, rows)
            dst_conn.commit()
            print(f'Migrated {len(rows)} data records in table {table}.')

    dst_cursor.execute('PRAGMA foreign_keys = ON')

print('Database migration complete.')