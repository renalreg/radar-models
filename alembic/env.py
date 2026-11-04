from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from sqlmodel import SQLModel
import radar_models.radar3  # noqa: F401 — registers the table models
from radar_models.radar3 import Group  # adjust if Group lives elsewhere

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _include_object_factory():
    """Optionally restrict autogenerate to tables in one group.

    Usage:
        alembic revision --autogenerate -m "lookup tables" -x group=lookup

    The group is read from each table's __table_args__ info dict:
        __table_args__ = {"info": {"group": Group.LOOKUP}}

    With no -x group=..., autogenerate behaves normally.
    """
    x_args = context.get_x_argument(as_dictionary=True)
    group_arg = x_args.get("group")
    if not group_arg:
        return None

    try:
        wanted = Group[group_arg.upper()]
    except KeyError:
        valid = ", ".join(g.name.lower() for g in Group)
        raise SystemExit(f"Unknown group {group_arg!r}. Valid groups: {valid}")

    # Resolve names from the models: tables reflected from the database
    # don't carry the info dict, so filtering is done by table name.
    selected = {
        t.name
        for t in target_metadata.tables.values()
        if t.info.get("group") == wanted
    }
    if not selected:
        raise SystemExit(f"No tables found in group {wanted.name}")

    def include_object(obj, name, type_, reflected, compare_to):
        if type_ == "table":
            return name in selected
        # columns, indexes, constraints, FKs: keep only if their table is selected
        table = getattr(obj, "table", None)
        return table is None or table.name in selected

    return include_object


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=_include_object_factory(),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=_include_object_factory(),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()