import asyncio
from pathlib import Path
from kele_sdk import KeleClient


async def main():
    relationship_script_path = Path(__file__).parent / 'relation.py'

    if not relationship_script_path.exists():
        print(f'Error: {relationship_script_path} not found.')
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
                ('README', '这个是一个上传文件的测试, KELE引擎并不是用他'.encode()),
            ]
        )
        session_uuid = kbs_result.uuid
        print(f'Files uploaded to session: {session_uuid}')

        print('\n=== 3. Run Inference (infer) ===')
        print(f"Sending inference request for '{relationship_script_path.name}'...")

        result = await client.infer(
            files=[relationship_script_path],
            entrypoint=relationship_script_path.name,
            uuid=session_uuid,
        )

        print(f'Status: {result.status}')
        if result.status == 'ok':
            print(f'Exit Code: {result.exit_code}')
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                print('Stdout (last 5 lines):')
                for line in stdout_lines[-5:]:
                    print(f'  {line}')
            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                print('Stderr (last 5 lines):')
                for line in stderr_lines[-5:]:
                    print(f'  {line}')
            if result.log:
                log_lines = result.log.strip().split('\n')
                print('Log (last 5 lines):')
                for line in log_lines[-5:]:
                    print(f'  {line}')

            if result.engine_result:
                print('Engine Result received successfully.')

            if result.metric:
                print('Metrics:')
                print(result.metric['meta'])
        else:
            print(f'Error Detail: {result.detail}')


if __name__ == '__main__':
    asyncio.run(main())


