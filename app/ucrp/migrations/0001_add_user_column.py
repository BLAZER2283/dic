from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # depends on auth app existing
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'ucrp_epgcalculation' AND column_name = 'user_id'
                ) THEN
                    ALTER TABLE ucrp_epgcalculation ADD COLUMN user_id integer;
                END IF;
            END$$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'ucrp_epgcalculation' AND column_name = 'user_id'
                ) THEN
                    ALTER TABLE ucrp_epgcalculation DROP COLUMN user_id;
                END IF;
            END$$;
            """,
        ),
    ]
