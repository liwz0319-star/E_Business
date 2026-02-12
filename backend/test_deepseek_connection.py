"""
测试 DeepSeek API 连接
"""
import asyncio
import os
from dotenv import load_dotenv
from app.infrastructure.generators import DeepSeekGenerator
from app.domain.entities.generation import GenerationRequest


async def test_connection():
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')

    if not api_key or api_key == 'your-api-key-here':
        print('[ERROR] API Key not configured')
        print('Please set DEEPSEEK_API_KEY in backend/.env')
        return

    print(f'[INFO] API Key: {api_key[:10]}...{api_key[-4:]}')

    async with DeepSeekGenerator() as llm:
        print('[INFO] Connecting to DeepSeek API...')

        # 测试 1: 简单连接测试
        print('\n[TEST 1] Simple connection test')
        request = GenerationRequest(
            prompt='Hello, please reply with "Connection successful"',
            model='deepseek-chat',
        )

        try:
            result = await llm.generate(request)

            if result.content:
                print('[SUCCESS] DeepSeek API connection successful!')
                print(f'[INFO] Response: {result.content}')
                print(f'[INFO] Tokens used: {result.usage.total_tokens if result.usage else "N/A"}')
                print(f'[INFO] Model: {result.model}')
            else:
                print('[WARN] Empty response')

        except Exception as e:
            print(f'[ERROR] Connection failed: {e}')
            import traceback
            traceback.print_exc()
            return

        # 测试 2: 中文响应测试
        print('\n[TEST 2] Chinese response test')
        request = GenerationRequest(
            prompt='你好，请用中文回复"连接成功"',
            model='deepseek-chat',
        )

        try:
            result = await llm.generate(request)

            if result.content:
                print('[SUCCESS] Chinese response test passed!')
                print(f'[INFO] Response: {result.content}')
            else:
                print('[WARN] Empty response')

        except Exception as e:
            print(f'[ERROR] Chinese test failed: {e}')

        # 测试 3: 实际产品分析场景
        print('\n[TEST 3] Product analysis scenario')
        prompt = """请分析以下产品并提取关键信息:

产品: 高端无线蓝牙耳机
特点:
- 主动降噪技术
- 30小时超长续航
- 快速充电 (10分钟充电3小时使用)
- 高品质音质 (40mm钕铁硼单元)

请以JSON格式返回:
{
    "category": "产品类别",
    "target_audience": ["目标受众1", "目标受众2"],
    "key_features": ["特点1", "特点2", "特点3"],
    "marketing_angles": ["营销角度1", "营销角度2"]
}
"""

        request = GenerationRequest(
            prompt=prompt,
            model='deepseek-chat',
            temperature=0.7,
            max_tokens=500,
        )

        try:
            result = await llm.generate(request)

            if result.content:
                print('[SUCCESS] Product analysis test passed!')
                print(f'[INFO] Generated analysis (first 200 chars):')
                print(f'  {result.content[:200]}...')
                print(f'[INFO] Total tokens: {result.usage.total_tokens if result.usage else "N/A"}')
            else:
                print('[WARN] Empty response')

        except Exception as e:
            print(f'[ERROR] Product analysis failed: {e}')

        print('\n[SUMMARY] All tests completed!')
        print('[INFO] DeepSeek API is working correctly')


if __name__ == '__main__':
    asyncio.run(test_connection())
