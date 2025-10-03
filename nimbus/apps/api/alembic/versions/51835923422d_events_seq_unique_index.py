from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '51835923422d'
down_revision = '0001_init'
branch_labels = None
depends_on = None

def upgrade():
    # Create a partial unique index on (project_id, seq) when seq is NOT NULL
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE schemaname = 'public'
              AND indexname = 'ux_events_project_seq_notnull'
        ) THEN
            CREATE UNIQUE INDEX ux_events_project_seq_notnull
            ON events(project_id, seq)
            WHERE seq IS NOT NULL;
        END IF;
    END$$;
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS ux_events_project_seq_notnull;")
