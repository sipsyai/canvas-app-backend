"""Drop all RLS policies to allow migrations"""
import asyncio
import asyncpg

async def drop_all_rls_policies():
    """Drop all RLS policies in public schema"""
    # Supabase local connection
    url = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

    conn = await asyncpg.connect(url)

    try:
        # Get all policies
        policies = await conn.fetch("""
            SELECT tablename, policyname
            FROM pg_policies
            WHERE schemaname = 'public'
        """)

        print(f"Found {len(policies)} RLS policies:")
        for policy in policies:
            table = policy['tablename']
            name = policy['policyname']
            print(f"  - {table}.{name}")

        # Drop each policy
        for policy in policies:
            table = policy['tablename']
            name = policy['policyname']
            try:
                await conn.execute(f'DROP POLICY IF EXISTS "{name}" ON "{table}"')
                print(f"✓ Dropped {table}.{name}")
            except Exception as e:
                print(f"✗ Failed to drop {table}.{name}: {e}")

        # Disable RLS on all tables
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public' AND rowsecurity = true
        """)

        print(f"\nDisabling RLS on {len(tables)} tables:")
        for table_row in tables:
            table = table_row['tablename']
            try:
                await conn.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')
                print(f"✓ Disabled RLS on {table}")
            except Exception as e:
                print(f"✗ Failed to disable RLS on {table}: {e}")

        print("\n✅ All RLS policies and security disabled successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(drop_all_rls_policies())
