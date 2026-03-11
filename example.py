import asyncio
from pathlib import Path
from kele_sdk import KeleClient


async def main():
    geometry_script_path = Path(__file__).parent / 'geometry_for_wo_tool_complex_2.py'

    if not geometry_script_path.exists():
        print(f'Error: {geometry_script_path} not found.')
        return

    async with KeleClient(base_url='http://210.45.70.163:12080') as client:
        print('=== 1. Health and Readiness Checks ===')
        health = await client.healthz()
        print(f'Health check: {health}')

        ready = await client.readyz()
        print(f'Readiness check: {ready}')

        print('\n=== 2. Upload Knowledge Bases (kbs) ===')
        kbs_result = await client.kbs(
            files=[
                ('config.yaml', b'timeout: 60'),
            ]
        )
        session_uuid = kbs_result['uuid']
        print(f'Files uploaded to session: {session_uuid}')

        print('\n=== 3. Run Inference (infer) ===')
        print(f"Sending inference request for '{geometry_script_path.name}'...")

        result = await client.infer(files=[geometry_script_path], entrypoint=geometry_script_path.name, uuid=session_uuid)

        print(f'Status: {result.status}')
        if result.status == 'ok':
            print(f'Exit Code: {result.exit_code}')
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                print('Stdout (last 5 lines):')
                for line in stdout_lines[-5:]:
                    print(f'  {line}')

            if result.engine_result:
                print('Engine Result received successfully.')

            if result.metric:
                print(f'Metrics: {result.metric.get("total_time", "N/A")}s')
        else:
            print(f'Error Detail: {result.detail}')
            if result.stderr:
                print(f'Stderr: {result.stderr}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Failed to connect to API: {e}')
        print('Make sure the KELE API service is running.')
