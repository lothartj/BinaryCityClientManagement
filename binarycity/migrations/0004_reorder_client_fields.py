from django.db import migrations
from django.db.migrations.operations.special import SeparateDatabaseAndState

class Migration(migrations.Migration):

    dependencies = [
        ('binarycity', '0003_reorder_contact_fields'),
    ]

    operations = [
        SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='''
                    DROP TABLE IF EXISTS "binarycity_client_new";
                    CREATE TABLE "binarycity_client_new" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "name" varchar(255) NOT NULL,
                        "client_code" varchar(6) NOT NULL UNIQUE,
                        "created_at" datetime NOT NULL,
                        "updated_at" datetime NOT NULL
                    );
                    INSERT INTO "binarycity_client_new" 
                    SELECT id, name, client_code, created_at, updated_at
                    FROM "binarycity_client";
                    DROP TABLE "binarycity_client";
                    ALTER TABLE "binarycity_client_new" RENAME TO "binarycity_client";
                    ''',
                    reverse_sql='''
                    DROP TABLE IF EXISTS "binarycity_client_new";
                    CREATE TABLE "binarycity_client_new" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "client_code" varchar(6) NOT NULL UNIQUE,
                        "name" varchar(255) NOT NULL,
                        "created_at" datetime NOT NULL,
                        "updated_at" datetime NOT NULL
                    );
                    INSERT INTO "binarycity_client_new" 
                    SELECT id, client_code, name, created_at, updated_at
                    FROM "binarycity_client";
                    DROP TABLE "binarycity_client";
                    ALTER TABLE "binarycity_client_new" RENAME TO "binarycity_client";
                    '''
                ),
            ],
            state_operations=[],
        ),
    ] 