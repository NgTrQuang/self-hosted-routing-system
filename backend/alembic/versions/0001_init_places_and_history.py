"""init places and route_history tables

Revision ID: 0001
Revises: 
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "places",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("name_en", sa.Text, nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("province", sa.Text, nullable=True),
        sa.Column("district", sa.Text, nullable=True),
        sa.Column("type", sa.Text, nullable=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("source", sa.Text, nullable=False, server_default="manual"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("places_name_idx", "places", ["name"])
    op.create_index("places_province_idx", "places", ["province"])

    op.create_table(
        "route_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("origin_lat", sa.Float, nullable=False),
        sa.Column("origin_lng", sa.Float, nullable=False),
        sa.Column("dest_lat", sa.Float, nullable=False),
        sa.Column("dest_lng", sa.Float, nullable=False),
        sa.Column("origin_name", sa.Text, nullable=True),
        sa.Column("dest_name", sa.Text, nullable=True),
        sa.Column("distance_m", sa.Float, nullable=True),
        sa.Column("duration_s", sa.Float, nullable=True),
        sa.Column("waypoints", sa.JSON, nullable=True),
        sa.Column("mode", sa.Text, nullable=False, server_default="route"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            index=True,
        ),
    )
    op.create_index("route_history_created_idx", "route_history", ["created_at"])


def downgrade() -> None:
    op.drop_table("route_history")
    op.drop_table("places")
