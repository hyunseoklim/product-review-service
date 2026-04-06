from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ai_gateway", "0002_reviewembedding"),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE INDEX review_embedding_idx
            ON ai_gateway_reviewembedding
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS review_embedding_idx;
            """
        ),
    ]
