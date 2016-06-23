import os

import sqlalchemy

from luizalabs.challenge import models


metadata = models.sqlbase.Base.metadata
engine = sqlalchemy.create_engine(os.environ["DATABASE_URI"])

print "Deleting tables (if they exist)..."
for table in reversed(metadata.sorted_tables):
    engine.execute("DROP TABLE IF EXISTS {}".format(table))

print "Creating database tables..."
metadata.create_all(engine)

print "You're all set!"
