from django.db import migrations
from django.db.migrations.operations.special import SeparateDatabaseAndState

class Migration(migrations.Migration):

    dependencies = [
        ('binarycity', '0002_notificationclient_alter_client_client_code_and_more'),
    ]

    operations = [
        SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='''
                    DROP TABLE IF EXISTS "binarycity_contact_new";
                    CREATE TABLE "binarycity_contact_new" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "name" varchar(255) NOT NULL,
                        "surname" varchar(255) NOT NULL,
                        "email" varchar(254) NOT NULL UNIQUE,
                        "created_at" datetime NOT NULL,
                        "updated_at" datetime NOT NULL
                    );
                    INSERT INTO "binarycity_contact_new" 
                    SELECT id, name, surname, email, created_at, updated_at 
                    FROM "binarycity_contact";
                    DROP TABLE "binarycity_contact";
                    ALTER TABLE "binarycity_contact_new" RENAME TO "binarycity_contact";
                    ''',
                    reverse_sql='''
                    DROP TABLE IF EXISTS "binarycity_contact_new";
                    CREATE TABLE "binarycity_contact_new" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "name" varchar(255) NOT NULL,
                        "email" varchar(254) NOT NULL UNIQUE,
                        "created_at" datetime NOT NULL,
                        "updated_at" datetime NOT NULL,
                        "surname" varchar(255) NOT NULL
                    );
                    INSERT INTO "binarycity_contact_new" 
                    SELECT id, name, email, created_at, updated_at, surname 
                    FROM "binarycity_contact";
                    DROP TABLE "binarycity_contact";
                    ALTER TABLE "binarycity_contact_new" RENAME TO "binarycity_contact";
                    '''
                ),
            ],
            state_operations=[],
        ),
    ] 