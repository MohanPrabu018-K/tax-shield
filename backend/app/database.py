from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def get_database() -> AsyncIOMotorDatabase:
    return db.db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    await create_indexes()


async def close_mongo_connection():
    if db.client:
        db.client.close()


async def create_indexes():
    database = db.db
    await database.users.create_index("email", unique=True)
    await database.transactions.create_index([("user_id", 1), ("date", -1)])
    await database.transactions.create_index([("user_id", 1), ("transaction_type", 1)])
    await database.documents.create_index([("user_id", 1), ("financial_year", 1)])
    await database.obligations.create_index([("user_id", 1), ("status", 1)])
    await database.obligations.create_index([("user_id", 1), ("title", 1)])
    await database.deadlines.create_index([("user_id", 1), ("due_date", 1)])
    await database.deadlines.create_index([("user_id", 1), ("title", 1), ("due_date", 1)])
    await database.scenarios.create_index([("user_id", 1), ("created_at", -1)])
    await database.investments.create_index([("user_id", 1), ("created_at", -1)])
    await database.deductions.create_index([("user_id", 1), ("financial_year", 1)])
    await database.tax_payments.create_index([("user_id", 1), ("payment_date", -1)])
    await database.ais_records.create_index([("user_id", 1), ("financial_year", 1)])
    await database.form26as_records.create_index([("user_id", 1), ("financial_year", 1)])
    await database.chat_messages.create_index([("user_id", 1), ("created_at", -1)])
    # Phase 1 foundation collections.
    await database.audit_events.create_index([("user_id", 1), ("created_at", -1)])
    await database.audit_events.create_index([("action", 1), ("created_at", -1)])
    await database.tax_rules.create_index([("domain", 1), ("version", 1)], unique=True)
    await database.organizations.create_index([("name", 1)])
    await database.memberships.create_index([("organization_id", 1), ("user_id", 1)], unique=True)
    await database.notifications.create_index([("user_id", 1), ("created_at", -1)])
    # Phases 3-13 collections.
    await database.accounts.create_index([("user_id", 1), ("code", 1)], unique=True)
    await database.journals.create_index([("user_id", 1), ("date", -1)])
    await database.journals.create_index([("user_id", 1), ("idempotency_key", 1)],
                                         unique=True, sparse=True)
    await database.parties.create_index([("user_id", 1), ("kind", 1), ("name", 1)])
    await database.invoices.create_index([("user_id", 1), ("date", -1)])
    await database.invoices.create_index([("user_id", 1), ("number", 1)], unique=True)
    await database.counters.create_index([("user_id", 1), ("prefix", 1)], unique=True)
    await database.tds_records.create_index([("user_id", 1), ("date", -1)])
    await database.products.create_index([("user_id", 1), ("sku", 1)], unique=True)
    await database.stock_moves.create_index([("user_id", 1), ("product_id", 1)])
    await database.clients.create_index([("user_id", 1), ("name", 1)])
    await database.tasks.create_index([("user_id", 1), ("status", 1)])
    await database.doc_requests.create_index([("user_id", 1), ("status", 1)])
    await database.reviews.create_index([("user_id", 1), ("state", 1)])
    await database.doc_links.create_index([("user_id", 1), ("event", 1)])
    # Commercial collections.
    await database.subscriptions.create_index([("user_id", 1)], unique=True)
    await database.password_resets.create_index([("digest", 1)], unique=True)
    await database.consents.create_index([("user_id", 1), ("purpose", 1)], unique=True)
    await database.support_tickets.create_index([("user_id", 1), ("status", 1)])
    await database.incidents.create_index([("status", 1), ("created_at", -1)])